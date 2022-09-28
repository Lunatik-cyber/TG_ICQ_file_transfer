import os
import random
import logging

import requests
from bot.bot import Bot
from bot.handler import MessageHandler

from config import Config

logging.basicConfig(level=Config.LOG_LEVEL)
TOKEN = Config.icq.icq_token  # bot token
bot = Bot(token=TOKEN)


def get_my_id(bot, event):
    print(event)
    # Команда /myid
    if event.text == '/myid':
        bot.send_text(chat_id=event.from_chat, text=event.from_chat)


if __name__ == '__main__':
    bot.dispatcher.add_handler(MessageHandler(callback=get_my_id))
    bot.start_polling()
    bot.idle()


