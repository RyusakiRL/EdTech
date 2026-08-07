"""Create a database session and return the security connection"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

URL_DATA = os.getenv("DATABASE_URL")
engine = create_engine(URL_DATA, echo=False)

SESSIONLOCAL = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Return the connection of security form using yield and finally"""
    db = SESSIONLOCAL()
    try:
        yield db
    finally:
        db.close()
