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


def create_students(estudante: UsuarioValidar, db: Session):
    """Permite pessoas criar um estudante para acessar os cursos"""
    existencia_estudante = (
        db.query(Usuario).filter(Usuario.nome_user == estudante.nome_user).first()
    )
    if existencia_estudante:
        raise HTTPException(status_code=400, detail="Nome ja existente, insira outro")
    senha_cript = gerar_hash_senha(estudante.senha)
    novo_estudante = Usuario(
        nome_user=estudante.nome_user, senha=senha_cript, cargo="estudante"
    )
    db.add(novo_estudante)
    db.commit()
    db.refresh(novo_estudante)
    return {"mensagem": "Seja bem vindo a nossa plataforma"}


def create_instructor(instrutor: UsuarioValidar, confirmacao_login: str, db: Session):
    """Cria o instrutor que sera o responsavel por gerenciar notas, progresso, curso"""
    validacao_nome_adm = (
        db.query(Usuario).filter(Usuario.nome_user == confirmacao_login).first()
    )
    if not validacao_nome_adm:
        raise HTTPException(status_code=404, detail="admnistrador nao encontrado")
    if validacao_nome_adm.cargo != "administrador":
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: apenas admnistradores podem criar instrutores na plataforma",
        )

    existencia_instrutor = (
        db.query(Usuario).filter(Usuario.nome_user == instrutor.nome_user).first()
    )
    if existencia_instrutor:
        raise HTTPException(status_code=400, detail="Nome ja existente, insira outro")
    senha_criptografada = gerar_hash_senha(instrutor.senha)
    novo_instrutor = Usuario(
        nome_user=instrutor.nome_user, senha=senha_criptografada, cargo="instrutor"
    )
    db.add(novo_instrutor)
    db.commit()
    db.refresh(novo_instrutor)
    return {"mensagem": "Boas vindas ao novo instrutor"}


def login(db: Session, username: str, senha: str):
    """Login no sistema e retorna o token"""
    existencia = db.query(Usuario).filter(Usuario.nome_user == username).first()
    if not existencia:
        raise HTTPException(status_code=404, detail="Credencial invalida")
    senha_verificada = verificar_senha(senha, existencia.senha)
    if not senha_verificada:
        raise HTTPException(status_code=400, detail="Credencial invalida")
    token = criar_token_jwt({"sub": existencia.nome_user})
    return {"access_token": token, "token_type": "bearer"}


def create_course(confirmacao_login: str, db: Session, dados_curso: CursosValidar):
    """O Instrutor consegue criar o curso e impede outros cargos de criarem"""
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
    """Fornece a possibilidade do aluno criar a matricula nos cursos ja existentes"""
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
    """Lista os cursos de cada professor"""
    cursos_de_cada_instrutor = (
        db.query(Curso).options(joinedload(Curso.instrutor)).all()
    )

    return cursos_de_cada_instrutor


def add_class_course(
    db: Session, curso_id: int, titulo_aula: str, arquive: UploadFile, nome_usuario: str
):
    """Faz o upload do arquivo e vincula a um curso do banco de dados"""
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
    """Retorna a lista de aulas em JSON vinculadas a um curso especifico"""
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(
            status_code=403,
            detail="Nenhum curso encontrado",
        )
    aulas = db.query(Aula).filter(Aula.id_curso == curso_id).all()
    return aulas


def download_file_of_class(db: Session, aula_id: int):
    """Devolve o arquivo para visualizacao/download"""
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
