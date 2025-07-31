from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from bot.database import get_session
from bot.models import Card
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

def check_auth():
    password = request.form.get('password')
    if password and check_password_hash(generate_password_hash(os.getenv('ADMIN_PASSWORD')), password):
        return True
    flash("Неверный пароль!")
    return False

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and check_auth():
        return redirect(url_for('cards'))
    return render_template('login.html')

@app.route('/cards', methods=['GET', 'POST'])
def cards():
    session = get_session()
    page = int(request.args.get('page', 1))
    per_page = 5
    cards = session.query(Card).offset((page-1)*per_page).limit(per_page).all()
    total_cards = session.query(Card).count()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        points = request.form.get('points')
        rarity = request.form.get('rarity')
        image_url = request.form.get('image_url')
        
        if not all([name, description, points, rarity, image_url]):
            flash("Все поля обязательны!")
        elif not points.isdigit():
            flash("Очки должны быть числом!")
        else:
            card = Card(
                name=name,
                description=description,
                points=int(points),
                rarity=rarity,
                image_url=image_url
            )
            session.add(card)
            session.commit()
            flash("Карточка добавлена!")
    
    return render_template('cards.html', cards=cards, page=page, total_pages=(total_cards+per_page-1)//per_page)

@app.route('/card/<int:card_id>/delete', methods=['POST'])
def delete_card(card_id):
    session = get_session()
    card = session.query(Card).get(card_id)
    if card:
        session.delete(card)
        session.commit()
        flash("Карточка удалена!")
    return redirect(url_for('cards'))

@app.route('/card/<int:card_id>/edit', methods=['GET', 'POST'])
def edit_card(card_id):
    session = get_session()
    card = session.query(Card).get(card_id)
    if request.method == 'POST':
        card.name = request.form.get('name')
        card.description = request.form.get('description')
        card.points = int(request.form.get('points'))
        card.rarity = request.form.get('rarity')
        card.image_url = request.form.get('image_url')
        session.commit()
        flash("Карточка обновлена!")
        return redirect(url_for('cards'))
    return render_template('cards.html', card=card)