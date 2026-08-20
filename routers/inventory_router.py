"""Router for inventory-related endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import InventoryMovementValidation, ProductValidation, DepartmentValidation
from services.inventory_service import (
    department_creation,
    product_creation,
    inventory_movement_creation,
)

router = APIRouter(prefix="/inventory", tags=["Inventory management"])


@router.post("/department/create")
def create_department(
    department_validation: DepartmentValidation,
    login_confirmation: int,
    db: Session = Depends(get_db),
):
    """Endpoint to create a department."""
    return department_creation(
        department_validation=department_validation,
        login_confirmation=login_confirmation,
        db=db,
    )


@router.post("/product/create")
def create_product(
    product_validation: ProductValidation,
    login_confirmation: int,
    db: Session = Depends(get_db),
):
    """Endpoint to create a product."""
    return product_creation(
        product_validation=product_validation,
        login_confirmation=login_confirmation,
        db=db,
    )


@router.post("/movement/create")
def create_inventory_movement(
    inventory_movement_validation: InventoryMovementValidation,
    login_confirmation: int,
    db: Session = Depends(get_db),
):
    """Endpoint to create an inventory movement."""
    return inventory_movement_creation(
        inventory_movement_validation=inventory_movement_validation,
        login_confirmation=login_confirmation,
        db=db,
    )
