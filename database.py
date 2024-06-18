from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
driver = '{ODBC Driver 17 for SQL Server}'
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

engine = create_engine(
    f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server",
    fast_executemany=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    db_session = SessionLocal()
    try:
        yield db_session
        db_session.commit()
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()

Base = declarative_base()

def recreate_database():
    """Drop all tables and recreate them."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

