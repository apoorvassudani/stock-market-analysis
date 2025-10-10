from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

database_url = 'postgresql://stock:Welcome123$@localhost:5432/stocks_db'
engine = create_engine(database_url)

Base = declarative_base()

class Watchlist(Base):
    __tablename__ = 'watchlist'

    stock_id = Column(String, primary_key=True)
    stock_name = Column(String)

    watchlists = relationship('Stocks', back_populates='stocks')

    def __repr__(self):
        return f"<Watchlist(stock_name={self.stock_name}, stock_id={self.stock_id})>"

class Stocks(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(String, ForeignKey('watchlist.stock_id'))
    hour = Column(Integer)
    minute = Column(Integer)
    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)
    actual = Column(Float)
    predicted = Column(Float)
    quarterly_prediction = Column(Float)

    stocks = relationship('Watchlist', back_populates='watchlists')

    def __repr__(self):
        return f"<Stocks(id={self.id}, stock_id={self.stock_id}, hour={self.hour}, minute={self.minute}, day={self.day}, month={self.month}, year={self.year}, actual={self.actual}, predicted={self.predicted}, quarterly_prediction={self.quarterly_prediction})>"

Base.metadata.create_all(engine)