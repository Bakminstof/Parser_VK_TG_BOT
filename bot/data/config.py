from environs import Env

from data.prices import SLOT_PERCENT

env = Env()
env.read_env('bot.env')

# Refresh time for collect posts
REFRESH_TIME = 60 * 60  # 60 min.

# for debug
DEBUG = True

# Telegram settings
TG_API_ID = env.str('TG_API_ID')
TG_API_HASH = env.str('TG_API_HASH')

PHONE_NUMBER = env.str('PHONE_NUMBER')

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

# DB settings
DB_DRIVER = env.str('DB_DRIVER')

DB_NAME = env.str('DB_NAME')

DB_LOGIN = env.str('DB_LOGIN')
DB_PASS = env.str('DB_PASS')

DB_HOST = env.str('DB_HOST')
DB_PORT = env.str('DB_PORT')

DB_URI = '{driver}://{auth}{server}/{db_name}'.format(
    driver=DB_DRIVER,
    auth='{login}:{password}@'.format(login=DB_LOGIN, password=DB_PASS) if DB_LOGIN and DB_PASS else '',
    server='{host}:{port}'.format(host=DB_HOST, port=DB_PORT) if DB_HOST and DB_PORT else '',
    host=DB_HOST,
    port=DB_PORT,
    db_name=DB_NAME
)

# Payments settings
PAYMENTS_TOKEN = env.str('PAYMENTS_TOKEN')

CURRENCY_RUB = 'rub'
