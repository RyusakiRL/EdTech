"""Funcoes do sistema"""

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from models import Curso, Matricula, Usuario
from schemas import CursosValidar, UsuarioValidar
from security import verificar_senha, gerar_hash_senha
from security import criar_token_jwt


def criar_estudante(estudante: UsuarioValidar, db: Session):
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


def criar_instrutor(instrutor: UsuarioValidar, confirmacao_login: str, db: Session):
    """Cria o instrutor que sera o responsavel por gerenciar notas, progresso, curso"""
    validacao_nome_adm = (
        db.query(Usuario).filter(Usuario.nome_user == confirmacao_login).first()
    )
    if not validacao_nome_adm.cargo == "administrador":
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


def criar_curso(confirmacao_login: str, db: Session, dados_curso: CursosValidar):
    """O Instrutor consegue criar o curso e impede outros cargos de criarem"""
    validacao_nome_instrutor = (
        db.query(Usuario).filter(Usuario.nome_user == confirmacao_login).first()
    )
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


def criar_matricula(confirmacao_login: str, curso_nome: str, db: Session):
    """Fornece a possibilidade do aluno criar a matricula nos cursos ja existentes"""
    existencia_estudante = (
        db.query(Usuario).filter(Usuario.nome_user == confirmacao_login).first()
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


def listar_cursos(db: Session):
    """Lista os cursos de cada professor"""
    cursos_de_cada_instrutor = (
        db.query(Curso).options(joinedload(Curso.instrutor)).all()
    )

    return cursos_de_cada_instrutor
