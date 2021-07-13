import csv
from datetime import datetime
import requests
from pyzabbix import ZabbixAPIException

from config import config
from zabbix_op.zabbixop import ZabbixOp


def zbx_get_issue(bot, chat_id, severity, zbx_names=None, polling=False):
    zbx_op = ZabbixOp()
    if zbx_names:
        zbx_name_list = zbx_names.split()
    else:
        zbx_name_list = zbx_op.zbx_name

    try:
        severity_number = config.zabbix_severity[severity]
    except KeyError:
        severity_number = zbx_op.severity

    # Zbx_name 별로 issue 를 가져와서 개별로 메시지 전송
    for zbx_name in zbx_name_list:
        issues = zbx_op.search_issue(zbx_name, severity_number)
        if issues:
            for issue in issues:
                lastchange_epochtime = int(issue['lastchange'])
                lastchange = datetime.fromtimestamp(lastchange_epochtime).strftime('%Y-%m-%d %H:%M:%S')
                host_info = zbx_op.host_info(zbx_name, issue['hosts'][0]['host'])

                if len(issue['items']) == 1:
                    lastvalue = issue['items'][0]['lastvalue']
                else:
                    lastvalue = 'value parse failed.'

                text = '[{}]\nHost: {}({})\nIssue: {}\nLastValue: {}\nLastChange: {}'\
                    .format(zbx_name, host_info['host'], host_info['ip'], issue['description'], lastvalue, lastchange)

                bot.send_message(chat_id, text=text)

        # polling 중이지 않고 issue 가 없는 경우
        elif not polling and not issues:
            bot.send_message(chat_id,
                             text='The requested trigger severity \'{}\' issue does not exist.'.format(severity))


def zbx_monitor_list(bot, chat_id, zbx_name, list_type):
    zbx_op = ZabbixOp()

    if list_type.lower() == 'monitored list':
        res = zbx_op.host_list(zbx_name, monitored=True)
    elif list_type.lower() == 'not monitored list':
        res = zbx_op.host_list(zbx_name, monitored=False)
    else:
        res = zbx_op.host_list(zbx_name, monitored=True, all_list=True)

    text = []
    inner_text = ''
    for i, v in enumerate(sorted(res), 1):
        host_info = zbx_op.host_info(zbx_name, res[v])
        host = '{}({})'.format(host_info['host'], host_info['ip'])
        inner_text += '{}\n'.format(host)
        if i % 30 == 0:
            text.append(inner_text)
            inner_text = ''

    text.append(inner_text)
    return text


def zbx_host_monitor_status(bot, chat_id, zbx_name, host):
    zbx_op = ZabbixOp()
    try:
        res = zbx_op.host_monitor_status(zbx_name, host)
    except ZabbixAPIException as e:
        bot.send_message(chat_id, text='An error has occurred.\n{}'.format(repr(e)))
    except Exception as e:
        bot.send_message(chat_id, text='An error has occurred.\nZabbix api call failed or host does not exist')
    else:
        if res == 0:
            bot.send_message(chat_id, text='Host({}) is currently being monitored'.format(host))
        elif res == 1:
            bot.send_message(chat_id, text='Host({}) is not currently monitoring'.format(host))
        else:
            bot.send_message(chat_id, text='Host({}) not fonud'.format(host))


def zbx_host_change_status(bot, chat_id, zbx_name, host, action):
    zbx_op = ZabbixOp()
    if action == 'enable':
        status = 0
    elif action == 'disable':
        status = 1
    else:
        status = None

    host_info = zbx_op.host_info(zbx_name, host)
    if host_info:
        if host_info['status'] == status:
            bot.send_message(chat_id, text='The current monitoring status has requested the same value.\n'
                                           'Request is ignored.')
            return True

        res = zbx_op.change_monitor_status(zbx_name, status, host_info)
        if isinstance(res, dict):
            if res['status'] == 0:
                text = '[{}]\nHost: {}\nAction: Zabbix Enable Monitor'.format(zbx_name, host)
                bot.send_message(chat_id, text=text)
                return True
            elif res['status'] == 1:
                text = '[{}]\nHost: {}\nAction: Zabbix Disable Monitor'.format(zbx_name, host)
                bot.send_message(chat_id, text=text)
                return True

    else:
        bot.send_message(chat_id, text='{} does not exist in {}'.format(host, zbx_name))
        return False


def _zbx_host_graph_list(zbx_name, host):
    zbx_op = ZabbixOp()
    host_info = zbx_op.host_info(zbx_name, host)
    if host:
        try:
            graph_list = zbx_op.host_graph(zbx_name, host_info)
        except ZabbixAPIException as e:
            return {
                'error': 'An error has occurred.\n{}'.format(repr(e))
            }
        else:
            res = {}
            for i, v in enumerate(graph_list):
                res[str(i)] = v['name']

            return res
    else:
        return {}


def zbx_host_graph_list(bot, chat_id, zbx_name, host, graph_list: dict):
    if 'error' in graph_list:
        bot.send_message(chat_id, text=graph_list['error'])
        return False

    if not graph_list:
        bot.send_message(chat_id, text='{} does not exist in {}'.format(host, zbx_name))
        return False

    text = ""
    for k, v in graph_list.items():
        text += '{}. {}\n'.format(k, v)

    bot.send_message(chat_id, text=text)
    return True


def zbx_host_graph_resource(bot, chat_id, zbx_name, host, graph_name):
    zbx_op = ZabbixOp()
    host_info = zbx_op.host_info(zbx_name, host)
    graph = zbx_op.host_graph(zbx_name, host_info, graph_name)
    if graph:
        stime = zbx_op._x_hour_ago()
        period_time = zbx_op._x_hour_ago_to_time() * 3600

        for i in graph:
            graph_url = '{}?graphid={}&width=900&height=200&period={}&stime={}'.format(zbx_op.graph_url(zbx_name), i['graphid'], period_time, stime)
            graph_img = zbx_op.graph_image_download(zbx_name, graph_url)
            bot.send_photo(chat_id, photo=open(graph_img, 'rb'))
            return True
    else:
        bot.send_message(chat_id, text='{} graph does not exist in {}'.format(host, graph_name))
        return False


def zbx_host_list_download(bot, chat_id, zbx_name, list_type):
    zbx_op = ZabbixOp()
    tmp_csv = '{}/{}.csv'.format(zbx_op.file_dir, list_type)
    try:
        if list_type.lower() == 'monitored list':
            res = zbx_op.host_list(zbx_name, monitored=True)
        elif list_type.lower() == 'not monitored list':
            res = zbx_op.host_list(zbx_name, monitored=False)
        else:
            res = zbx_op.host_list(zbx_name, monitored=True, all_list=True)
    except ZabbixAPIException as e:
        bot.send_message(chat_id, text='An error has occurred.\n{}'.format(repr(e)))
    except Exception as e:
        bot.send_message(chat_id, text='An error has occurred.\n'
                                       'Zabbix API call failed. please check your network or access information')
    else:
        if res:
            with open(tmp_csv, 'w', encoding='utf-8', newline='') as f:
                csv_writer = csv.writer(f)
                for i in sorted(res):
                    host_info = zbx_op.host_info(zbx_name, res[i])
                    csv_writer.writerow([host_info['host'], host_info['ip']])

            bot.send_document(chat_id, document=open(tmp_csv, 'rb'))
            return True
        else:
            bot.send_message(chat_id, text='Host does not exist in zabbix.')
            return False
