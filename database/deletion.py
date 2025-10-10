from tables import Stocks, Watchlist

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datetime import datetime

import json

database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
engine = create_engine(database_url)

def create_database_session():
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

session = create_database_session()

data = session.query(Stocks).all()

for stock in data:
    if (stock.day in [8, 9]) or (stock.day == 10 and stock.hour < 14):
        to_delete = session.query(Stocks).filter(Stocks.id == stock.id).first()
        session.delete(to_delete)
        session.commit()

print("Complete!")