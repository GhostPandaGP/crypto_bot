import datetime
import logging
from subprocess import PIPE
from subprocess import Popen

from telegram import Bot
from telegram import Update
from telegram import ParseMode
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackQueryHandler  # обработчик события нажатия на кнопке клавиатуры
from telegram.utils.request import Request

import messageButtonBot.config as config
from messageButtonBot.bitrex import BittrexClient
from messageButtonBot.bitrex import BittrexError

client = BittrexClient()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("message_button_bot_main")


# callback_data -- это то, что будет присылать TG при нажатии на каждую кнопку
# Поэтому каждый идентификатор должен быть уникальным
CALLBACK_BUTTON1_LEFT = "callback_button1_left"
CALLBACK_BUTTON2_RIGHT = "callback_button2_right"
CALLBACK_BUTTON3_MORE = "callback_button3_more"
CALLBACK_BUTTON4_BACK = "callback_button4_back"
CALLBACK_BUTTON5_TIME = "callback_button5_time"
CALLBACK_BUTTON6_PRICE = "callback_button6_price"
CALLBACK_BUTTON7_PRICE = "callback_button7_price"
CALLBACK_BUTTON8_PRICE = "callback_button8_price"


TITLES = {
    CALLBACK_BUTTON1_LEFT: "Новое сообщение ",
    CALLBACK_BUTTON2_RIGHT: "Отредактировать",
    CALLBACK_BUTTON3_MORE: "Еще",
    CALLBACK_BUTTON4_BACK: "Назад",
    CALLBACK_BUTTON5_TIME: "Время",
    CALLBACK_BUTTON6_PRICE: "BTC",
    CALLBACK_BUTTON7_PRICE: "LTC",
    CALLBACK_BUTTON8_PRICE: "ETH",
}


def get_base_inline_keyboard():
    """Получить клавиатуру для сообщения
       Эта клавиатура будет видна под каждым сообщением, где ее прикрепили
    """
    #  Каждый список внутри 'keyboard' -- это один горизонтальный ряд кнопок
    keyboard = [
        # Каждый элемент внутри списка -- это вертикальный столбец.
        # Сколько кнопок, столько столбцов
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON1_LEFT], callback_data=CALLBACK_BUTTON1_LEFT),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON2_RIGHT], callback_data=CALLBACK_BUTTON2_RIGHT),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON3_MORE], callback_data=CALLBACK_BUTTON3_MORE)
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_keyboard2():
    """Получить вторую страницу клавиатуры для сообщений
       Возможно получить только при нажатии на первой клавиатуре
    """
    keyboard = [
        # Каждый элемент внутри списка -- это вертикальный столбец.
        # Сколько кнопок, столько столбцов
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON5_TIME], callback_data=CALLBACK_BUTTON5_TIME)
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON6_PRICE], callback_data=CALLBACK_BUTTON6_PRICE),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON7_PRICE], callback_data=CALLBACK_BUTTON7_PRICE),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON8_PRICE], callback_data=CALLBACK_BUTTON8_PRICE),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON4_BACK], callback_data=CALLBACK_BUTTON4_BACK)
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def keyboard_callback_handler(update: Update, chat_data=None, **kwargs):
    """Обработчик всех кнопок со всех клавиатур"""
    query = update.callback_query
    data = query.data
    now = datetime.datetime.now()

    # Необходимо использвовать именно effective message
    chat_id = update.effective_message.chat_id
    current_text = update.edited_message.text

    if data == CALLBACK_BUTTON1_LEFT:
        # удалим клавиатуру у прошлого сообщения
        # т.е. отредактируем сообщение так, чтобы текст остался тот же, а клавиатура пропала
        query.edit_message_text(
            text=current_text,
            parse_mode=ParseMode.MARKDOWN,
        )
        # Отправим новое сообщение при нажатии на кнопку
        update.message.reply_text(
            text="Новое сообщение\n\ncallback_query_data={}".format(data),
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON2_RIGHT:
        # Отредактируем текст сообщения, но оставим клавиатуру
        query.edit_message_text(
            text=f"Успешно отредактировано в {now}",
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON3_MORE:
        # Показать следующий экран клавиатуры
        # (оставим тот же текст, но указать другой массив кнопок)
        query.edit_message_text(
            text=current_text,
            reply_markup=get_keyboard2(),
        )
    elif data == CALLBACK_BUTTON4_BACK:
        # Показать предыдущий экран клавиатуры
        # (оставить тот же текст, но указать другой массив кнопок)
        query.edit_message_text(
            text=current_text,
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON5_TIME:
        # Покажем новый текст и оставим ту же клавиатуру
        text = f"*Точное время*\n\n{now}"
        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_keyboard2(),
        )
    elif data in (CALLBACK_BUTTON6_PRICE, CALLBACK_BUTTON7_PRICE, CALLBACK_BUTTON8_PRICE):
        pair = {
            CALLBACK_BUTTON6_PRICE: "USD-BTC",
            CALLBACK_BUTTON7_PRICE: "USD-LTC",
            CALLBACK_BUTTON8_PRICE: "USD-ETH",
        }[data]

        try:
            current_price = client.get_last_price(pair=pair)
            text = f"*Курс валюты:*\n\n*{pair}* = {current_price}$"
        except BittrexError:
            text = "Произошла ошибка!\n\nПопробуйте еще раз позднее."
        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_keyboard2(),
        )
    else:
        update.message.reply_text(
            text="Other button"
        )


def do_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Привет! Отправь мне что-нибудь!",
        reply_markup=get_base_inline_keyboard(),
    )


def do_echo(update: Update, context: CallbackContext):
    text = f"Ваше сообщение: {update.message.text}"
    update.message.reply_text(
        text=text,
        reply_markup=get_base_inline_keyboard(),
    )


def main():
    req = Request(
        connect_timeout=1,
        read_timeout=1,
    )
    bot = Bot(
        token=config.TG_TOKEN,
        base_url=config.TG_API_URL,
        request=req,
    )
    updater = Updater(
        bot=bot,
        use_context=True,
    )
    logger.info("Status bot: %s", updater.bot.get_me())

    start_handler = CommandHandler("start", do_start)
    message_handler = MessageHandler(Filters.text, do_echo)
    buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler, pass_chat_data=True)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(message_handler)
    updater.dispatcher.add_handler(buttons_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()