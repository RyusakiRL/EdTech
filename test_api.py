"""System tests"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db
from models import Base, User, Status

# 1. Criamos um banco de dados temporário em memória para o teste (SQLite)
# Assim não mexemos no seu PostgreSQL do Docker!
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 2. Criamos uma "injeção de dependência" temporária para a API usar esse banco
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Avisamos o FastAPI para trocar o banco real pelo banco de teste durante os testes
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Cria as tabelas antes de cada teste e deleta depois (Limpeza automática)"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_deny_user_creation_without_perm(setup_database):
    """Prevents anyone other than an administrator from creating a manager"""
    db = TestingSessionLocal()
    normal_employee = User(
        name_user="Operador Teste",
        my_number="123456789012",
        role_user=Status.OPERATOR,
        is_active=True,
    )
    db.add(normal_employee)
    db.commit()
    db.close()

    new_manager_data = {
        "name_user": "New Manager",
        "password_user": "senhaforte123",
        "my_number": "999888777666",
    }

    response = client.post(
        "/users/manager/create?login_confirmation=123456789012", json=new_manager_data
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Access denied: only administrator can create managers on plataform"
    )
