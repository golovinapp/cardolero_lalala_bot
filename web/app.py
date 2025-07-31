from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from bot.database import get_session
from bot.models import Card
from dotenv import load_dotenv
import os
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

UPLOAD_FOLDER = 'web/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def check_auth():
    password = request.form.get('password')
    expected_password = os.getenv('ADMIN_PASSWORD')
    if password and password == expected_password:
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
        image = request.files.get('image')
        
        if not all([name, description, points, rarity, image]):
            flash("Все поля, включая изображение, обязательны! 📷")
        elif not points.isdigit():
            flash("Очки должны быть числом! 🔢")
        else:
            if image:
                filename = f"{uuid.uuid4()}.{image.filename.split('.')[-1]}"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                image_url = f"/static/images/{filename}"
            else:
                image_url = ""
            
            card = Card(
                name=name,
                description=description,
                points=int(points),
                rarity=rarity,
                image_url=image_url
            )
            session.add(card)
            session.commit()
            flash("Карточка добавлена! 🎉")
    
    return render_template('cards.html', cards=cards, page=page, total_pages=(total_cards+per_page-1)//per_page)

@app.route('/card/<int:card_id>/delete', methods=['POST'])
def delete_card(card_id):
    session = get_session()
    card = session.query(Card).get(card_id)
    if card:
        if card.image_url and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], card.image_url.split('/')[-1])):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], card.image_url.split('/')[-1]))
        session.delete(card)
        session.commit()
        flash("Карточка удалена! 🗑️")
    return redirect(url_for('cards', page=request.args.get('page', 1)))

@app.route('/card/<int:card_id>/edit', methods=['GET', 'POST'])
def edit_card(card_id):
    session = get_session()
    card = session.query(Card).get(card_id)
    if not card:
        flash("Карточка не найдена!")
        return redirect(url_for('cards'))
    
    page = int(request.args.get('page', 1))  # Передача текущей страницы
    if request.method == 'POST':
        card.name = request.form.get('name')
        card.description = request.form.get('description')
        card.points = int(request.form.get('points'))
        card.rarity = request.form.get('rarity')
        image = request.files.get('image')
        if image:
            if card.image_url and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], card.image_url.split('/')[-1])):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], card.image_url.split('/')[-1]))
            filename = f"{uuid.uuid4()}.{image.filename.split('.')[-1]}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            card.image_url = f"/static/images/{filename}"
        session.commit()
        flash("Карточка обновлена! ✨")
        return redirect(url_for('cards', page=page))
    return render_template('cards.html', card=card, page=page)

@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)