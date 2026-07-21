"""Funcoes do sistema"""

import shutil
from pathlib import Path
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from models import Curso, Matricula, Usuario, Aula
from schemas import CursosValidar, UsuarioValidar
from security import verificar_senha, gerar_hash_senha
from security import criar_token_jwt

PASTA_UPLOADS = Path("uploads")

PASTA_UPLOADS.mkdir(exist_ok=True)


def create_students(student: UsuarioValidar, db: Session):
    """Allow peoples for create a student to acess the courses"""
    student_existance = (
        db.query(Usuario).filter(Usuario.nome_user == student.nome_user).first()
    )
    if student_existance:
        raise HTTPException(
            status_code=400, detail="Name already exists; please enter another one."
        )
    password_cript = gerar_hash_senha(student.senha)
    new_student = Usuario(
        nome_user=student.nome_user, senha=password_cript, cargo="estudante"
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {"message": "Welcome to our platform."}


def create_instructor(instructor: UsuarioValidar, login_confirmation: str, db: Session):
    """Create a instructor route, responsability of this role: manage grades, progress and courses"""
    name_validation_admnistrator = (
        db.query(Usuario).filter(Usuario.nome_user == login_confirmation).first()
    )
    if not name_validation_admnistrator:
        raise HTTPException(status_code=404, detail="Administrator not encountered")
    if name_validation_admnistrator.cargo != "administrador":
        raise HTTPException(
            status_code=403,
            detail="Acess denied: only admnistrator can create instructors on plataform",
        )

    instructor_existence = (
        db.query(Usuario).filter(Usuario.nome_user == instructor.nome_user).first()
    )
    if instructor_existence:
        raise HTTPException(status_code=400, detail="Name already exists: insert other")
    encrypted_password = gerar_hash_senha(instructor.senha)
    new_instructor = Usuario(
        nome_user=instructor.nome_user, senha=encrypted_password, cargo="instrutor"
    )
    db.add(new_instructor)
    db.commit()
    db.refresh(new_instructor)
    return {"message": "Welcome to the new instructor"}


def login(db: Session, username: str, senha: str):
    """Login in system and return the token"""
    existencia = db.query(Usuario).filter(Usuario.nome_user == username).first()
    if not existencia:
        raise HTTPException(status_code=404, detail="Credencial invalida")
    senha_verificada = verificar_senha(senha, existencia.senha)
    if not senha_verificada:
        raise HTTPException(status_code=400, detail="Credencial invalida")
    token = criar_token_jwt({"sub": existencia.nome_user})
    return {"access_token": token, "token_type": "bearer"}


def create_course(confirmacao_login: str, db: Session, dados_curso: CursosValidar):
    """The instructor can create a course, and block others roles to create a course"""
    validacao_nome_instrutor = (
        db.query(Usuario).filter(Usuario.nome_user == confirmacao_login).first()
    )
    if not validacao_nome_instrutor:
        raise HTTPException(status_code=404, detail="Instrutor nao encontrado")
    if not validacao_nome_instrutor.cargo == "instrutor":
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: apenas instrutores podem criar cursos",
        )
    novo_curso = Curso(
        titulo=dados_curso.titulo,
        descricao=dados_curso.descricao,
        id_instrutor=validacao_nome_instrutor.id,
    )
    db.add(novo_curso)
    db.commit()
    db.refresh(novo_curso)
    return {"mensagem": "Curso criado com sucesso"}


def create_registration(confirmacao_login: str, curso_nome: str, db: Session):
    """Enable students to enroll in existing courses."""
    existencia_estudante = (
        db.query(Usuario).filter(Usuario.nome_user == confirmacao_login).first()
    )
    if not existencia_estudante:
        raise HTTPException(
            status_code=403,
            detail="Estudante nao encontrado",
        )
    if not existencia_estudante.cargo == "estudante":
        raise HTTPException(
            status_code=403,
            detail="Apenas estudantes sao autorizados a se cadastrar em uma aula",
        )

    existencia_curso = db.query(Curso).filter(Curso.titulo == curso_nome).first()
    if not existencia_curso:
        raise HTTPException(status_code=404, detail="Curso nao encontrado")
    ja_matriculado = (
        db.query(Matricula)
        .filter(
            Matricula.id_aluno == existencia_estudante.id,
            Matricula.id_curso == existencia_curso.id,
        )
        .first()
    )
    if ja_matriculado:
        raise HTTPException(
            status_code=403,
            detail="Estudante ja matriculado nessa aula",
        )
    nova_matricula = Matricula(
        id_aluno=existencia_estudante.id, id_curso=existencia_curso.id
    )

    db.add(nova_matricula)
    db.commit()
    db.refresh(nova_matricula)
    return {"mensagem": "Matricula realizada com sucesso"}


def list_courses(db: Session):
    """Lists the courses for each teacher"""
    cursos_de_cada_instrutor = (
        db.query(Curso).options(joinedload(Curso.instrutor)).all()
    )

    return cursos_de_cada_instrutor


def add_class_course(
    db: Session, curso_id: int, titulo_aula: str, arquive: UploadFile, nome_usuario: str
):
    """Uploads the file and links it to a course in the database."""
    instrutor_logado = (
        db.query(Usuario).filter(Usuario.nome_user == nome_usuario).first()
    )

    if not instrutor_logado or instrutor_logado.cargo != "instrutor":
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: apenas instrutores",
        )
    curso_alvo = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso_alvo:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: curso inexistente",
        )
    if curso_alvo.id_instrutor != instrutor_logado.id:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: Você não é o dono deste curso",
        )
    caminho_destino = PASTA_UPLOADS / arquive.filename
    with caminho_destino.open("wb") as buffer:
        shutil.copyfileobj(arquive.file, buffer)

    nova_aula = Aula(
        titulo=titulo_aula,
        caminho_arquivo=str(caminho_destino),
        id_curso=curso_alvo.id,
    )
    db.add(nova_aula)
    db.commit()
    db.refresh(nova_aula)
    return {"mensagem": f"Aula '{titulo_aula}' adicionada com sucesso ao curso!"}


def list_course_classes(db: Session, curso_id: int):
    """
    65
    Returns the list of lessons in JSON format linked to a specific course."""
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(
            status_code=403,
            detail="Nenhum curso encontrado",
        )
    aulas = db.query(Aula).filter(Aula.id_curso == curso_id).all()
    return aulas


def download_file_of_class(db: Session, aula_id: int):
    """Returns the file for viewing/downloading."""
    aula = db.query(Aula).filter(Aula.id == aula_id).first()
    if not aula:
        raise HTTPException(
            status_code=403,
            detail="Aula nao encontrada",
        )
    caminho_arquivo = Path(aula.caminho_arquivo)
    if not caminho_arquivo.exists():
        raise HTTPException(
            status_code=404, detail="O arquivo físico nao existe/sumiu do servidor"
        )

    return FileResponse(
        path=caminho_arquivo, filename=aula.titulo + caminho_arquivo.suffix
    )
