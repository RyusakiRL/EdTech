"""Cria um administrador para checar as informacoes do sistema"""

from sqlalchemy.orm import Session
from models import Usuario
from schemas import UserValidation
from security import gerar_hash_senha
from database import get_db

ROLE = "administrador"
NAME_ADM = str(input("Input the name of new system admnistrator: "))
SENHA_ADM = str(input("Input the password of new system admnistrator: "))
new_administrator = UserValidation(user_name=NAME_ADM, password_model=SENHA_ADM)
db = next(get_db())


def new_admnistrator(new_adm: UserValidation, db_session: Session):
    """cria um novo admnistrador do sistema"""
    if db_session.query(Usuario).filter(Usuario.name_user == new_adm.user_name).first():
        print("This name already exists input a other name")
    else:
        senha_hash = gerar_hash_senha(new_adm.password_model)

        creation_of_new_admnistrator = Usuario(
            nome_user=new_adm.user_name, senha=senha_hash, cargo=ROLE
        )

        db_session.add(creation_of_new_admnistrator)
        db_session.commit()
        db_session.refresh(creation_of_new_admnistrator)
        print("Sucess in adm acreation")
    return {"Sucess in adm acreation"}


new_admnistrator(new_adm=new_administrator, db_session=db)
