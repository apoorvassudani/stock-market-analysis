import requests
from bs4 import BeautifulSoup
import lxml

from datetime import datetime
import json
import time

from database.tables import Stocks, Watchlist

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
engine = create_engine(database_url)

def create_database_session():
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

session = create_database_session()
watch = session.query(Watchlist).all()
session.close()

while True:
    for stock in watch:
        session = create_database_session()
        link = f"https://www.google.com/finance/quote/{stock.stock_id}"

        soup = requests.get(link)
        stock_soup = BeautifulSoup(soup.text, 'html.parser')

        '''historical_data = infy_soup.findAll('script')[27].text

        stock_data = historical_data.split('data')[1].split('sideChannel')[0]'''

        price = float(stock_soup.find('div', {'class' : 'YMlKec fxKbKc'}).text.strip("₹").replace(",", ""))

        ts = datetime.now()
        hour = ts.hour
        minute = ts.minute
        day = ts.day
        month = ts.month
        year = ts.year
        actual = price
        predicted = 0.0

        existing = session.query(Stocks).filter(
            Stocks.stock_id == stock.stock_id,
            Stocks.hour == hour,
            Stocks.minute == minute,
            Stocks.day == day,
            Stocks.month == month,
            Stocks.year == year
        ).first()

        if existing is not None:
            existing.actual = actual
            print(f"Delta = {existing.predicted - existing.actual}")

        else:
            session.add(Stocks(
                    stock_id = stock.stock_id,
                    hour = hour,
                    minute = minute,
                    day = day,
                    month = month,
                    year = year,
                    actual = actual,
                    predicted = predicted,
                    quarterly_prediction = 0.0
            ))

        session.commit()
        
        print(f"{datetime.now()} - {stock.stock_name}")

        session.close()
        
    time.sleep(45)