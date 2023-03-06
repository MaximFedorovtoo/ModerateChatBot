import telebot
from nltk.tokenize import word_tokenize
import time
import config
import logging
import filters
from aiogram import Bot, Dispatcher, executor, types
import config as cfg
from filters import IsAdminFilter
# log level
logging.basicConfig(level=logging.INFO)

# bot init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# activate filters
dp.filters_factory.bind(IsAdminFilter)

bad_words = ['слово1', 'слово2', 'слово3']

user_rating = {}

def check_for_bad_words(text):
    words = word_tokenize(text.lower())
    for word in words:
        if word in bad_words:
            return True
    return False

def delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

def calculate_user_rating(user_id):
    if user_id not in user_rating:
        user_rating[user_id] = 0
    return user_rating[user_id]

def ban_user(user_id):
    bot.kick_chat_member(chat_id, user_id, until_date=int(time.time()) + 18000) #бан пользователя на 5 часов
    user_rating[user_id] = 0

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привет! Я телеграм-бот, который поможет тебе избежать использования ненормативной лексики в чате.")
    bot.send_message(chat_id, f"Ваш рейтинг: {calculate_user_rating(message.from_user.id)}")

@bot.message_handler(commands=['help'])
def handle_help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Я могу помочь тебе избежать использования ненормативной лексики в чате. Просто отправь мне сообщение, и я проверю его на содержание ненормативных слов. Если они будут обнаружены, я предупрежу тебя и удалю сообщение.")

@bot.message_handler(content_types=['text'])
def handle_message(message):
    chat_id = message.chat.id
    message_id = message.message_id
    user_id = message.from_user.id
    text = message.text
    if check_for_bad_words(text):
        bot.reply_to(message, 'Предупреждение: в вашем сообщении была использована ненормативная лексика')
        delete_message(chat_id, message_id)
        user_rating[user_id] += 1
        if user_rating[user_id] >= 3: #если пользователь использует ненормативную лексику более 3 раз, бот банит его на 5 часов
            ban_user(user_id)
    bot.send_message(chat_id, f"Ваш рейтинг: {calculate_user_rating(user_id)}")

@bot.message_handler(func=lambda message: True, content_types=['new_chat_members'])
def handle_new_member(message):
    chat_id = message.chat.id
    new_members = message.new_chat_members
    for member in new_members:
        bot.send_message(chat_id, f"Добро пожаловать в чат, {member.first_name}! Я помогу тебе избежать использования ненормативной лексики в сообщениях.")

if __name__ == '__main__':
    bot.polling(none_stop=True)



