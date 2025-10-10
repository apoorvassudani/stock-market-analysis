import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta, date
from database.tables import Stocks, Watchlist

import time
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def create_database_session():
    database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

def create_plot(df, stock, date):
    plt.figure(figsize=(10, 5))

    plt.plot(df['Timestamp'], df['Actual'], label='Actual', marker='o')

    plt.plot(df['Timestamp'], df['Predicted'], label='Predicted', marker='x')

    plt.title(f'{stock} {date}')
    plt.xlabel('Timestamp')
    plt.ylabel('Value')
    plt.legend()

    plt.xticks(rotation=45)

    plt.tight_layout()
    
    try:
        plt.savefig(f'plots/{date}/{stock}.png')
    except:
        os.mkdir(f'plots/{date}')
        plt.savefig(f'plots/{date}/{stock}.png')


if __name__ == "__main__":
    session = create_database_session()

    watchlist = session.query(Watchlist).all()

    session.close()

    day, month, year = datetime.now().day, datetime.now().month, datetime.now().year

    print(f"Average delta for {day}-{month}-{year}")

    for stock in watchlist:
        stock_id = stock.stock_id

        session = create_database_session()
        transactions = session.query(Stocks).filter(
            Stocks.stock_id == stock_id,
            Stocks.actual != 0,
            Stocks.predicted != 0,
            Stocks.day == day,
            Stocks.month == month,
            Stocks.year == year,
            Stocks.actual > 0,
            Stocks.predicted > 0
        ).order_by(Stocks.day).order_by(Stocks.hour).order_by(Stocks.minute).all()

        counter = 0
        total_delta = 0

        timestamp, actual, predicted = [], [], []

        for transaction in transactions:
            delta = transaction.actual - transaction.predicted
            total_delta += delta
            counter += 1

            timestamp.append(f'{transaction.year}-{transaction.month}-{transaction.day} {transaction.hour}:{transaction.minute}')
            actual.append(transaction.actual)
            predicted.append(transaction.predicted)

        timestamp = pd.to_datetime(timestamp)

        data = {
            'Timestamp': timestamp,
            'Actual': actual,
            'Predicted': predicted
        }

        df = pd.DataFrame(data)
        create_plot(df, stock.stock_name, date.today())
        #create_plot(df, "Infosys", date.today())

        average_delta = total_delta / counter
        #print(f"Average Delta for Infosys: {average_delta}")

        print(f"{stock.stock_name} : {round(average_delta, 2)}")
        session.close()