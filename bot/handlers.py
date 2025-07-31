from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.database import get_session
from bot.models import User, Card, UserCard
from bot.keyboards import main_menu, cards_menu, card_details
from datetime import datetime, timedelta
from random import choice

router = Router()

class CardStates(StatesGroup):
    SELECT_RARITY = State()
    SELECT_CARD = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    session = get_session()
    user = session.query(User).filter_by(id=message.from_user.id).first()
    if not user:
        user = User(id=message.from_user.id, username=message.from_user.username)
        session.add(user)
        session.commit()
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=main_menu())

@router.message(F.text == "Получить карточку")
async def get_card(message: Message):
    session = get_session()
    user = session.query(User).filter_by(id=message.from_user.id).first()
    now = datetime.utcnow()
    
    if user.last_card_received and (now - user.last_card_received) < timedelta(hours=12):
        await message.answer("Вы сможете получить новую карточку позже!")
        return
    
    cards = session.query(Card).all()
    if not cards:
        await message.answer("Карточки пока не добавлены!")
        return
    
    random_card = choice(cards)
    user_card = UserCard(user_id=user.id, card_id=random_card.id)
    user.points += random_card.points
    user.last_card_received = now
    
    if user.points >= 1000:
        user.title = "Гуру"
    elif user.points >= 500:
        user.title = "Профи"
    
    session.add(user_card)
    session.commit()
    
    await message.answer(f"Вы получили карточку: {random_card.name} ({random_card.rarity})!")

@router.message(F.text == "Мои карточки")
async def my_cards(message: Message, state: FSMContext):
    await message.answer("Выберите категорию:", reply_markup=cards_menu())
    await state.set_state(CardStates.SELECT_RARITY)

@router.callback_query(CardStates.SELECT_RARITY)
async def select_rarity(callback: CallbackQuery, state: FSMContext):
    rarity = callback.data
    session = get_session()
    user_cards = session.query(UserCard).join(Card).filter(
        UserCard.user_id == callback.from_user.id,
        Card.rarity == rarity
    ).all()
    
    if not user_cards:
        await callback.message.answer("У вас нет карточек этой редкости!")
        return
    
    cards = {uc.card.name: uc.card_id for uc in user_cards}
    await callback.message.answer("Выберите карточку:", reply_markup=card_details(cards, rarity))
    await state.set_state(CardStates.SELECT_CARD)
    await callback.answer()

@router.callback_query(CardStates.SELECT_CARD, F.data.startswith("card_"))
async def show_card(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data.split("_")[1])
    session = get_session()
    
    user_card = session.query(UserCard).filter_by(
        user_id=callback.from_user.id,
        card_id=card_id
    ).first()
    
    if not user_card:
        await callback.message.answer("Эта карточка вам не принадлежит!")
        return
    
    card = session.query(Card).get(card_id)
    caption = f"{card.name}\n{card.description}\nОчки: {card.points}\nРедкость: {card.rarity}"
    await callback.message.answer_photo(
        photo=card.image_url,
        caption=caption,
        reply_markup=card_details({"favorite": card_id}, card.rarity, user_card.is_favorite)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("favorite_"))
async def toggle_favorite(callback: CallbackQuery):
    card_id = int(callback.data.split("_")[1])
    session = get_session()
    user_card = session.query(UserCard).filter_by(
        user_id=callback.from_user.id,
        card_id=card_id
    ).first()
    
    if user_card:
        user_card.is_favorite = not user_card.is_favorite
        session.commit()
        await callback.message.answer("Статус избранного обновлён!")
    await callback.answer()

@router.message(F.text == "Профиль")
async def profile(message: Message):
    session = get_session()
    user = session.query(User).filter_by(id=message.from_user.id).first()
    card_count = session.query(UserCard).filter_by(user_id=user.id).count()
    await message.answer(
        f"Имя: {user.username}\n"
        f"Карточек: {card_count}\n"
        f"Очки: {user.points}\n"
        f"Титул: {user.title}",
        reply_markup=main_menu()
    )

@router.message(F.text == "Топ")
async def top_players(message: Message):
    session = get_session()
    top_users = session.query(User).order_by(User.points.desc()).limit(10).all()
    text = "Топ игроков:\n"
    for i, user in enumerate(top_users, 1):
        text += f"{i}. {user.username} — {user.points} очков\n"
    await message.answer(text, reply_markup=main_menu())