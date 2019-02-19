import logging
from functools import wraps
from config import config

logger = logging.getLogger(__name__)


def access_restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        # 접근제한을 사용하는 경우
        if config.use_access_restrict:
            # access_restircted 설정 여부에 따라 동작 결정
            # allow_users 목록에 없는 경우 설정 여부에 bot 메시지 전송 결정
            user_id = update.effective_user.id
            first_name = update.effective_user.first_name
            chat_id = update.message.chat_id
            if str(user_id) not in config.allow_users:
                logger.info('access denied for {}({})').format(user_id, first_name)
                if config.use_access_restrict_notification:
                    bot.send_message(chat_id, text=config.restrict_notification_message)

                return
            return func(bot, update, *args, **kwargs)
        # 접근 제한을 사용하지 않는 경우
        else:
            return func(bot, update, *args, **kwargs)

    return wrapped
