class Telegram:
    tg_token = ''
    admin = 111111111


class ICQ:
    icq_token = ''
    admin = 1111111111


class Config:
    tg = Telegram()
    icq = ICQ()
    DEBUG = False
    LOG_LEVEL = 'INFO'

