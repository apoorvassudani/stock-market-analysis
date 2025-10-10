import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

import requests
from bs4 import BeautifulSoup

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

from datetime import datetime, timedelta, date
from database.tables import Stocks, Watchlist

import time
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from csv import writer

from github import Github

time_list = [
    "09:15",
    "09:30",
    "09:45",
    "10:00",
    "10:15",
    "10:30",
    "10:45",
    "10:51",
    "11:00",
    "11:15",
    "11:30",
    "11:45",
    "12:00",
    "12:15",
    "12:30",
    "12:43",
    "12:45",
    "12:52",
    "13:00",
    "13:15",
    "13:30",
    "13:45",
    "14:00",
    "14:15",
    "14:30",
    "14:45",
    "15:00",
    "15:15",
    "15:30"
]

def push_files():
    token = "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"
    g = Github(token)
    repo = g.get_repo("nirajitpramanik/stock-data")

    files = [
        'BHARTIARTL_NSE.html',
        'index.html',
        'INFY_NSE.html',
        'NIFTY_50_INDEXNSE.html',
        'SENSEX_INDEXBOM.html',
        'TCS_NSE.html',
        'AXISBANK_NSE.html',
        'ICICIBANK_NSE.html',
        'HDFCBANK_NSE.html',
        'RELIANCE_NSE.html',
        'SBIN_NSE.html'
    ]
        
    for filename in files:
        file_path = f"./website/{filename}"
        
        with open(file_path, 'r') as file:
            content = file.read()

        github_path = filename
        
        try:
            existing_file = repo.get_contents(github_path)
            repo.update_file(existing_file.path, f"Updated stock data at {datetime.now().hour}:{datetime.now().minute}", content, existing_file.sha)
        except Exception as e:
            repo.create_file(github_path, f"Added stock data at {datetime.now().hour}:{datetime.now().minute}", content)

def create_database_session():
    database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

def scrape_data():
    session = create_database_session()
    watch = session.query(Watchlist).all()
    session.close()

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

def generate_webpage(stock):
    f = open('./website/template.txt', 'r')
    template = f.read()

    table_data = ""

    for stamp in time_list:
        hour, minute = [int(x) for x in stamp.split(":")]
        session = create_database_session()

        try:
            stock_data = session.query(Stocks).filter(
                Stocks.stock_id == stock,
                Stocks.hour == hour,
                Stocks.minute == minute,
                Stocks.day == datetime.now().day,
                Stocks.month == datetime.now().month,
                Stocks.year == datetime.now().year
            ).first()

            table_data += f"<tr><td>{stamp}</td><td>{round(stock_data.actual, 2)}</td><td>{round(stock_data.predicted, 2)}</td><td>{round(stock_data.quarterly_prediction, 2)}</td>"
        except:
            pass

        session.close()

    table_data += '''
</tbody>
        </table>
    </center>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  </body>
</html>
    '''

    template += table_data

    filename = stock.replace(":", "_")
    webpage = open(f'./website/{filename}.html', 'w')
    webpage.write(template)
    webpage.close()

    return True


def current_and_future_times():
    current_time = datetime.now().strftime("%H:%M")
    print(current_time)

    for i in range(len(time_list)):
        if time_list[i] == current_time:
            return (True, time_list[i+1:], time_list[i])
        
    return False

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

if __name__ == "__main__":
    while True:
        flag = current_and_future_times()

        if flag:
            scrape_data()
            hours, minutes = flag[2].split(":")
            csv_data = [["Stock Name", f"Current ({datetime.now().hour}:{datetime.now().minute})"] + flag[1]]

            session = create_database_session()
            stocks = session.query(Watchlist).all()
            session.close()

            for stock_data in stocks:
                model = recreate_model(stock_data.stock_id)

                sname = stock_data.stock_name
                sub = [sname]

                def preprocess_timestamp(timestamp):
                    dt = timestamp
                    
                    return {
                        'hour': dt.hour,
                        'minute': dt.minute,
                        'day': dt.day,
                        'month': dt.month,
                        'year': dt.year
                    }

                session = create_database_session()

                existing = session.query(Stocks).filter(
                    Stocks.stock_id == f'{stock_data.stock_id}',
                    Stocks.hour == hours,
                    Stocks.minute == minutes
                ).first()

                session.close()

                sub.append(existing.actual)

                for timestamp in flag[1]:
                    timestamp = datetime.strptime(f"{date.today()} {timestamp}", "%Y-%m-%d %H:%M")
                    new_features = preprocess_timestamp(timestamp)
                    new_features_df = pd.DataFrame([new_features])
                    predicted_value = model.predict(new_features_df)

                    session = create_database_session()

                    existing = session.query(Stocks).filter(
                        Stocks.stock_id==f'{stock_data.stock_id}',
                        Stocks.hour == timestamp.hour,
                        Stocks.minute == timestamp.minute,
                        Stocks.day == timestamp.day,
                        Stocks.month == timestamp.month,
                        Stocks.year == timestamp.year,
                    ).first()

                    if existing:
                        existing.quarterly_prediction = predicted_value[0][0]

                    else:
                        session.add(
                            Stocks(
                                stock_id=f'{stock_data.stock_id}',
                                hour = timestamp.hour,
                                minute = timestamp.minute,
                                day = timestamp.day,
                                month = timestamp.month,
                                year = timestamp.year,
                                actual = 0.0,
                                predicted = 0.0,
                                quarterly_prediction = predicted_value[0][0]
                            )
                        )

                    session.commit()
                    session.close()

                    sub.append(predicted_value[0][0])

                generate_webpage(stock_data.stock_id)

                csv_data.append(sub)

            try:
                f = open(f'./predictions/{date.today()}/{datetime.now().hour}.{datetime.now().minute}.csv', 'w')
            except:
                os.mkdir(f'./predictions/{date.today()}')
                f = open(f'./predictions/{date.today()}/{datetime.now().hour}.{datetime.now().minute}.csv', 'w')

            data_writer = writer(f)

            data_writer.writerows(csv_data)

            f.close()
            #push_files()
            print(f'Predicted values and added files - {datetime.now()}')

        time.sleep(30)