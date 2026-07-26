"""Cria um administrador para checar as informacoes do sistema"""

from sqlalchemy.orm import Session
from models import Usuario
from schemas import UsuarioValidar
from security import gerar_hash_senha
from database import get_db

ROLE = "administrador"
NAME_ADM = str(input("Insira o nome do novo admnistrador do sistema: "))
SENHA_ADM = str(input("Insira a senha do novo administrador do sistema: "))
novo_adm = UsuarioValidar(nome_user=NAME_ADM, senha=SENHA_ADM)
db = next(get_db())


def new_admnistrator(new_adm: UsuarioValidar, db_session: Session):
    """cria um novo admnistrador do sistema"""
    if db_session.query(Usuario).filter(Usuario.name_user == new_adm.nome_user).first():
        print("Esse nome de admnistrador ja existe registre outro nome")
    else:
        senha_hash = gerar_hash_senha(new_adm.senha)

        criacao_de_novo_admnistrador = Usuario(
            nome_user=new_adm.nome_user, senha=senha_hash, cargo=ROLE
        )

        db_session.add(criacao_de_novo_admnistrador)
        db_session.commit()
        db_session.refresh(criacao_de_novo_admnistrador)
        print("Sucesso na criacao do adm")
    return {"Sucesso na criacao do e admnistador"}


new_admnistrator(new_adm=novo_adm, db_session=db)
