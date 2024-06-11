from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

server = '100.73.16.195:1433'
database = 'DineEase'
driver = '{ODBC Driver 17 for SQL Server}'
username = 'SA'
password = 'White4Life'

# Create the engine
engine = create_engine(
    f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server",
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