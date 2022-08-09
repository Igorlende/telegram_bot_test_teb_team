import platform
import asyncio
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text
from config import API_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from states import States
from aiogram.dispatcher import FSMContext
import re
from register import register_user

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message):
    button_registration = KeyboardButton('Реєстрація')
    keybord = ReplyKeyboardMarkup(resize_keyboard=True)
    keybord.add(button_registration)
    await States.start.set()
    await bot.send_message(message.from_user.id, "Виберіть варіант", reply_markup=keybord)


@dp.message_handler(state=States.start)
async def registration(message: types.Message):
    if message.text == 'Реєстрація':
        await States.login.set()
        await bot.send_message(message.from_user.id, "Вкажіть Login:", reply_markup=ReplyKeyboardRemove())
    else:
        button_registration = KeyboardButton('Реєстрація')
        keybord = ReplyKeyboardMarkup(resize_keyboard=True)
        keybord.add(button_registration)
        await bot.send_message(message.from_user.id, "Виберіть варіант", reply_markup=keybord)


@dp.message_handler(state=States.login)
async def get_login(message: types.Message, state: FSMContext):

    login = message.text
    if len(login) < 4:
        await bot.send_message(message.from_user.id, "Login некоректний, спробуйте ще раз")
        return
    check_login = re.search("^[a-zA-Z0-9_]*$", login)
    if check_login is None:
        await bot.send_message(message.from_user.id, "Login некоректний, спробуйте ще раз")
    else:
        await States.password.set()
        await state.update_data(login=login)
        await bot.send_message(message.from_user.id, "Вкажіть password:")


@dp.message_handler(state=States.password)
async def get_password(message: types.Message, state: FSMContext):

    password = message.text
    if len(password) < 6:
        await bot.send_message(message.from_user.id, "Password некоректний, спробуйте ще раз")
        return
    check_password = re.search("^[a-zA-Z0-9_]*$", password)
    if check_password is None:
        await bot.send_message(message.from_user.id, "Password некоректний, спробуйте ще раз")
    else:
        data = await state.get_data()
        login = data['login']
        await States.user_id.set()
        await state.update_data(password=password, login=login)
        await bot.send_message(message.from_user.id, "Вкажіть user_id:")


@dp.message_handler(state=States.user_id)
async def get_user_id(message: types.Message, state: FSMContext):

    user_id = message.text
    if len(user_id) < 10:
        await bot.send_message(message.from_user.id, "User_id некоректний, спробуйте ще раз")
        return
    check_user_id = re.search("^[0-9]*$", user_id)
    if check_user_id is None:
        await bot.send_message(message.from_user.id, "User_id некоректний, спробуйте ще раз")
    else:
        data = await state.get_data()
        login = data['login']
        password = data['password']
        await States.registration.set()
        await state.update_data(user_id=user_id, login=login, password=password)

        button_yes = KeyboardButton('Так')
        button_no = KeyboardButton('Ні')
        keybord = ReplyKeyboardMarkup(resize_keyboard=True)
        keybord.add(button_yes)
        keybord.add(button_no)
        await bot.send_message(message.from_user.id, "З даними все окей, реєструємось?", reply_markup=keybord)


@dp.message_handler(state=States.registration)
async def registration(message: types.Message, state: FSMContext):

    if message.text == "Ні":
        await state.finish()
        button_start = KeyboardButton('/start')
        keybord = ReplyKeyboardMarkup(resize_keyboard=True)
        keybord.add(button_start)
        await bot.send_message(message.from_user.id, "Добре, починайте спочатку.",
                               reply_markup=keybord)
    elif message.text == "Так":
        data = await state.get_data()
        user_id = data['user_id']
        login = data['login']
        password = data['password']
        await state.finish()
        res = await register_user({"user_id": user_id, "username": login, "password": password})
        if res == 'success':
            button_start = KeyboardButton('/start')
            keybord = ReplyKeyboardMarkup(resize_keyboard=True)
            keybord.add(button_start)
            await bot.send_message(message.from_user.id, "Реєстрація пройшла успішно!",
                                   reply_markup=keybord)
        else:
            button_start = KeyboardButton('/start')
            keybord = ReplyKeyboardMarkup(resize_keyboard=True)
            keybord.add(button_start)
            await bot.send_message(message.from_user.id, "Щось не вдалося..",
                                   reply_markup=keybord)

    else:
        button_start = KeyboardButton('/start')
        keybord = ReplyKeyboardMarkup(resize_keyboard=True)
        keybord.add(button_start)
        await bot.send_message(message.from_user.id, "Упс.. Натиснули щось не те.",
                               reply_markup=keybord)


@dp.message_handler(state="*")
async def zero(message: types.Message):
    await bot.send_message(message.from_user.id, "Нажміть /start")


if __name__ == '__main__':

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def on_shutdown(dp):
        await bot.close()
        await storage.close()

    executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)
