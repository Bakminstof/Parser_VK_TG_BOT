from environs import Env

from data.prices import SLOT_PERCENT

env = Env()
env.read_env('bot.env')

# Refresh time for collect posts
REFRESH_TIME = 60 * 60  # 60 min.

# for debug
DEBUG = False

# Telegram settings
TG_API_ID = env.str('TG_API_ID')
TG_API_HASH = env.str('TG_API_HASH')

TG_PHONE = env.str('TG_PHONE')

SUPPORT = 'https://t.me/Foster_sup'

# VK settings
ACCESS_TOKEN = env.str('ACCESS_TOKEN')
VERSION_VK_API = env.str('VERSION_VK_API')

# Bot settings
BOT_TOKEN = env.str('BOT_TOKEN')

BOT_INFO = 'Бот раз в час сканирует группы (Вконтакте/Телеграм) для сбора информации, собирает новые посты' \
           ' и отправляет их в группы для отправки в Телеграмм или пользователю Телеграм.' \
           '\n* Бот собирает из групп Вконтакте только те посты, в которых есть текст и/или фото/видео.' \
           '\n* Бот собирает из групп Телеграм только те посты, которые содержат: ' \
           'текст, фото, видео, документ, анимация, голосовое сообщение, видеосообщение, контакт.' \
           '\n* Бот сможет отправлять информацию в группу в Телеграме только в том случае, ' \
           'если он добавлен в нее и ему предоставлен доступ к сообщениям.' \
           '\n* Бот не может брать информацию от пользователей или от других ботов.' \
           '\n* Если подписку не продлевать, то дополнительные слоты групп будут сброшены' \
           ' и при обновлении подписки их придётся покупать заново.' \
           '\n* При добавлении слота группы стоимость подписки возрастает на {SLOT_PERCENT}% ' \
           'от базовой стоимости подписки за каждый слот.' \
           '\n\nПо всем вопросам обращаться - <b><a href="{SUPPORT}">Поддержка</a></b>'.format(
               SLOT_PERCENT=SLOT_PERCENT,
               SUPPORT=SUPPORT
           )

START_MESSAGE = 'Вас приветствует бот-парсер! ' \
                'Я могу собираю посты в Телграмм или Вконтакте и отправлять их в Телеграм. ' \
                'Надеюсь, вам вам понравиться данный сервис :)'

ADMINS = env.list('ADMINS')

# MAIN DB settings
MAIN_DB_DRIVER = env.str('MAIN_DB_DRIVER')

MAIN_DB_NAME = env.str('MAIN_DB_NAME')

MAIN_DB_LOGIN = env.str('MAIN_DB_LOGIN')
MAIN_DB_PASS = env.str('MAIN_DB_PASS')

MAIN_DB_HOST = env.str('MAIN_DB_HOST')
MAIN_DB_PORT = env.str('MAIN_DB_PORT')

MAIN_DB_URI = '{driver}://{auth}{server}/{db_name}'.format(
    driver=MAIN_DB_DRIVER,
    auth='{login}:{password}@'.format(
        login=MAIN_DB_LOGIN,
        password=MAIN_DB_PASS
    ) if MAIN_DB_LOGIN and MAIN_DB_PASS else '',
    server='{host}:{port}'.format(
        host=MAIN_DB_HOST,
        port=MAIN_DB_PORT
    ) if MAIN_DB_HOST and MAIN_DB_PORT else '',
    db_name=MAIN_DB_NAME
)

# Logs DB setting
LOGS_DB_DRIVER = env.str('LOGS_DB_DRIVER')

LOGS_DB_NAME = env.str('LOGS_DB_NAME')

LOGS_DB_LOGIN = env.str('LOGS_DB_LOGIN')
LOGS_DB_PASS = env.str('LOGS_DB_PASS')

LOGS_DB_HOST = env.str('LOGS_DB_HOST')
LOGS_DB_PORT = env.str('LOGS_DB_PORT')

LOGS_DB_URI = '{driver}://{auth}{server}/{db_name}'.format(
    driver=LOGS_DB_DRIVER,
    auth='{login}:{password}@'.format(
        login=LOGS_DB_LOGIN,
        password=LOGS_DB_PASS
    ) if LOGS_DB_LOGIN and LOGS_DB_PASS else '',
    server='{host}:{port}'.format(
        host=LOGS_DB_HOST,
        port=LOGS_DB_PORT
    ) if LOGS_DB_HOST and LOGS_DB_PORT else '',
    db_name=LOGS_DB_NAME
)

# Payments settings
QIWI_API_TOKEN = env.str('QIWI_API_TOKEN')

QIWI_PHONE = env.str('QIWI_PHONE')

QIWI_PAYMENT_URL = env.str('QIWI_PAYMENT_URL')
