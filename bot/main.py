import datetime
import logging

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

from bot.config import TG_TOKEN
from bot.config import TG_API_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("message_button_bot_main")


# callback_data -- это то, что будет присылать TG при нажатии на каждую кнопку
# Поэтому каждый идентификатор должен быть уникальным
CALLBACK_BUTTON1_PREDICT = "callback_button1_predict"
CALLBACK_BUTTON2_BEST_PREDICT = "callback_button2_best_predict"
CALLBACK_BUTTON3_HELP = "callback_button3_help"
CALLBACK_BUTTON4_RETURN = "callback_button4_return"
CALLBACK_BUTTON5_BTC = "callback_button5_btc"
CALLBACK_BUTTON6_LTC = "callback_button6_ltc"
CALLBACK_BUTTON7_ETH = "callback_button7_eth"


TITLES = {
    CALLBACK_BUTTON1_PREDICT: "Построить прогноз",
    CALLBACK_BUTTON2_BEST_PREDICT: "Показать самый выгодный",
    CALLBACK_BUTTON3_HELP: "Помощь",
    CALLBACK_BUTTON4_RETURN: "Назад",
    CALLBACK_BUTTON5_BTC: "BTC",
    CALLBACK_BUTTON6_LTC: "LTC",
    CALLBACK_BUTTON7_ETH: "ETH",
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
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON1_PREDICT], callback_data=CALLBACK_BUTTON1_PREDICT),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON2_BEST_PREDICT], callback_data=CALLBACK_BUTTON2_BEST_PREDICT)
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON3_HELP], callback_data=CALLBACK_BUTTON3_HELP)
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
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON5_BTC], callback_data=CALLBACK_BUTTON5_BTC)
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON6_LTC], callback_data=CALLBACK_BUTTON6_LTC),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON7_ETH], callback_data=CALLBACK_BUTTON7_ETH)
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON4_RETURN], callback_data=CALLBACK_BUTTON4_RETURN)
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_keyboard_return():
    """Получить кнопку назад, которая вернет к первой клавиатуре
       Возможно получить при получении прогноза и вызове помощи
    """
    keyboard = [
        # Каждый элемент внутри списка -- это вертикальный столбец.
        # Сколько кнопок, столько столбцов
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON4_RETURN], callback_data=CALLBACK_BUTTON4_RETURN)
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def keyboard_callback_handler(update: Update, chat_data=None, **kwargs):
    """Обработчик всех кнопок со всех клавиатур"""
    query = update.callback_query
    data = query.data

    if data == CALLBACK_BUTTON1_PREDICT:
        # удалим клавиатуру у прошлого сообщения
        # т.е. отредактируем сообщение так, чтобы текст остался тот же, а клавиатура пропала
        text = "Выберите интересующий Вас тип криптовалюты:"
        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_keyboard2(),
        )
    elif data == CALLBACK_BUTTON2_BEST_PREDICT:
        # Отредактируем текст сообщения, но оставим клавиатуру
        text = "Прогноз модели:\nНаходится в разработке"
        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_keyboard_return(),
        )
    elif data == CALLBACK_BUTTON3_HELP:
        # Показать следующий экран клавиатуры
        # (оставим тот же текст, но указать другой массив кнопок)
        text = "Функционал бота:\n->Показать самую выгодную для покупки криптовалюту на данный момент\n->Показать " \
               "прогноз для выбранной криптовалюты\n----------\nДанный бот разработан:\n->Проскурин Александр " \
               "Михайлович\n->Шушкова Варвара Владимировна "
        query.edit_message_text(
            text=text,
            reply_markup=get_keyboard_return(),
        )
    elif data == CALLBACK_BUTTON4_RETURN:
        # Показать предыдущий экран клавиатуры
        # (оставить тот же текст, но указать другой массив кнопок)
        text = "Выберите нужную функцию:"
        query.edit_message_text(
            text=text,
            reply_markup=get_base_inline_keyboard(),
        )
    elif data in (CALLBACK_BUTTON5_BTC, CALLBACK_BUTTON6_LTC, CALLBACK_BUTTON7_ETH):
        pair = {
            CALLBACK_BUTTON5_BTC: "USD-BTC",
            CALLBACK_BUTTON6_LTC: "USD-LTC",
            CALLBACK_BUTTON7_ETH: "USD-ETH",
        }[data]

        # try:
        #     current_price = client.get_last_price(pair=pair)
        #     text = f"*Курс валюты:*\n\n*{pair}* = {current_price}$"
        # except BittrexError:
        #     text = "Произошла ошибка!\n\nПопробуйте еще раз позднее."
        text = "Данный раздел находится в разработке"
        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_keyboard2(),
        )
    else:
        update.message.reply_text(
            text="Ошибка!\nНеизвестное действие пользователя!\nОбратитесь к администратору!"
        )


def do_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Привет!\nВыберите нужную функцию:",
        reply_markup=get_base_inline_keyboard(),
    )


def do_echo(update: Update, context: CallbackContext):
    text = f"Извините, но команда\n'{update.message.text}'\nНе найдена\n----------\nВыберите команду из " \
           f"представленных ниже "
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
        token=TG_TOKEN,
        base_url=TG_API_URL,
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
