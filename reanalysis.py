import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

from datetime import datetime, timedelta
from database.tables import Stocks, Watchlist

import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datetime import datetime

import time

def create_database_session():
    database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

def create_timestamp(row):
    date_string = f"{row.year}-{row.month}-{row.day} {row.hour}:{row.minute}"
    date_object = datetime.strptime(date_string, "%Y-%m-%d %H:%M")

    return date_object


def recreate_model(df):
    X = df[['hour', 'minute', 'day', 'month', 'year']]
    y = df[['actual']]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')

    return model

session = create_database_session()

transactions = session.query(Stocks).filter(
    Stocks.stock_id == "TCS:NSE"    
).order_by(Stocks.day, Stocks.hour, Stocks.minute).all()

session.close()

query = f"SELECT hour, minute, day, month, year, actual, predicted FROM stocks WHERE stock_id = 'TCS:NSE' AND actual != 0.0 ORDER BY day, month, hour, minute"

database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
engine = create_engine(database_url)
df = pd.read_sql(query, engine)
epochs = (df.shape)[0]

for i in range(180, (epochs + 1)):
    database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
    engine = create_engine(database_url)
    df = pd.read_sql(query, engine)

    newdf = df.iloc[0:i]
    next_row = df.iloc[i]

    new_data = {
            'hour': next_row.hour,
            'minute': next_row.minute,
            'day': next_row.day,
            'month': next_row.month,
            'year': next_row.year
        }

    model = recreate_model(newdf)
    new_features_df = pd.DataFrame([new_data])
    prediction = model.predict(new_features_df)

    session = create_database_session()

    transaction = session.query(Stocks).filter(
        Stocks.stock_id == "TCS:NSE",
        Stocks.day == next_row.day,
        Stocks.month == next_row.month,
        Stocks.year == next_row.year,
        Stocks.hour == next_row.hour,
        Stocks.minute == next_row.minute
    ).first()

    transaction.predicted = prediction[0][0]

    session.commit()

    print(f"Epoch {i}/{epochs}:\nActual: {transaction.actual}\nPrediction: {prediction[0][0]}")

    time.sleep(2)