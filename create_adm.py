"""Create a admnistrator for the system, to check any database"""

from sqlalchemy.orm import Session
from models import User, Status
from schemas import ManagerAdministratorValidation
from security import generator_hash_password
from database import get_db

ADM_NAME = str(input("Input the name of new system administrator: "))
ADM_PASSWORD = str(input("Input the password of new system administrator: "))
ADM_NUMBER = int(input("Input the number of new system administrator: "))
new_administrator = ManagerAdministratorValidation(
    name_user=ADM_NAME, password_user=ADM_PASSWORD, my_number=ADM_NUMBER
)
db = next(get_db())


def new_server_administrator(
    new_adm: ManagerAdministratorValidation, db_session: Session
):
    """Create a new admnistrator in the system"""
    adm_existence = (
        db_session.query(User).filter(User.my_number == new_adm.my_number).first()
    )
    if adm_existence and adm_existence.is_active is True:
        print("This number already exists input a other number")
    else:
        hashed_password = generator_hash_password(new_adm.password_user)

        creation_of_new_administrator = User(
            name_user=new_adm.name_user,
            password_user=hashed_password,
            role_user=Status.ADMINISTRATOR,
            my_number=new_adm.my_number,
        )

        db_session.add(creation_of_new_administrator)
        db_session.commit()
        db_session.refresh(creation_of_new_administrator)
        print("Sucess in administrator creation")
    return {"Sucess in administrator creation"}


new_server_administrator(new_adm=new_administrator, db_session=db)
