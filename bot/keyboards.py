from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Получить карточку"), KeyboardButton(text="Мои карточки")],
            [KeyboardButton(text="Профиль"), KeyboardButton(text="Топ")]
        ],
        resize_keyboard=True
    )

def cards_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обычные", callback_data="обычная")],
        [InlineKeyboardButton(text="Редкие", callback_data="редкая")],
        [InlineKeyboardButton(text="Избранное", callback_data="избранное")]
    ])

def card_details(cards, rarity, is_favorite=False):
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"card_{card_id}")]
        for name, card_id in cards.items()
    ]
    if "favorite" in cards:
        buttons.append([
            InlineKeyboardButton(
                text="❤️ Снять избранное" if is_favorite else "❤️ В избранное",
                callback_data=f"favorite_{cards['favorite']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="‹ Назад", callback_data=rarity)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)