# Zabbix-op-bot
-------

Zabbix-op-bot은 Telegram 을 통해 Zabbix의 Agent host를 관리합니다. Zabbix에 발생한 트리거 이슈를 레벨별로 조회하고 Agent host의 모니터링 상태를 조회하거나 변경할 수 있으며, Agent host의 그래프를 조회하여 이미지로 가져올 수 있습니다. 또한 Agent host 리스트를 타입별로(전체/모니터 상태의 호스트/모니터링 중이지 않은 호스트) 선택하여 조회 또는 csv형식으로 다운로드할 수 있습니다

#### 지원하는 기능:
  - Zabbix에서 발생한 트리거 이슈 레벨별 조회
  - Agent host 모니터링 상태 조회 및 변경(Monitored Enable/Disable)
  - Agent host 그래프 조회
  - Agent host 리스트 조회 또는 .csv 파일 다운로드


### Installation
zabbix-op-bot은 [python 3.6.3](https://www.python.org/downloads/release/python-363/) 에서 만들어졌습니다

zabbix-op-bot을 다운로드 받고 의존성 파일을 설치합니다
(다른 파이썬 프로그램을 사용중인 경우, virtualenv를 통해 별도의 가상환경을 통해 실행하는 것을 권장합니다)
```sh
$ git clone https://github.com/99-66/zabbix-op-bot.git
$ cd zabbix-op-bot/
$ pip install -r requirements.txt
```

### Configuration

zabbix-op-bot을 사용하기 위한 설정 파일의 내용을 변경합니다

설정 파일 열기:
```sh
$ vim config/config.py
```

Telegram 관련 설정:
Telegram bot만들기와 같은 내용은 여기에 없습니다!
Bot만들기는 아래 링크를 참고해주세요
https://docs.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0 
```sh
# ----- [Telegram] -----
# Telegram Bot 의 token 을 설정합니다
token = 'telegram bot의 토큰으로 변경해주세요'
```

Zabbix 로그인 정보 설정:
```sh
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
```
Zabbix 이슈 트리거 최대 개수 설정(default 20):
```sh
# Zabbix Trigger Issue 를 가져올 때의 최대 개수를 설정합니다
zabbix_issue_limit = 20
```

Zabbix Agent host 그래프 시작 시간 설정(default 3):
```sh
# Zabbix Graph 의 시작 시간을 설정합니다
# Graph 를 가져오게 될 때, 현재 시간에서 설정된 시간만큼 빼서 가져오게 됩니다
# Default 값은 3시간 전으로, 현재 시간의 3시간 전부터의 데이터 그래프를 가져옵니다
zabbix_graph_stime = 3
```

Bot 제한 설정:
```sh
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
```

### Running service
파이썬을 통해 스크립트를 실행합니다. supervisor나 Docker를 통해 데몬 방식으로 서비스 구동을 권장합니다
```sh
$ python main.py
```
### Docker
zabbix-op-bot을 Docker container를 통해 실행할 수 있습니다
미리 만들어진 container 이미지는 존재하지 않으며, git clone을 통해 다운로드하여 Dockerfile을 통해 이미지를 빌드합니다
이미 앞에서 git clone을 통해 다운로드 하였다면 해당 단계는 넘어가서  바로 Dockerfiler을 작성하여 빌드합니다
```sh
git clone https://github.com/99-66/zabbix-op-bot.git
```

Dockerfile 생성:
```sh
$ vim Dockerfile
````

Dockerfile 작성:
```sh
FROM python:3.6.6-slim

COPY zabbix-op-bot /zabbix-op-bot
WORKDIR /zabbix-op-bot

RUN cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime
RUN pip install -r requirements.txt

CMD ["python", "/zabbix-op-bot/main.py"]
```
Dockerfile을 통해 container image build. [CODE VERSION]은 zabbix-op-bot의 버전 또는 임의로 관리할 번호를 입력합니다:
```sh
$ docker build -t zabbix-op-bot:[CODE VERSION] .

ex) $ docker build -t zabbix-op-bot:1.0 .
```

Docker 실행 []부분은 임의로 변경하여 실행합니다. 또는 예를 참조하여 실행합니다:
[CODE VERSION]은 build했을 때의 코드 버전을 입력합니다
```sh
$ docker run -d --name [CONTAINER NAME] zabbix-op-bot:[CODE VERSION]

ex) $ docker run -d --name zabbix-op-bot zabbix-op-bot:1.0
```
### Service Usage
Telegram 토큰 설정과 서비스 실행이 정상적으로 되었다면, 텔레그램 봇에게 다음과 같은 명령을 내려보세요!
(BotFather의 botcommand를 사용 설정 하면 '/'만 입력해도 자동으로 사용 가능한 명령어를 알려줍니다
![Telegram command use](https://user-images.githubusercontent.com/31076511/53035476-dee9c580-34b8-11e9-9f04-36cb2eeecdd2.png)
```sh
/zabbixop
```

### Conversation Flow
![Conversation Flow](https://user-images.githubusercontent.com/31076511/53035507-f163ff00-34b8-11e9-98de-d28b55b4daff.png)

### Next Plan
  - 코드별 주석 추가
  - host_info 조회 시간 줄이기외 코드 개선
  - 예외처리 재확인 및 강화
  - 버그 개선
  - 데모 봇 추가


### Contact
 - 6199@outlook.kr
 - 관련된 문의는 어느 것이든 환영입니다!(비난과 비판도 함께 환영해요!)
