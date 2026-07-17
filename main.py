"""Liga o sistema a API"""

from typing import List
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
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


@app.get("/", include_in_schema=False)
def root():
    """Connects the system in a Render"""
    return RedirectResponse(url="/docs")


@app.post("/login")
def login_route(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """Rota de login do sistema"""
    login_name = form_data.username
    login_password = form_data.password
    return login(db=db, username=login_name, senha=login_password)


PASTA_UPLOADS = Path("uploads")

PASTA_UPLOADS.mkdir(exist_ok=True)


@app.post("/cursos/{curso_id}/aulas")
def receive_files_endpoint(
    course_id: int,
    class_title: str = Form(...),
    file_upload: UploadFile = File(...),
    username_login: str = Depends(verificar_token),
    db: Session = Depends(get_db),
):
    """Recebe os arquivos em uma pasta chamada upload"""

    return adicionar_aula_curso(
        db=db,
        arquive=file_upload,
        curso_id=course_id,
        nome_usuario=username_login,
        titulo_aula=class_title,
    )


@app.post("/registro/aluno")
def create_student_endpoint(
    student_register: UsuarioValidar, db: Session = Depends(get_db)
):
    """Rota publica para registro de estudantes"""

    return criar_estudante(db=db, estudante=student_register)


@app.post("/registro/instrutor")
def create_instructor_endpoint(
    register_of_instructor: UsuarioValidar,
    username_login: str = Depends(verificar_token),
    db: Session = Depends(get_db),
):
    """Rota privada para admnistradores registrarem novos instrutores para o site"""
    return criar_instrutor(
        instrutor=register_of_instructor, confirmacao_login=username_login, db=db
    )


@app.post("/registro/curso")
def create_course_endpoint(
    registration_course: CursosValidar,
    username_login: str = Depends(verificar_token),
    db: Session = Depends(get_db),
):
    """Rota privada a qual apenas o instrutor pode criar o curso"""

    return criar_curso(
        confirmacao_login=username_login, dados_curso=registration_course, db=db
    )


@app.get("/curso/matricula")
def create_registration_endpoint(
    course_name: str,
    db: Session = Depends(get_db),
    username_login: str = Depends(verificar_token),
):
    """Rota privada para estudantes  para registrar a matricula em alguma aula"""

    return criar_matricula(
        confirmacao_login=username_login, curso_nome=course_name, db=db
    )


@app.get("/curso/lista", response_model=List[ModelResponseCursos])
def list_courses_endpoint(db: Session = Depends(get_db)):
    """Lista os cursos disponiveis"""
    return listar_cursos(db=db)


@app.get("/cursos/{curso_id}/aulas")
def list_classes_endpoint(course_id: int, db: Session = Depends(get_db)):
    """Lista as aulas em formato JSON"""
    return listar_aulas_do_curso(db=db, curso_id=course_id)


@app.get("/aulas/{aula_id}/download")
def download_class_endpoint(
    class_id: int,
    db: Session = Depends(get_db),
    login_str: str = Depends(verificar_token),
):
    """Rota privada: o aluno precisa estar logado para baixar o arquivo da aula"""
    return baixar_arquivo_aula(aula_id=class_id, db=db)
