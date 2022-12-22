from environs import Env


env = Env()
env.read_env('logs_db.env')

# DB settings
LOGS_DB_HOST = env.str('LOGS_DB_HOST')
LOGS_DB_PORT = env.str('LOGS_DB_PORT')

LOGS_DB_LOGIN = env.str('LOGS_DB_LOGIN')
LOGS_DB_PASS = env.str('LOGS_DB_PASS')

LOGS_DB_DRIVER = env.str('LOGS_DB_DRIVER')

LOGS_DB_NAME = env.str('LOGS_DB_NAME')

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
