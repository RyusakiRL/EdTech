import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db
from models import Base

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


# --- OS TESTES REAIS ---


def test_criar_estudante_com_sucesso():
    """Garante que a rota pública de registro de alunos funciona"""
    dados_aluno = {"nome_user": "aluno_teste", "senha": "senha_segura_123"}

    # Simula um disparo de POST na sua rota
    resposta = client.post("/registro/aluno", json=dados_aluno)

    # Validações (Asserts)
    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Seja bem vindo a nossa plataforma"}


def test_impedir_estudante_de_criar_curso():
    """Garante que a trava de segurança (RBAC) bloqueia quem não é instrutor"""
    # 1. Primeiro criamos um aluno
    client.post(
        "/registro/aluno", json={"nome_user": "estudante_invasor", "senha": "123"}
    )

    # 2. Pegamos o token dele fazendo login
    resposta_login = client.post(
        "/login", data={"username": "estudante_invasor", "password": "123"}
    )
    token = resposta_login.json()["access_token"]

    # 3. Tentamos criar um curso usando o cabeçalho de segurança (Token) desse aluno
    dados_curso = {"titulo": "Curso Hacker", "descricao": "Tentando burlar o sistema"}

    headers = {"Authorization": f"Bearer {token}"}
    resposta_curso = client.post("/registro/curso", json=dados_curso, headers=headers)

    # Validação de Ouro: O sistema TEM que dar erro 403 (Acesso Negado)
    assert resposta_curso.status_code == 403
