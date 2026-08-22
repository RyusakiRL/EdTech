"""General user service module for managing user creation and demission."""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import User, Status
from schemas import OperatorValidation, ManagerAdministratorValidation
from security import generator_hash_password


def create_employee(operator: OperatorValidation, login_confirmation: int, db: Session):
    """Allow a manager to create a employee"""
    my_number_validation_manager = (
        db.query(User).filter(User.my_number == login_confirmation).first()
    )
    if not my_number_validation_manager:
        raise HTTPException(status_code=404, detail="manager not found")
    if my_number_validation_manager.role_user != Status.MANAGER:
        raise HTTPException(
            status_code=403,
            detail="Access denied: only manager can create operator on plataform",
        )
    operator_existence = (
        db.query(User).filter(User.my_number == operator.my_number).first()
    )
    if operator_existence and operator_existence.is_active is True:
        raise HTTPException(
            status_code=400,
            detail="My number already exists: please enter another one.",
        )
    if operator_existence and operator_existence.is_active is False:
        operator_existence.is_active = True
        operator_existence.name_user = operator.name_user
        db.commit()
        db.refresh(operator_existence)
        return {"message": "Welcome back to our enterprise."}
    new_operator = User(
        name_user=operator.name_user,
        my_number=operator.my_number,
        role_user=Status.OPERATOR,
    )
    db.add(new_operator)
    db.commit()
    db.refresh(new_operator)
    return {"message": "Welcome to our enterprise."}


def create_manager(
    manager: ManagerAdministratorValidation, login_confirmation: int, db: Session
):
    """Create a security manager route: manage works, progress and others functions"""
    name_validation_administrator = (
        db.query(User).filter(User.name_user == login_confirmation).first()
    )
    if not name_validation_administrator:
        raise HTTPException(status_code=404, detail="administrator not found")
    if name_validation_administrator.role_user != Status.ADMINISTRATOR:
        raise HTTPException(
            status_code=403,
            detail="Access denied: only administrator can create managers on plataform",
        )

    manager_existence = (
        db.query(User).filter(User.my_number == manager.my_number).first()
    )
    if manager_existence and manager_existence.is_active is True:
        raise HTTPException(
            status_code=400, detail="My number already exists: insert other"
        )
    if manager_existence and manager_existence.is_active is False:
        manager_existence.is_active = True
        manager_existence.name_user = manager.name_user
        encrypted_password = generator_hash_password(manager.password_model)
        manager_existence.password_user = encrypted_password
        db.commit()
        db.refresh(manager_existence)
        return {"message": "Welcome back to our enterprise."}
    encrypted_password = generator_hash_password(manager.password_model)
    new_manager = User(
        name_user=manager.name_user,
        password_user=encrypted_password,
        role_user=Status.MANAGER,
        my_number=manager.my_number,
    )
    db.add(new_manager)
    db.commit()
    db.refresh(new_manager)
    return {"message": "Welcome to the new manager"}


def employee_demission(db: Session, my_number: int, login_confirmation: int):
    """Allow a manager to demission a employee"""
    my_number_validation_manager = (
        db.query(User).filter(User.my_number == login_confirmation).first()
    )
    if not my_number_validation_manager:
        raise HTTPException(status_code=404, detail="manager not found")
    if (
        my_number_validation_manager.role_user != Status.MANAGER
        or my_number_validation_manager.is_active is False
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied: only manager can demission operator on plataform",
        )
    employee_existence = db.query(User).filter(User.my_number == my_number).first()
    if not employee_existence or employee_existence.is_active is not True:
        raise HTTPException(status_code=404, detail="employee not found")
    if employee_existence.role_user != Status.OPERATOR:
        raise HTTPException(
            status_code=403,
            detail="Access denied: only operator can be demissioned on plataform",
        )
    employee_existence.is_active = False
    db.commit()
    db.refresh(employee_existence)
    return {"message": "Employee demissioned successfully."}


def manager_demission(db: Session, my_number: int, login_confirmation: int):
    """Allow a administrator to demission a manager"""
    my_number_validation_administrator = (
        db.query(User).filter(User.my_number == login_confirmation).first()
    )
    if not my_number_validation_administrator:
        raise HTTPException(status_code=404, detail="administrator not found")
    if my_number_validation_administrator.role_user != Status.ADMINISTRATOR:
        raise HTTPException(
            status_code=403,
            detail="Access denied: only administrator can demission manager on plataform",
        )
    manager_existence = db.query(User).filter(User.my_number == my_number).first()
    if not manager_existence or manager_existence.is_active is not True:
        raise HTTPException(status_code=404, detail="manager not found")
    if manager_existence.role_user != Status.MANAGER:
        raise HTTPException(
            status_code=403,
            detail="Access denied: only manager can be demissioned on plataform",
        )
    manager_existence.is_active = False
    db.commit()
    db.refresh(manager_existence)
    return {"message": "Manager demissioned successfully."}
