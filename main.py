import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from zabbix_op.bot.conversation.zabbixop import zabbix_op_conversation_handler, callback_monitor_list
from config import config

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Version command
# check current bot version
def version(bot, update):
    chat_id = update.message.chat_id
    logger.info('command: /version  user: {}({})').format(update.effective_user.id, update.effective_user.first_name)

    bot.send_message(chat_id, text='zabbix-op-bot Version {}'.format(config.VERSION))


# Error handler
def error(bot, update, error):
    logger.warning('Update {} caused error {}'.format(update, error))


def main():
    token = config.token
    updater = Updater(token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('version', version))
    dp.add_handler(zabbix_op_conversation_handler)

    dp.add_handler(CallbackQueryHandler(callback_monitor_list, pass_user_data=True))

    # Error handler
    dp.add_error_handler(error)

    # bot polling - loop
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()