from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура выбора режима анализа
def get_mode_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Анализ тональности"),
                KeyboardButton(text="😊 Анализ эмоций")
            ],
            [
                KeyboardButton(text="ℹ️ Помощь")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard