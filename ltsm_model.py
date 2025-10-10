import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.tables import Watchlist

def create_database_session():
    database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

session = create_database_session()
stocks = session.query(Watchlist).all()
session.close()

for stock in stocks:
    query = f"SELECT hour, minute, day, month, year, actual FROM stocks WHERE stock_id = '{stock.stock_id}' AND actual != 0.0"

    database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
    engine = create_engine(database_url)
    df = pd.read_sql(query, engine)

    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute']])

    df = df.sort_values(by='datetime')

    scaler = MinMaxScaler()
    df['actual'] = scaler.fit_transform(df[['actual']])

    def create_sequences(data, time_steps=60):
        X, y = [], []
        for i in range(len(data) - time_steps):
            X.append(data[i:i + time_steps])
            y.append(data[i + time_steps])
        return np.array(X), np.array(y)

    time_steps = 60  
    X, y = create_sequences(df['actual'].values, time_steps)

    X = X.reshape((X.shape[0], X.shape[1], 1))

    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(time_steps, 1)))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.1)

    y_pred = model.predict(X_test)

    y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))
    y_pred_inv = scaler.inverse_transform(y_pred)

    mse = tf.keras.losses.MeanSquaredError()
    print(f'Mean Squared Error: {mse(y_test_inv, y_pred_inv).numpy()}')

    def predict_next_minute(model, scaler, data, time_steps=60):
        last_sequence = data[-time_steps:]
        last_sequence = last_sequence.reshape(1, time_steps, 1)
        next_minute_prediction = model.predict(last_sequence)
        return scaler.inverse_transform(next_minute_prediction)

    next_minute_prediction = predict_next_minute(model, scaler, df['actual'].values)
    print(f'Predicted value for {stock.stock_name}: {next_minute_prediction[0][0]}')
