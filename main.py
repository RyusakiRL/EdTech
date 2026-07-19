"""Liga o sistema a API"""

from typing import List
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from functions import (
    create_course,
    create_students,
    create_instructor,
    create_registration,
    list_courses,
    login,
    add_class_course,
    list_course_classes,
    download_file_of_class,
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
    """System route of login"""
    login_name = form_data.username
    login_password = form_data.password
    return login(db=db, username=login_name, senha=login_password)


PASTA_UPLOADS = Path("uploads")

PASTA_UPLOADS.mkdir(exist_ok=True)


@app.post("/courses/{course_id}/class")
def receive_files_endpoint(
    course_id: int,
    class_title: str = Form(...),
    file_upload: UploadFile = File(...),
    username_login: str = Depends(verificar_token),
    db: Session = Depends(get_db),
):
    """Receive the files in a past named upload"""

    return add_class_course(
        db=db,
        arquive=file_upload,
        curso_id=course_id,
        nome_usuario=username_login,
        titulo_aula=class_title,
    )


@app.post("/registration/student")
def create_student_endpoint(
    student_register: UsuarioValidar, db: Session = Depends(get_db)
):
    """Pulic route to register students"""

    return create_students(db=db, estudante=student_register)


@app.post("/registration/instructor")
def create_instructor_endpoint(
    register_of_instructor: UsuarioValidar,
    username_login: str = Depends(verificar_token),
    db: Session = Depends(get_db),
):
    """Private route for admnistrators to registry new instructors"""
    return create_instructor(
        instrutor=register_of_instructor, confirmacao_login=username_login, db=db
    )


@app.post("/registration/course")
def create_course_endpoint(
    registration_course: CursosValidar,
    username_login: str = Depends(verificar_token),
    db: Session = Depends(get_db),
):
    """Private route for only instructors create a course"""

    return create_course(
        confirmacao_login=username_login, dados_curso=registration_course, db=db
    )


@app.get("/course/registry")
def create_registration_endpoint(
    course_name: str,
    db: Session = Depends(get_db),
    username_login: str = Depends(verificar_token),
):
    """Private route for students to registry in a course"""

    return create_registration(
        confirmacao_login=username_login, curso_nome=course_name, db=db
    )


@app.get("/course/list", response_model=List[ModelResponseCursos])
def list_courses_endpoint(db: Session = Depends(get_db)):
    """List the available courses"""
    return list_courses(db=db)


@app.get("/courses/{course_id}/class")
def list_classes_endpoint(course_id: int, db: Session = Depends(get_db)):
    """List class in format JSON"""
    return list_course_classes(db=db, curso_id=course_id)


@app.get("/aulas/{aula_id}/download")
def download_class_endpoint(
    class_id: int,
    db: Session = Depends(get_db),
    login_str: str = Depends(verificar_token),
):
    """Private route: the student need to stay logged to download the files of class"""
    return download_file_of_class(aula_id=class_id, db=db)
