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

def create_database_session():
    database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

def recreate_model(stock):
    query = f"SELECT hour, minute, day, month, year, actual FROM stocks WHERE stock_id = '{stock}' AND actual != 0.0"

    database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
    engine = create_engine(database_url)
    df = pd.read_sql(query, engine)

    X = df[['hour', 'minute', 'day', 'month', 'year']]
    y = df[['actual']]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')

    return model

while True:
    session = create_database_session()

    stocks = session.query(Watchlist).all()

    for stock_data in stocks:
        model = recreate_model(stock_data.stock_id)
        timestamp = datetime.now() + timedelta(minutes=1)

        sname = stock_data.stock_name

        def preprocess_timestamp(timestamp):
            dt = timestamp
            
            return {
                'hour': dt.hour,
                'minute': dt.minute,
                'day': dt.day,
                'month': dt.month,
                'year': dt.year
            }

        new_features = preprocess_timestamp(timestamp)
        new_features_df = pd.DataFrame([new_features])
        predicted_value = model.predict(new_features_df)

        existing = session.query(Stocks).filter(
            Stocks.stock_id == f'{stock_data.stock_id}',
            Stocks.hour == new_features['hour'],
            Stocks.minute == new_features['minute'],
            Stocks.day == new_features['day'],
            Stocks.month == new_features['month'],
            Stocks.year == new_features['year']
        ).first()

        if existing is not None:
            existing.predicted = predicted_value[0][0]

        else:
            session.add(
                Stocks(
                    stock_id=f'{stock_data.stock_id}',
                    hour = new_features['hour'],
                    minute = new_features['minute'],
                    day = new_features['day'],
                    month = new_features['month'],
                    year = new_features['year'],
                    actual = 0,
                    predicted = predicted_value[0][0]
                )
            )

        print(f'Predicted value for {sname} at {timestamp}: {predicted_value[0][0]}')
        session.commit()
    
    session.close()
    time.sleep(60)