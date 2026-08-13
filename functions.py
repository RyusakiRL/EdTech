"""System Functions"""

import shutil
from pathlib import Path
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from models import (
    User,
    DailyInventory,
    MonthlyPayroll,
    TimeRecord,
    Department,
    Product,
    Status,
)
from schemas import ManagerAdministratorValidation, OperatorValidation

from security import verify_password, generator_hash_password
from security import create_token_jwt

UPLOADS_FOLDER = Path("uploads")

UPLOADS_FOLDER.mkdir(exist_ok=True)


def create_employee(operator: OperatorValidation, login_confirmation: str, db: Session):
    """Allow a manager to create a employee"""
    name_validation_manager = (
        db.query(User).filter(User.name_user == login_confirmation).first()
    )
    if not name_validation_manager:
        raise HTTPException(status_code=404, detail="manager not found")
    if name_validation_manager.role_user != Status.MANAGER:
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
    manager: ManagerAdministratorValidation, login_confirmation: str, db: Session
):
    """Create a security manager route: manage works, progress and others functions"""
    name_validation_administrator = (
        db.query(User).filter(User.name_user == login_confirmation).first()
    )
    if not name_validation_administrator:
        raise HTTPException(status_code=404, detail="administrator not found")
    if name_validation_administrator.role_user != Status.ADM:
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


def login(db: Session, username: str, password: str):
    """Login in system and return the token"""
    existence = db.query(User).filter(User.name_user == username).first()
    if not existence:
        raise HTTPException(status_code=404, detail="Invalid credential")
    verified_password = verify_password(password, existence.password_user)
    if not verified_password:
        raise HTTPException(status_code=400, detail="Invalid credential")
    token = create_token_jwt({"sub": existence.name_user})
    return {"access_token": token, "token_type": "bearer"}
