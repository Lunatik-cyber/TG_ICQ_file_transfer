import datetime
import logging
import os

from aiogram import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor

from config import Config
from functions import ICQ_transfer
from peewee import *

logging.basicConfig(level=Config.LOG_LEVEL)

bot = Bot(token=Config.tg.tg_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

admin = Config.tg.admin

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

if Config.DEBUG:
    db = SqliteDatabase(':memory:')
else:
    db = SqliteDatabase('users.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = IntegerField(primary_key=True)
    user_id = IntegerField(null=False)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    full_name = CharField(null=True)
    icq_id = IntegerField(null=True)
    banned = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_at = DateTimeField(default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        table_name = 'users'


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class UserControl:
    def __init__(self, message):
        self.user_id = message.from_user.id
        self.username = message.from_user.username
        self.first_name = message.from_user.first_name
        self.last_name = message.from_user.last_name
        self.full_name = message.from_user.full_name

    async def check_user(self):
        if User.select().where(User.user_id == self.user_id).exists():
            User.update(
                username=self.username,
                first_name=self.first_name,
                last_name=self.last_name,
                full_name=self.full_name,
                updated_at=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).where(
                User.user_id == self.user_id
            ).execute()
            return True
        else:
            User.create(
                user_id=self.user_id,
                username=self.username,
                first_name=self.first_name,
                last_name=self.last_name,
                full_name=self.full_name
            )
            return False

    async def check_ban(self):
        if User.select().where(User.user_id == self.user_id).exists():
            if User.select().where(User.user_id == self.user_id).get().banned:
                return True
            else:
                return False
        else:
            return False

    async def check_icq(self):
        if User.select().where(User.user_id == self.user_id).exists():
            if User.select().where(User.user_id == self.user_id).get().icq_id:
                return True
            else:
                return False
        else:
            return False

    async def get_icq(self):
        if User.select().where(User.user_id == self.user_id).exists():
            return User.select().where(User.user_id == self.user_id).get().icq_id
        else:
            return False

    @staticmethod
    async def ban_user(user_id):
        if User.select().where(User.user_id == user_id).exists():
            User.update(banned=True).where(User.user_id == user_id).execute()
            return True
        else:
            return False

    @staticmethod
    async def unban_user(user_id):
        if User.select().where(User.user_id == user_id).exists():
            User.update(banned=False).where(User.user_id == user_id).execute()
            return True
        else:
            return False

    @staticmethod
    async def update_icq(user_id, icq_id):
        if User.select().where(User.user_id == user_id).exists():
            User.update(icq_id=icq_id).where(User.user_id == user_id).execute()
            return True
        else:
            return False


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    user = UserControl(message)
    await user.check_user()
    if not await user.check_ban():
        await message.answer(
            '<b>Привет!</b> Я бот для отправки файлов в <b>ICQ</b>.\n\n'
            '<b>Команды:</b>\n'
            '<i>🌀 Помощь: <b>/help</b></i>\n'
            '<i>🌀 Для начала работы введите: <b>/start</b></i>\n'
            '<i>🌀 Для получения своего <b>ICQ ID</b> введите команду: <b>/icq</b></i>\n'
            '<i>🌀 Для отправки файла просто перешлите его мне</i>\n\n'
            '<b>❗ Размер файла не должен превышать 20 МБ ❗</b>\n\n'
            'Если у вас есть вопросы, пишите: <b>@ShellRok</b>'
        )


@dp.message_handler(commands=['ban'], state='*')
async def ban(message: types.Message, state: FSMContext):
    if message.from_user.id == admin:
        await state.finish()
        user_id = message.get_args()
        if UserControl.ban_user(user_id):
            await message.answer(f'Пользователь {user_id} заблокирован.')
        else:
            await message.answer(f'Пользователь {user_id} не найден.')
    else:
        await message.answer('У вас нет прав.')


@dp.message_handler(commands=['unban'], state='*')
async def unban(message: types.Message, state: FSMContext):
    if message.from_user.id == admin:
        await state.finish()
        user_id = message.get_args()
        if UserControl.unban_user(user_id):
            await message.answer(f'Пользователь {user_id} разблокирован.')
        else:
            await message.answer(f'Пользователь {user_id} не найден.')
    else:
        await message.answer('У вас нет прав.')


@dp.message_handler(commands=['get_banned_users'], state='*')
async def get_banned_users(message: types.Message, state: FSMContext):
    if message.from_user.id == admin:
        await state.finish()
        users = User.select().where(User.banned == True)
        if users.count() > 0:
            text = ''
            for user in users:
                text += f'{user.user_id}\n'
            await message.answer(text)
        else:
            await message.answer('Нет заблокированных пользователей.')
    else:
        await message.answer('У вас нет прав.')


class SetICQ(StatesGroup):
    icq = State()


@dp.message_handler(commands=['icq'], state='*')
async def icq(message: types.Message, state: FSMContext):
    await state.finish()
    user = UserControl(message)
    await user.check_user()
    if not await user.check_ban():
        await message.answer('Введите ID ICQ его можно получить командой /myid в ICQ боте: @AF_icq_file_bot')
        await SetICQ.icq.set()


@dp.message_handler(lambda message: message.text.isdigit(), state=SetICQ.icq)
async def icq(message: types.Message, state: FSMContext):
    user = UserControl(message)
    await user.check_user()
    if not await user.check_ban():
        if await UserControl.update_icq(message.from_user.id, message.text):
            await message.answer('ID ICQ обновлен.')
        else:
            await message.answer('Ошибка.')
        await state.finish()


@dp.message_handler(commands=['stats'], state='*')
async def stats(message: types.Message, state: FSMContext):
    if message.from_user.id == admin:
        await state.finish()
        users = User.select()
        await message.answer(
            f'Всего пользователей: {users.count()}\n'
            f'За сегодня: {users.where(User.created_at == datetime.date.today()).count()}\n'
            f'За неделю: {users.where(User.created_at >= datetime.date.today() - datetime.timedelta(days=7)).count()}\n'
            f'За месяц: {users.where(User.created_at >= datetime.date.today() - datetime.timedelta(days=30)).count()}\n'
            f'Заблокировано: {User.select().where(User.banned == True).count()}'
        )
    else:
        await message.answer('У вас нет прав.')


@dp.message_handler(content_types='audio', state='*')
async def audio(message: types.Message, state: FSMContext):
    user = UserControl(message)
    await user.check_user()
    if not await user.check_ban():
        file_name = message.audio.file_unique_id + '.mp3'
        src = f'temp/{file_name}'
        await message.audio.download(src)
        if os.path.getsize(src) <= 20971520:
            if await user.check_icq():
                ICQ_transfer(await user.get_icq()).send_file_to_icq(file_name)
                await message.answer('Файл отправлен.')
            else:
                await message.answer('Укажите ID ICQ.')
        else:
            await message.answer('Файл слишком большой.')


@dp.message_handler(content_types='video', state='*')
async def video(message: types.Message, state: FSMContext):
    user = UserControl(message)
    await user.check_user()
    if not await user.check_ban():
        file_name = message.video.file_unique_id + '.mp4'
        src = f'temp/{file_name}'
        await message.video.download(src)
        if os.path.getsize(src) <= 20971520:
            if await user.check_icq():
                ICQ_transfer(await user.get_icq()).send_file_to_icq(message.document.file_name)
                await message.answer('Файл отправлен.')
            else:
                await message.answer('Укажите ID ICQ.')
        else:
            await message.answer('Файл слишком большой.')


@dp.message_handler(content_types='photo', state='*')
async def photo(message: types.Message, state: FSMContext):
    user = UserControl(message)
    await user.check_user()
    if not await user.check_ban():
        file_name = f'{message.photo[-1].file_unique_id}.jpg'
        src = f'temp/{file_name}'
        await message.photo[-1].download(src)
        if os.path.getsize(src) <= 20971520:
            if await user.check_icq():
                ICQ_transfer(await user.get_icq()).send_file_to_icq(file_name)
                await message.answer('Файл отправлен.')
            else:
                await message.answer('Укажите ID ICQ.')
        else:
            await message.answer('Файл слишком большой.')


@dp.message_handler(content_types='document', state='*')
async def send_file(message: types.Message):
    user = UserControl(message)
    await user.check_user()
    if not await user.check_ban():
        src = f'temp/{message.document.file_name}'
        await message.document.download(src)

        if os.path.getsize(src) <= 20971520:
            if await user.check_icq():
                ICQ_transfer(await user.get_icq()).send_file_to_icq(message.document.file_name)
                await message.answer('Файл отправлен.')
            else:
                await message.answer('Укажите ID ICQ.')
        else:
            await message.answer('Файл слишком большой.')


@dp.message_handler(commands=['help'], state='*')
async def help(message: types.Message, state: FSMContext):
    user = UserControl(message)
    await user.check_user()
    if not await user.check_ban():
        await message.answer(
            '<b>Привет!</b> Я бот для отправки файлов в <b>ICQ</b>.\n\n'
            '<b>Команды:</b>\n'
            '<i>🌀 Для начала работы введите: <b>/start</b></i>\n'
            '<i>🌀 Для получения своего <b>ICQ ID</b> введите команду: <b>/icq</b></i>\n'
            '<i>🌀 Для отправки файла просто перешлите его мне</i>\n\n'
            '<b>❗ Размер файла не должен превышать 20 МБ ❗</b>\n\n'
            '<b>Администратирование:</b>\n'
            '<i>🌀 Заблокировать пользователя: <b>/ban</b></i>\n'
            '<i>🌀 Разблокировать пользователя: <b>/unban</b></i>\n'
            '<i>🌀 Получить список заблокированных пользователей: <b>/get_benned_users</b></i>\n'
            '<i>🌀 Статистика бота: <b>/stats</b></i>\n'
            '<i>🌀 Помощь: <b>/help</b></i>\n\n'
            'Если у вас есть вопросы, пишите: <b>@ShellRok</b>'
        )


if __name__ == '__main__':
    db.create_tables([User])
    if not os.path.exists('temp'):
        os.mkdir('temp')
    executor.start_polling(dp, skip_updates=True)
