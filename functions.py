"""System Functions"""

import shutil
from pathlib import Path
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from models import (
    User,
    CurrentInventory,
    MonthlyPayroll,
    TimeRecord,
    Department,
    Product,
    Status,
)
from schemas import (
    ManagerAdministratorValidation,
    OperatorValidation,
    DepartmentValidation,
    ProductValidation,
)

from security import verify_password, generator_hash_password
from security import create_token_jwt

UPLOADS_FOLDER = Path("uploads")

UPLOADS_FOLDER.mkdir(exist_ok=True)

NORMAL_OPERATOR_SALARY_HOUR = 1200.00


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


def login(db: Session, username: str, password: str):
    """Login in system and return the token"""
    existence = db.query(User).filter(User.name_user == username).first()
    if not existence:
        raise HTTPException(status_code=404, detail="Invalid credential")
    verified_password = verify_password(password, existence.password_user)
    if not verified_password:
        raise HTTPException(status_code=400, detail="Invalid credential")
    if existence.is_active is False:
        raise HTTPException(
            status_code=403, detail="Access denied: user is not active on plataform"
        )
    token = create_token_jwt({"sub": existence.name_user})
    return {"access_token": token, "token_type": "bearer"}


def employee_demission(db: Session, my_number: int, login_confirmation: str):
    """Allow a manager to demission a employee"""
    name_validation_manager = (
        db.query(User).filter(User.name_user == login_confirmation).first()
    )
    if not name_validation_manager:
        raise HTTPException(status_code=404, detail="manager not found")
    if (
        name_validation_manager.role_user != Status.MANAGER
        or name_validation_manager.is_active is False
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


def manager_demission(db: Session, my_number: int, login_confirmation: str):
    """Allow a administrator to demission a manager"""
    name_validation_administrator = (
        db.query(User).filter(User.name_user == login_confirmation).first()
    )
    if not name_validation_administrator:
        raise HTTPException(status_code=404, detail="administrator not found")
    if name_validation_administrator.role_user != Status.ADMINISTRATOR:
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


def department_creation(
    department_validation: DepartmentValidation, login_confirmation: str, db: Session
):
    """Allow a administrator to create a department"""
    name_validation_administrator = (
        db.query(User).filter(User.name_user == login_confirmation).first()
    )
    if not name_validation_administrator:
        raise HTTPException(status_code=404, detail="administrator not found")
    if (
        name_validation_administrator.role_user != Status.ADMINISTRATOR
        or name_validation_administrator.is_active is False
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied: only administrator can create department on plataform",
        )

    user = db.query(User).filter(User.id == department_validation.users_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.role_user != Status.MANAGER or user.is_active is False:
        raise HTTPException(
            status_code=400,
            detail="Only managers can be assigned to a department.",
        )

    new_department = Department(
        users_id=department_validation.users_id,
        department_title=department_validation.department_title,
    )
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    return {"message": "Department created successfully."}


def product_creation(
    product_validation: ProductValidation, login_confirmation: str, db: Session
):
    """Allow a manager to create a product"""
    name_validation_manager = (
        db.query(User).filter(User.name_user == login_confirmation).first()
    )
    if not name_validation_manager:
        raise HTTPException(status_code=404, detail="manager not found")
    if (
        name_validation_manager.role_user != Status.MANAGER
        or name_validation_manager.is_active is False
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied: only manager can create product on plataform",
        )

    new_product = Product(
        product_name=product_validation.product_name,
        base_price=product_validation.base_price,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "Product created successfully."}
