"""System Functions"""

import shutil
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from models import (
    Card,
    InventoryMovement,
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
    InventoryMovementValidation,
    CardValidation,
)

from security import verify_password, generator_hash_password
from security import create_token_jwt

UPLOADS_FOLDER = Path("uploads")

UPLOADS_FOLDER.mkdir(exist_ok=True)

NORMAL_OPERATOR_SALARY_HOUR = 1200.00


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
    token = create_token_jwt({"sub": existence.my_number})
    return {"access_token": token, "token_type": "bearer"}


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


def department_creation(
    department_validation: DepartmentValidation, login_confirmation: int, db: Session
):
    """Allow a administrator to create a department"""
    my_number_validation_administrator = (
        db.query(User).filter(User.my_number == login_confirmation).first()
    )
    if not my_number_validation_administrator:
        raise HTTPException(status_code=404, detail="administrator not found")
    if (
        my_number_validation_administrator.role_user != Status.ADMINISTRATOR
        or my_number_validation_administrator.is_active is False
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
    product_validation: ProductValidation, login_confirmation: int, db: Session
):
    """Allow a manager to create a product"""
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


def create_inventory_movement(
    inventory_movement_validation: InventoryMovementValidation,
    login_confirmation: int,
    db: Session,
):
    """Allow a manager to move products in/out of inventory"""
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
            detail="Access denied: only manager can move products in/out of inventory",
        )

    product = (
        db.query(Product)
        .filter(Product.id == inventory_movement_validation.product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    department = (
        db.query(Department)
        .filter(Department.id == inventory_movement_validation.departments_id)
        .first()
    )
    if not department:
        raise HTTPException(status_code=404, detail="Department not found.")

    if inventory_movement_validation.movement_type not in ["IN", "OUT"]:
        raise HTTPException(
            status_code=400, detail="Invalid movement type. Must be 'IN' or 'OUT'."
        )

    inventory_record = (
        db.query(CurrentInventory)
        .filter(
            CurrentInventory.product_id == inventory_movement_validation.product_id,
            CurrentInventory.departments_id
            == inventory_movement_validation.departments_id,
        )
        .first()
    )

    if inventory_movement_validation.movement_type == "IN":
        if inventory_record:

            inventory_record.product_in_stock += inventory_movement_validation.quantity
        else:

            inventory_record = CurrentInventory(
                product_id=inventory_movement_validation.product_id,
                departments_id=inventory_movement_validation.departments_id,
                product_in_stock=inventory_movement_validation.quantity,
                product_to_come=0,
            )
            db.add(inventory_record)
            db.flush()

    elif inventory_movement_validation.movement_type == "OUT":
        if not inventory_record:
            raise HTTPException(
                status_code=404,
                detail="Inventory record not found. Cannot remove non-existent stock.",
            )
        if inventory_record.product_in_stock < inventory_movement_validation.quantity:
            raise HTTPException(
                status_code=400, detail="Insufficient stock for the requested movement."
            )

        inventory_record.product_in_stock -= inventory_movement_validation.quantity

    new_movement = InventoryMovement(
        current_inventory_id=inventory_record.id,
        movement_type=inventory_movement_validation.movement_type,
        quantity=inventory_movement_validation.quantity,
        unit_price_at_transaction=product.base_price,
    )
    db.add(new_movement)

    db.commit()
    db.refresh(inventory_record)

    return {
        "message": f"Inventory movement '{inventory_movement_validation.movement_type}' for product '{product.product_name}' processed successfully."
    }


def card_creation(
    card_validation: CardValidation, login_confirmation: int, db: Session
):
    """Allow a manager to create a card"""
    creator = db.query(User).filter(User.my_number == login_confirmation).first()
    if not creator or creator.is_active is False:
        raise HTTPException(status_code=404, detail="User not found or inactive.")
    card_user = db.query(User).filter(User.id == card_validation.users_id).first()

    if not card_user or card_user.is_active is False:
        raise HTTPException(status_code=404, detail="User not found or inactive.")
    if card_user.role_user == Status.ADMINISTRATOR:
        raise HTTPException(
            status_code=403,
            detail="Access denied: cannot create cards for administrators.",
        )
    if creator.role_user != Status.MANAGER and card_user.role_user == Status.OPERATOR:
        raise HTTPException(
            status_code=403,
            detail="Access denied: managers can only create cards for operators.",
        )

    if (
        creator.role_user != Status.ADMINISTRATOR
        and card_user.role_user == Status.MANAGER
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied: administrators can only create cards for managers.",
        )
    generated_card_number_qr_code = str(uuid.uuid4())
    new_card = Card(
        card_number=generated_card_number_qr_code,
        users_id=card_validation.users_id,
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return {
        "message": "Card created successfully.",
        "qr_code": generated_card_number_qr_code,
    }
