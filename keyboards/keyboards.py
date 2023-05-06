from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def start_kb():
    button_1: KeyboardButton = KeyboardButton(text='Создать свзяь')
    button_2: KeyboardButton = KeyboardButton(text='Моя свзяь')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1, button_2]],
                                   resize_keyboard=True)
    return keyboard


def cancel_kb():
    button_1: KeyboardButton = KeyboardButton(text='Отмена')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]], resize_keyboard=True)
    return keyboard


def forward_kb():
    button_1 = InlineKeyboardButton(text='Да',
                                    callback_data='yes_forwarding')
    button_2 = InlineKeyboardButton(text='Нет',
                                    callback_data='no_forwarding')
    keyboard: list[list[InlineKeyboardButton]] = [[button_1, button_2]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def forward_start_kb():
    button_1 = InlineKeyboardButton(text='🟢Запустить',
                                    callback_data='forward_start')
    button_2 = InlineKeyboardButton(text='📝Изменить',
                                    callback_data='update_link')
    button_3 = InlineKeyboardButton(text='❌Удалить',
                                    callback_data='delete_link')
    keyboard: list[list[InlineKeyboardButton]] = [[button_1], [button_2, button_3]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def forward_stop_kb():
    button_1 = InlineKeyboardButton(text='🔴Остановить',
                                    callback_data='forward_stop')
    button_2 = InlineKeyboardButton(text='📝Изменить',
                                    callback_data='update_link')
    button_3 = InlineKeyboardButton(text='❌Удалить',
                                    callback_data='delete_link')
    keyboard: list[list[InlineKeyboardButton]] = [[button_1], [button_2, button_3]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def test_stop_kb():
    button_1: KeyboardButton = KeyboardButton(text='🟢Запустить')
    button_2: KeyboardButton = KeyboardButton(text='🔴Остановить')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1, button_2]],
                                   resize_keyboard=True)
    return keyboard
