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

watch = {
    'INFY:NSE' : "Infosys",
    'NIFTY_50:INDEXNSE' : "Nifty 50 (Index)",
    'SENSEX:INDEXBOM' : "Sensex (Index)",
    'TCS:NSE': "Tata Consultancy Services",
    'BHARTIARTL:NSE' : "Bharti Airtel"
}

'''for stock in watch:
    session.add(Watchlist(stock_name=watch[stock], stock_id=stock))'''

days = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}

stocks = session.query(Stocks).all()

for stock in stocks:
    if stock.day == 0:
        stock.day = 8
    elif stock.day == 1:
        stock.day = 9

    session.commit()

session.close()

'''for stock in watch:
    filename = stock.replace(":", "_")
    with open(f'stock_data/{filename}.json', "r") as fp:
        data = json.load(fp)

    for time in data:
        ts = time
        time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
        hour = time.hour
        minute = time.minute
        date = time.weekday()
        month = time.month
        year = time.year
        actual = data[ts]
        predicted = 0.0

        existing = session.query(Stocks).filter(
            Stocks.stock_id == stock,
            Stocks.hour == hour,
            Stocks.minute == minute
        ).first()

        if existing:
            existing.actual = actual

        else:
            session.add(Stocks(
                stock_id = stock,
                hour = hour,
                minute = minute,
                day = date,
                month = month,
                year = year,
                actual = actual,
                predicted = predicted
            ))

        session.commit()

    print(f"{stock} completed.")
session.close()'''