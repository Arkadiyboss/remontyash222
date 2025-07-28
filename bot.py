import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("Оставить заявку"), KeyboardButton("Частые вопросы"))
main_kb.add(KeyboardButton("Связаться с нами"))

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Здравствуйте! Я — бот сервиса 'Ремонтяш'. Чем могу помочь?", reply_markup=main_kb)

@dp.message_handler(lambda m: m.text == "Частые вопросы")
async def faq(message: types.Message):
    await message.answer("❓ Мы ремонтируем: стиральные машины, холодильники, микроволновки и другое.\n📍 Адрес: Хабаровск, ул. Пушкина, д. Колотушкина.\n🕙 Работаем: Пн–Пт с 10:00 до 19:00.")

@dp.message_handler(lambda m: m.text == "Связаться с нами")
async def contact_info(message: types.Message):
    await message.answer("📩 Почта: abc123321@gmail.com\n📞 Телефон: +7 999 999 99 99")

user_data = {}

@dp.message_handler(lambda m: m.text == "Оставить заявку")
async def request_name(message: types.Message):
    await message.answer("Пожалуйста, укажите ваше имя:")
    user_data[message.from_user.id] = {}
    dp.register_message_handler(get_name, lambda m: True, state=None, content_types=types.ContentTypes.TEXT)

async def get_name(message: types.Message):
    user_data[message.from_user.id]['name'] = message.text
    await message.answer("Спасибо. Теперь введите номер телефона:")
    dp.register_message_handler(get_phone, lambda m: True, state=None, content_types=types.ContentTypes.TEXT)

async def get_phone(message: types.Message):
    user_data[message.from_user.id]['phone'] = message.text
    name = user_data[message.from_user.id]['name']
    phone = message.text
    await message.answer("Спасибо! Ваша заявка отправлена.")
    send_email(name, phone)
    user_data.pop(message.from_user.id, None)

def send_email(name, phone):
    msg = EmailMessage()
    msg.set_content(f"Новая заявка:\nИмя: {name}\nТелефон: {phone}")
    msg['Subject'] = 'Заявка с Telegram-бота'
    msg['From'] = EMAIL_USER
    msg['To'] = ADMIN_EMAIL
    try:
        with smtplib.SMTP_SSL('smtp.yandex.ru', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print("Ошибка отправки письма:", e)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
