"""Create a admnistrator for the system, to check any database"""

from sqlalchemy.orm import Session
from models import User
from schemas import UserValidation
from security import generator_hash_password
from database import get_db

ROLE = "administrator"
ADM_NAME = str(input("Input the name of new system admnistrator: "))
ADM_PASSWORD = str(input("Input the password of new system admnistrator: "))
new_administrator = UserValidation(user_name=ADM_NAME, password_model=ADM_PASSWORD)
db = next(get_db())


def new_admnistrator(new_adm: UserValidation, db_session: Session):
    """Create a new admnistrator in the system"""
    if db_session.query(User).filter(User.name_user == new_adm.user_name).first():
        print("This name already exists input a other name")
    else:
        senha_hash = generator_hash_password(new_adm.password_model)

        creation_of_new_admnistrator = User(
            name_user=new_adm.user_name, password_user=senha_hash, role_user=ROLE
        )

        db_session.add(creation_of_new_admnistrator)
        db_session.commit()
        db_session.refresh(creation_of_new_admnistrator)
        print("Sucess in adm creation")
    return {"Sucess in adm creation"}


new_admnistrator(new_adm=new_administrator, db_session=db)
