import os

# ----- [Base] -----
# Configuration base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DIR = os.path.join(os.path.dirname(BASE_DIR), 'tmp_file')

VERSION = '1.0'

# ----- [Telegram] -----
# Telegram Bot 의 token 을 설정합니다
token = ''

# ----- [Zabbix] -----
# Zabbix 의 접속 정보를 설정합니다
# 'ZABBIX_NAME': Zabbix를 식별할 수 있는 이름을 설정합니다
# 'USER': Zabbix 로그인 계정을 입력합니다
# 'PASSWORD': Zabbix 로그인 계정의 패스워드를 입력합니다
# 'URL': Zabbix의 접속 주소(URL)을 입력합니다
#
# Example) 여러 개의 Zabbix 에 사용할 경우 다음과 같이 여러 개의 접속 정보를 입력합니다
# ZABBIX_INFO = {
#     'Asia_Seoul_Zabbix': {
#         'USER': 'admin',
#         'PASSWORD': 'admin_password',
#         'URL': 'https://192.168.10.2'
#     },
#     'US_NewYork_Zabbix_1': {
#         'USER': 'ny_admin',
#         'PASSWORD': 'newyork',
#         'URL': 'https://10.0.0.2/zabbix'
#     },
#     'US_California': {
#         'USER': 'administrator',
#         'PASSWORD': 'PASSWORD',
#         'URL': 'https://10.100.0.2/zabbix'
#     }
# }
ZABBIX_INFO = {
    'ZABBIX_NAME': {
        'USER': '',
        'PASSWORD': '',
        'URL': ''
    }
}

# Zabbix Trigger Issue 를 가져올 때의 최대 개수를 설정합니다
zabbix_issue_limit = 20

# Zabbix Trigger Issue 를 가져오는 Level 을 설정합니다
# Trigger Level
# 0: Not classfied(Unknown severity.)
# 1: Infomation(For information purposes.)
# 2: Warning(Be warned.)
# 3: Average(Average problem.)
# 4: High(Something importance has happened.)
# 5: Disaster(Disaster. Financial losses, etc.)
# Reference: https://www.zabbix.com/documentation/4.0/manual/config/triggers/severity
zabbix_min_severity = 3
zabbix_severity = {
    'Not-classfied': 0,
    'Information': 1,
    'Warning': 2,
    'Average': 3,
    'High': 4,
    'Disaster': 5
}

# Zabbix Graph 의 시작 시간을 설정합니다
# Graph 를 가져오게 될 때, 현재 시간에서 설정된 시간만큼 빼서 가져오게 됩니다
# Default 값은 3시간 전으로, 현재 시간의 3시간 전부터의 데이터 그래프를 가져옵니다
zabbix_graph_stime = 3

# ----- [Bot] -----
# Bot access restrict
# Bot 사용자 제한 기능 설정. Telegram UserID를 통해 bot 을 사용할 수 있는 사용자를 제한할 수 있습니다
# False : 사용자 제한을 사용하지 않습니다
# True  : 'allow_users' 에 설정한 사용자만 사용이 가능합니다
use_access_restrict = False

# 접근 권한이 없는 사용자가 Bot 을 사용한 경우, 사용자에게 '권한이 없습니다' 메시지를 발송합니다
# False : 사용자에게 알림 메시지를 발송하지 않습니다
# True  : 사용자에게 '권한이 없습니다' 메시지를 발송합니다
use_access_restrict_notification = True

# 'use_access_restrict_notification' 옵션을 사용하는 경우, 사용자에게 발송한 메시지 내용을 설정합니다
restrict_notification_message = 'Access denied'

# Bot 을 사용할 수 있는 사용자를 설정합니다
# 사용자는 1명 또는 다수의 사람을 설정할 수 있습니다
# 'telegram_user_id': Telegram 의 UserID 를 입력합니다. UserId를 모르는 경우 아래 참조를 통해 확인할 수 있습니다
# 'user_name': 사용자 이름을 입력합니다(임의로 설정해도 무방합니다)
# 나의 Telegram UserID 확인 : @userinfobot 을 통해 나의 Telegram UserId를 확인할 수 있습니다
# Reference: https://bigone.zendesk.com/hc/en-us/articles/360008014894-How-to-get-the-Telegram-user-ID-
allow_users = {
    'telegram_user_id': 'user_name',
    'telegram_user_id2': 'user_name2'
}
