import os

from icq import bot

temp_dir = os.path.join(os.getcwd(), 'temp')


class ICQ_transfer:
    def __init__(self, user_id):
        self.user_id = user_id

    def send_file_to_icq(self, file_name):
        file_path = os.path.join(temp_dir, file_name)
        with open(file_path, 'rb') as file:
            bot.send_file(chat_id=self.user_id, file=file, file_name=file_name)
        os.remove(file_path)
