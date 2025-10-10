from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_url = 'postgresql//stock:Welcome123$@localhost:5432/stocks_db'
engine = create_engine(database_url)

def create_database_session():
    Session = sessionmaker(bind=engine)
    session = Session()

    return session
