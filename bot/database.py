from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.models import Base

engine = create_engine('sqlite:///data.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()