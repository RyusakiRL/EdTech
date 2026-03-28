"""Cria a Sessao do banco de dados e retorna a conexao de forma segura"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

URL_DATA = "sqlite:///cursos_gerenciamento.db"
engine = create_engine(URL_DATA, echo=False, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Retornar a conexao de forma segura com o yield e finally"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
