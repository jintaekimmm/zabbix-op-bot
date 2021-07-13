import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, RegexHandler, Filters, MessageHandler
from config import config
from decorators import access_restricted
from zabbix_op import bot_command
from common import build_menu, is_next, is_previous

ZBX_NAME, ZBX_MENU, ZBX_HOST_MENU, ZBX_HOST_LIST, ZBX_SEVERITY, ZBX_ACTION, ZBX_HOST, ZBX_GRAPH_HOST, ZBX_GRAPH_RESOURCE, ZBX_HOST_DOWNLOAD = range(10)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Conversation start ('current')
@access_restricted
def zabbix_op_start(bot, update):
    logger.info('command: /zabbixop  user: {}({})'.format(update.effective_user.id, update.effective_user.first_name))

    zbx_names = [key for key in config.ZABBIX_INFO.keys()]

    reply_keyboard = [zbx_names[i:i+3] for i in range(0, len(zbx_names), 3)]
    update.message.reply_text(text='Please select zabbix.\nSend /end to end the conversation.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True, selective=True))

    return ZBX_NAME


# Conversation Tree(Zabbix name - 'current')
@access_restricted
def select_menu(bot, update, user_data):
    user_data['zbx_name'] = update.message.text

    reply_keyboard = [['Get issues', 'Get hosts']]
    update.message.reply_text(text='Please select menu.\nSend /end to end the conversation.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True, selective=True))

    return ZBX_MENU


# Conversation Tree(Zabbix name - Get hosts - 'current')
@access_restricted
def select_hosts_menu(bot, update, user_data):
    reply_keyboard = [['Host status', 'Host list(view)'], ['Host graph', 'Host list(download)']]
    update.message.reply_text(text='Please select menu.\nSend /end to end the conversation.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True, selective=True))

    return ZBX_HOST_MENU


# Conversation Tree(Zabbix name - Get hosts - Host list - 'current')
@access_restricted
def select_host_list(bot, update, user_data):
    reply_keyboard = [['Monitored list', 'Not Monitored list'], ['All Host list']]
    update.message.reply_text(text='Please select menu.\nSend /end to end the conversation.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True, selective=True))

    return ZBX_HOST_LIST


# Conversation Tree(Zabbix name - Get issues - 'current')
@access_restricted
def select_trigger_severity(bot, update, user_data):
    reply_keyboard = [['Not-classfied', 'Information'], ['Warning', 'Average'], ['High', 'Disaster']]
    update.message.reply_text(text='Please select trigger severity to from zabbix.\nSend /end to end the conversation.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True, selective=True))
    return ZBX_SEVERITY


# Conversation Tree(Zabbix name - Get issues - trigger_severity - 'current')
@access_restricted
def send_issue(bot, update, user_data):
    chat_id = update.message.chat_id
    zbx_name = user_data['zbx_name']
    severity = update.message.text

    update.message.reply_text(text='Get the issue list of trigger severity \'{}\'.'.format(severity),
                              reply_markup=ReplyKeyboardRemove())
    bot_command.zbx_get_issue(bot, chat_id, severity, zbx_name)

    return ConversationHandler.END


# Conversation Tree(Zabbix name - Get hosts - Host status - 'current')
@access_restricted
def host_action(bot, update, user_data):
    reply_keyboard = [['Enable', 'Disable', 'Status']]
    update.message.reply_text(text='Please select an action to take against the hosts of Zabbix.\n'
                                   'Send /end to end the conversation.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True, selective=True))
    return ZBX_ACTION


# Conversation Tree(Zabbix name - Get Hosts - Host status - Enable|Disable|Status - 'current')
@access_restricted
def change_host(bot, update, user_data):
    user_data['zbx_action'] = update.message.text
    update.message.reply_text(text='Please enter hostname or ip.\nSend \end to end the conversation.',
                              reply_markup=ReplyKeyboardRemove())

    return ZBX_HOST


# Conversation Tree(Zabbix name - Get Hosts - Host status - Enable|Disable|Status - typing host - 'current')
@access_restricted
def change_status(bot, update, user_data):
    chat_id = update.message.chat_id
    host = update.message.text
    zbx_action = user_data['zbx_action'].lower()
    zbx_name = user_data['zbx_name']

    if zbx_action == 'status':
        bot_command.zbx_host_monitor_status(bot, chat_id, zbx_name, host)
        return ConversationHandler.END
    else:
        bot_command.zbx_host_change_status(bot, chat_id, zbx_name, host, zbx_action)
        return ConversationHandler.END


# Conversation Tree(Zabbix name - Get Hosts - Host list - select list type - 'current')
@access_restricted
def monitor_list(bot, update, user_data):
    list_type = update.message.text
    chat_id = update.message.chat_id
    zbx_name = user_data['zbx_name']
    msg_id = int(update.message.message_id) + 1

    update.message.reply_text(text='Get the list you requested.\nIf you have many lists, it may take some time',
                              reply_markup=ReplyKeyboardRemove())

    search_result = bot_command.zbx_monitor_list(bot, chat_id, zbx_name, list_type)

    first = '{}_first'.format(msg_id)
    last = '{}_last'.format(msg_id)
    result = '{}_result'.format(msg_id)
    current = '{}_current'.format(msg_id)

    user_data[first] = 0
    user_data[last] = len(search_result) - 1
    user_data[result] = search_result
    user_data[current] = 0

    if len(search_result) > 1:
        keyboard = [
            InlineKeyboardButton('<<', callback_data=user_data[first]),
            InlineKeyboardButton('{}/{}'.format(user_data[first] + 1, user_data[last] + 1),
                                 callback_data=user_data[first]),
            InlineKeyboardButton('>>', callback_data=int(user_data[first] + 1)),
        ]
    else:
        keyboard = None

    if keyboard is not None:
        reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=3))
    else:
        reply_markup = None

    bot.send_message(chat_id, text=search_result[0], reply_markup=reply_markup)

    return ConversationHandler.END


# Monitor list conversation callback function
def callback_monitor_list(bot, update, user_data):
    query = update.callback_query
    msg_id = query.message.message_id
    chat_id = query.message.chat_id

    first = '{}_first'.format(msg_id)
    last = '{}_last'.format(msg_id)
    result = '{}_result'.format(msg_id)
    current = '{}_current'.format(msg_id)

    select_index = int(query.data)

    if user_data[first] <= select_index or select_index > user_data[last]:
        text = str(user_data[result][select_index])

        prev = is_previous(select_index, user_data[first])
        next = is_next(select_index, user_data[last])

        keybord = [
            InlineKeyboardButton('<<', callback_data=prev),
            InlineKeyboardButton('{}/{}'.format(select_index + 1, user_data[last] + 1), callback_data='None'),
            InlineKeyboardButton('>>', callback_data=next)
        ]
        reply_markup = InlineKeyboardMarkup(build_menu(keybord, n_cols=3))
        user_data[current] = select_index

        bot.edit_message_text(reply_markup=reply_markup, text=text, chat_id=chat_id, message_id=msg_id)


# Conversation Tree(Zabbix name - Get Hosts - Host graph - 'current')
def select_graph_host(bot, update, user_data):
    update.message.reply_text(text='Please enter hostname or ip.\nSend \end to end the conversation.',
                              reply_markup=ReplyKeyboardRemove())

    return ZBX_GRAPH_HOST


# Conversation Tree(Zabbix name - Get Hosts - Host graph - typing host - 'current')
def select_graph_list(bot, update, user_data):
    chat_id = update.message.chat_id
    user_data['zbx_host'] = update.message.text
    zbx_name = user_data['zbx_name']

    update.message.reply_text(text='Please enter a graph name or number.')
    graph_list = bot_command._zbx_host_graph_list(zbx_name, user_data['zbx_host'])
    user_data['graph_list'] = graph_list

    bot_command.zbx_host_graph_list(bot, chat_id, zbx_name, user_data['zbx_host'], graph_list)
    return ZBX_GRAPH_RESOURCE


# Conversation Tree(Zabbix name - Get Hosts - Host graph - typing host - typing graph - 'current')
def select_graph_resource(bot, update, user_data):
    chat_id = update.message.chat_id
    graph_name = update.message.text
    zbx_name = user_data['zbx_name']
    zbx_host = user_data['zbx_host']
    graph_list = user_data['graph_list']

    try:
        select_graph = graph_list[graph_name]
    except KeyError:
        select_graph = graph_name

    bot_command.zbx_host_graph_resource(bot, chat_id, zbx_name, zbx_host, select_graph)

    return ConversationHandler.END


# Conversation Tree(Zabbix name - Get Hosts - Host list(download) - 'current'
def select_host_download(bot, update, user_data):
    reply_keyboard = [['Monitored list', 'Not monitored list'], ['All monitored list']]
    update.message.reply_text(text='Please select a list of hosts to download.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True, selective=True))

    return ZBX_HOST_DOWNLOAD


# Conversation Tree(Zabbix name - Get Hosts - Host list(download) - select list type - 'current')
def select_download_type(bot, update, user_data):
    chat_id = update.message.chat_id
    list_type = update.message.text
    update.message.reply_text(text='Download the list of selected hosts.\nPlease wait..', reply_markup=ReplyKeyboardRemove())

    bot_command.zbx_host_list_download(bot, chat_id, user_data['zbx_name'], list_type)

    return ConversationHandler.END


@access_restricted
def end(bot, update):
    update.message.reply_text(text='conversation end.', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


zbx_names = config.ZABBIX_INFO.keys()
severity_names = config.zabbix_severity.keys()

zabbix_op_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('zabbixop', zabbix_op_start)],

    states={
        ZBX_NAME: [RegexHandler('^(' + '|'.join(zbx_names) + ')$', select_menu, pass_user_data=True)],
        ZBX_MENU: [RegexHandler('^((g|G)et (i|I)ssues)$', select_trigger_severity, pass_user_data=True),
                   RegexHandler('^((g|G)et (h|H)osts)$', select_hosts_menu, pass_user_data=True)],
        ZBX_HOST_MENU: [RegexHandler('^((h|H)ost (s|S)tatus)$', host_action, pass_user_data=True),
                        RegexHandler('^((h|H)ost (l|L)ist\(view\))$', select_host_list, pass_user_data=True),
                        RegexHandler('^((h|H)ost (g|G)raph)$', select_graph_host, pass_user_data=True),
                        RegexHandler('^((h|H)ost (l|L)ist\(download\))$', select_host_download, pass_user_data=True)],
        ZBX_HOST_LIST: [RegexHandler('^((m|M)onitored (l|L)ist|(n|N)ot (m|M)onitored (l|L)ist|'
                                     '(a|A)ll (h|H)ost (l|L)ist)$', monitor_list, pass_user_data=True)],
        ZBX_SEVERITY: [RegexHandler('^(' + '|'.join(severity_names) + ')$', send_issue, pass_user_data=True)],
        ZBX_ACTION: [RegexHandler('^((E|e)nable|(D|d)isable|(S|s)tatus)$', change_host, pass_user_data=True)],
        ZBX_HOST: [MessageHandler(Filters.text, change_status, pass_user_data=True)],
        ZBX_GRAPH_HOST: [MessageHandler(Filters.text, select_graph_list, pass_user_data=True)],
        ZBX_GRAPH_RESOURCE: [MessageHandler(Filters.text, select_graph_resource, pass_user_data=True)],
        ZBX_HOST_DOWNLOAD: [RegexHandler('^((m|M)onitored (l|L)ist|(n|N)ot (m|M)onitored (l|L)ist|'
                                           '(a|A)ll (h|H)ost (l|L)ist)$', select_download_type, pass_user_data=True)]

    },

    conversation_timeout=300,
    fallbacks=[CommandHandler('end', end)],
)