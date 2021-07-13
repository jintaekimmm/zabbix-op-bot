import ipaddress
from datetime import datetime, timedelta

import requests
from pyzabbix import ZabbixAPI
from requests.auth import HTTPBasicAuth

from config import config


class ZabbixOp(object):
    def __init__(self):
        self.zbx_name = [key for key in config.ZABBIX_INFO.keys()]
        self.severity = config.zabbix_min_severity
        self.limit = config.zabbix_issue_limit
        self.file_dir = config.FILE_DIR

    @staticmethod
    def _is_ipaddress(host):
        try:
            ip_addr = ipaddress.ip_address(host)
        except ValueError:
            return False

        return True

    @staticmethod
    def _is_number(host):
        try:
            float(host)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(host)
            return True
        except (TypeError, ValueError):
            pass

        return False

    def _check_host_type(self, host):
        if self._is_ipaddress(host):
            return 'ip'
        elif self._is_number(host):
            return 'hostid'
        else:
            return 'host'

    @staticmethod
    def _login_by_zbx_name(zbx_name):
        zbx_info = config.ZABBIX_INFO[zbx_name]
        user_info = {
            'USER': zbx_info['USER'],
            'PASSWORD': zbx_info['PASSWORD'],
            'URL': zbx_info['URL']
        }
        return user_info

    def _login(self, zbx_name):
        zbx_info = self._login_by_zbx_name(zbx_name)
        zapi = ZabbixAPI(url=zbx_info['URL'], user=zbx_info['USER'], password=zbx_info['PASSWORD'])

        return zapi

    def _web_login(self, zbx_name):
        zbx_info = self._login_by_zbx_name(zbx_name)
        proxies = {}
        data = {'name': zbx_info['USER'], 'password': zbx_info['PASSWORD'], 'enter': 'Sign in'}
        login = requests.post('{}/'.format(zbx_info['URL']), data=data, proxies=proxies, verify=False,
                              auth=HTTPBasicAuth(zbx_info['USER'], zbx_info['PASSWORD']))
        return login.cookies

    @staticmethod
    def _graph_url(zbx_name):
        zbx_info = config.ZABBIX_INFO[zbx_name]
        urls = '{}/chart2.php'.format(zbx_info['URL'])

        return urls

    @staticmethod
    def _is_status(status):
        try:
            status = int(status)
        except ValueError:
            pass

        if status == 0:
            return 'Monitored'
        elif status == 1:
            return 'Not monitored'
        else:
            return 'Unkown monitored status'

    def host_info(self, zbx_name, host):
        host_type = self._check_host_type(host)
        zapi = self._login(zbx_name)

        if host_type == 'ip':
            res = self._get_host_by_ip(zapi, host)

        elif host_type == 'hostid':
            res = self._get_host_by_hostid(zapi, host)
        else:
            res = self._get_host_by_hostname(zapi, host)

        return res

    def search_issue(self, zbx_name, severity):
        zapi = self._login(zbx_name)

        try:
            issues = zapi.trigger.get(limit=self.limit, filter={'value': 1}, selectHosts=['host'],
                                      sortfield='lastchange', sortorder='DESC', output='extend', monitored=True,
                                      active=True, skipDependent=True, only_true=True, expandDescription=True,
                                      min_severity=severity, expandData='extend', selectItems=['lastvalue'])
        except Exception:
            raise ConnectionError('Zabbix API call failed. please check your network or access information')
        else:
            return issues

    def change_monitor_status(self, zbx_name, status, host_info):
        zapi = self._login(zbx_name)
        try:
            res = zapi.host.update(hostid=host_info['hostid'], status=status)
            res['status'] = status
        except Exception:
            raise ConnectionError('Zabbix API call failed. please check your network or access information')

        return res

    def host_monitor_status(self, zbx_name, host=None):
        zapi = self._login(zbx_name)

        host = self.host_info(zbx_name, host)
        return int(host['status'])

    def host_graph(self, zbx_name, host_info, graph_name=None):
        zapi = self._login(zbx_name)
        try:
            if graph_name:
                res = zapi.graph.get(output='extend', hostids=host_info['hostid'], filter={'name': graph_name})
            else:
                res = zapi.graph.get(output='extend', hostids=host_info['hostid'])
        except Exception:
            raise ConnectionError('Zabbix API call failed. please check your network or access information')

        return res

    def _get_host_list(self, zapi, zbx_name, monitored):
        zapi = self._login(zbx_name)
        if monitored:
            try:
                monitor_lists = zapi.host.get(output='extend', filter={'status': 0})
            except Exception:
                raise ConnectionError('Zabbix API call failed. please check your network or access information')
            else:
                return {i['host']: i['hostid'] for i in monitor_lists}
        else:
            try:
                not_monitor_lists = zapi.host.get(output='extend', filter={'status': 1})
            except Exception:
                raise ConnectionError('Zabbix API call failed. please check your network or access information')
            else:
                return {i['host']: i['hostid'] for i in not_monitor_lists}

    def host_list(self, zbx_name, monitored, all_list=False):
        zapi = self._login(zbx_name)
        if all_list and monitored:
            try:
                all_hosts = zapi.host.get(output='extend')
            except Exception:
                raise ConnectionError('Zabbix API call failed. please check your network or access information')
            else:
                res = {i['host']: i['hostid'] for i in all_hosts}
        elif not all_list and monitored:
            res = self._get_host_list(zapi, zbx_name, monitored=True)
        elif not all_list and not monitored:
            res = self._get_host_list(zapi, zbx_name, monitored=False)
        else:
            res = None

        return res

    @staticmethod
    def _get_host_by_ip(zapi, ip):
        try:
            ips = zapi.hostinterface.get(output=['ip', 'hostid'], filter={'ip': str(ip)})
        except Exception:
            raise ConnectionError('Zabbix API call failed. please check your network or access information')

        else:
            for i in ips:
                if str(ip) == i['ip']:
                    try:
                        hosts_obj = zapi.host.get(output=['host', 'status'], filter={'hostid': str(i['hostid'])})
                    except Exception:
                        raise ConnectionError('Zabbix API call failed. please check your network or access information')
                    else:
                        for j in hosts_obj:
                            return {
                                'hostid': j['hostid'],
                                'status': j['status'],
                                'host': j['host'],
                                'ip': ip
                            }

            return None

    def _get_host_by_hostname(self, zapi, host):
        try:
            hosts = zapi.host.get(output=['host', 'status'], fileter={'host': str(host)})
        except Exception:
            raise ConnectionError('Zabbix API call failed. please check your network or access information')
        else:
            for i in hosts:
                if host.lower() == i['host'].lower():
                    return {
                        'hostid': i['hostid'],
                        'status': int(i['status']),
                        'host': host,
                        'ip': self._get_ip_by_hostid(zapi, i['hostid'])
                    }

            return None

    def _get_host_by_hostid(self, zapi, hostid):
        try:
            hosts = zapi.host.get(output=['host', 'status'], filter={'hostid': str(hostid)})
        except Exception:
            raise ConnectionError('Zabbix API call failed. please check your network or access information')
        else:
            for i in hosts:
                if str(hostid) == i['hostid']:
                    return {
                        'hostid': str(hostid),
                        'status': int(i['status']),
                        'host': i['host'],
                        'ip': self._get_ip_by_hostid(zapi, hostid)
                    }

            return None

    @staticmethod
    def _get_ip_by_hostid(zapi, hostid):
        try:
            ips = zapi.hostinterface.get(output=['ip'], filter={'hostid': str(hostid)})
        except Exception:
            raise ConnectionError('Zabbix API call failed. please check your network or access information')
        else:
            for i in ips:
                return str(i['ip'])

            return None

    @staticmethod
    def _x_hour_ago():
        current = datetime.now()
        hour_ago = config.zabbix_graph_stime
        stime = current - timedelta(hours=hour_ago)

        return stime.strftime('%Y%m%d%H%M%S')

    @staticmethod
    def _x_hour_ago_to_time():
        return config.zabbix_graph_stime

    def graph_url(self, zbx_name):
        return self._graph_url(zbx_name)

    def graph_image_download(self, zbx_name, graph_url):
        img = '{}/tmp_make_graph.png'.format(self.file_dir)
        cookie = self._web_login(zbx_name)
        zbx_info = self._login_by_zbx_name(zbx_name)
        res = requests.get(graph_url, cookies=cookie, verify=False, auth=HTTPBasicAuth(zbx_info['USER'],
                                                                                       zbx_info['PASSWORD']))
        res_img = res.content
        with open(img, 'wb') as f:
            f.write(res_img)

        return img
