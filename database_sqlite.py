from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

# Use SQLite for direct file-based database
engine = create_engine(
    "sqlite:///restaurant.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    db_session = SessionLocal()
    try:
        yield db_session
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        print(f"Database error: {str(e)}")
        raise
    finally:
        db_session.close()

Base = declarative_base()

def recreate_database():
    """Drop all tables and recreate them."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)