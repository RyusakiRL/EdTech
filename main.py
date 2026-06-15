"""Liga o sistema a API"""

from typing import List
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from functions import (
    criar_curso,
    criar_estudante,
    criar_instrutor,
    criar_matricula,
    listar_cursos,
    login,
    adicionar_aula_curso,
    listar_aulas_do_curso,
    baixar_arquivo_aula,
)
from schemas import CursosValidar, UsuarioValidar, ModelResponseCursos
from security import verificar_token

app = FastAPI()


@app.post("/login")
def rota_login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """Rota de login do sistema"""
    nome_login = form_data.username
    senha_login = form_data.password
    return login(db=db, username=nome_login, senha=senha_login)


PASTA_UPLOADS = Path("uploads")

PASTA_UPLOADS.mkdir(exist_ok=True)


@app.post("/cursos/{curso_id}/aulas")
def receber_arquivos_endpoint(
    curso_id: int,
    titulo_aula: str = Form(...),
    arquivo_upload: UploadFile = File(...),
    username_login: str = Depends(verificar_token),
    db: Session = Depends(get_db),
):
    """Recebe os arquivos em uma pasta chamada upload"""

    return adicionar_aula_curso(
        db=db,
        arquive=arquivo_upload,
        curso_id=curso_id,
        nome_usuario=username_login,
        titulo_aula=titulo_aula,
    )


@app.post("/registro/aluno")
def criar_estudante_endpoint(
    estudante_registro: UsuarioValidar, db: Session = Depends(get_db)
):
    """Rota publica para registro de estudantes"""

    return criar_estudante(db=db, estudante=estudante_registro)


@app.post("/registro/instrutor")
def criar_instrutor_endpoint(
    instrutor_registro: UsuarioValidar,
    username_login: str = Depends(verificar_token),
    db: Session = Depends(get_db),
):
    """Rota privada para admnistradores registrarem novos instrutores para o site"""
    return criar_instrutor(
        instrutor=instrutor_registro, confirmacao_login=username_login, db=db
    )


@app.post("/registro/curso")
def criar_curso_endpoint(
    curso_registro: CursosValidar,
    username_login: str = Depends(verificar_token),
    db: Session = Depends(get_db),
):
    """Rota privada a qual apenas o instrutor pode criar o curso"""

    return criar_curso(
        confirmacao_login=username_login, dados_curso=curso_registro, db=db
    )


@app.get("/curso/matricula")
def criar_matricula_endpoint(
    nome_curso: str,
    db: Session = Depends(get_db),
    username_login: str = Depends(verificar_token),
):
    """Rota privada para estudantes  para registrar a matricula em alguma aula"""

    return criar_matricula(
        confirmacao_login=username_login, curso_nome=nome_curso, db=db
    )


@app.get("/curso/lista", response_model=List[ModelResponseCursos])
def listar_cursos_endpoint(db: Session = Depends(get_db)):
    """Lista os cursos disponiveis"""
    return listar_cursos(db=db)


@app.get("/cursos/{curso_id}/aulas")
def listar_aulas_endpoint(curso_id: int, db: Session = Depends(get_db)):
    """Lista as aulas em formato JSON"""
    return listar_aulas_do_curso(db=db, curso_id=curso_id)


@app.get("/aulas/{aula_id}/download")
def baixar_aula_endpoint(
    aula_id: int,
    db: Session = Depends(get_db),
    login_str: str = Depends(verificar_token),
):
    """Rota privada: o aluno precisa estar logado para baixar o arquivo da aula"""
    return baixar_arquivo_aula(aula_id=aula_id, db=db)
