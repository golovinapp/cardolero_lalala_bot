from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    points = Column(Integer, default=0)
    last_card_received = Column(DateTime, nullable=True)
    title = Column(String, default="Новичок")

class Card(Base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    points = Column(Integer, nullable=False)
    rarity = Column(String, nullable=False)
    image_url = Column(String, nullable=False)

class UserCard(Base):
    __tablename__ = 'user_cards'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    card_id = Column(Integer, ForeignKey('cards.id'))
    is_favorite = Column(Boolean, default=False)
    user = relationship("User")
    card = relationship("Card")