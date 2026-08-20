"""Liga o sistema a API"""

from typing import List
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from functions import (
    create_employee,
    login,
    create_manager,
    department_creation,
    employee_demission,
    manager_demission,
    product_creation,
    create_inventory_movement,
    card_creation,
)
from schemas import (
    DepartmentValidation,
    ManagerAdministratorValidation,
    OperatorValidation,
    ProductValidation,
    InventoryMovementValidation,
    CardValidation,
)
from security import verify_token

app = FastAPI()


@app.get("/", include_in_schema=False)
def root():
    """Connects the system in a Render"""
    return RedirectResponse(url="/docs")


@app.post("/login")
def login_route(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """System route of login"""
    login_name = form_data.username
    login_password = form_data.password
    return login(db=db, username=login_name, password=login_password)


FOLDER_UPLOADS = Path("uploads")

FOLDER_UPLOADS.mkdir(exist_ok=True)


@app.post("/create_employee")
def create_employee_route(
    operator: OperatorValidation,
    login_confirmation: int = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Route to create a employee"""
    return create_employee(
        operator=operator, login_confirmation=login_confirmation, db=db
    )


@app.post("/create_manager")
def create_manager_route(
    manager: ManagerAdministratorValidation,
    login_confirmation: int = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Route to create a manager"""
    return create_manager(manager=manager, login_confirmation=login_confirmation, db=db)


@app.post("/create_department")
def create_department_route(
    department: DepartmentValidation,
    login_confirmation: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Route to create a department"""
    return department_creation(
        department_validation=department, login_confirmation=login_confirmation, db=db
    )


@app.delete("/demission_employee")
def demission_employee_route(
    my_number: int = Form(...),
    login_confirmation: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Route to demission a employee"""
    return employee_demission(
        my_number=my_number, login_confirmation=login_confirmation, db=db
    )


@app.delete("/demission_manager")
def demission_manager_route(
    my_number: int = Form(...),
    login_confirmation: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Route to demission a manager"""
    return manager_demission(
        my_number=my_number, login_confirmation=login_confirmation, db=db
    )


@app.post("/create_product")
def create_product_route(
    product: ProductValidation,
    login_confirmation: int = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Route to create a product"""
    return product_creation(
        product_validation=product, login_confirmation=login_confirmation, db=db
    )


@app.post("/create_inventory_movement")
def create_inventory_movement_route(
    inventory_movement: InventoryMovementValidation,
    login_confirmation: int = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Route to create an inventory movement"""
    return create_inventory_movement(
        inventory_movement_validation=inventory_movement,
        login_confirmation=login_confirmation,
        db=db,
    )


@app.post("/create_card")
def create_card_route(
    card_validation: CardValidation,
    login_confirmation: int = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Route to create a card"""
    return card_creation(
        card_validation=card_validation,
        login_confirmation=login_confirmation,
        db=db,
    )
