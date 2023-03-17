import logging
import time
from config import *
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db import Database

# Логгирование и создание бота
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=storage)
db = Database('database.db')


# приветствует пользователя
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, 'рад приветствовать')


# задаем время командой /time
@dp.message_handler(commands=['time'])
async def time_set(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id == admin_id:
            global mail_time
            mail_time = int(message.text[6:])


# рассылка командой /sendall
@dp.message_handler(commands=['sendall'])
async def sendall(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id == admin_id:
            text = message.text[9:]
            users = db.get_user()
            await bot.send_message(message.from_user.id, f'рассылка началась\nинтервал рассылки'
                                                         f' {mail_time} минут(a)')
            while True:
                for row in users:
                    try:
                        await bot.send_message(row[0], text)
                        time.sleep(int(mail_time)*60)
                        if int(row[1]) != 1:
                            db.set_active(row[0], 1)
                    except:
                        db.set_active(row[0], 0)


@dp.message_handler()
async def nothing(message: types.Message):
    if message.from_user.id == admin_id:
        await message.answer('Введи интервал командой /time, \nа затем начни рассылку\
         командой /sendall')
    else:
        await message.answer('реклама')


# Конструкция запуска бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
