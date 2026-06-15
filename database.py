"""Cria a Sessao do banco de dados e retorna a conexao de forma segura"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

URL_DATA = os.getenv("DATABASE_URL")
engine = create_engine(URL_DATA, echo=False)

SESSIONLOCAL = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Retornar a conexao de forma segura com o yield e finally"""
    db = SESSIONLOCAL()
    try:
        yield db
    finally:
        db.close()
