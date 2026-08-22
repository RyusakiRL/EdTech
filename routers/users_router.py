"""Router for user-related endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import OperatorValidation, ManagerAdministratorValidation

from services.users_service import (
    create_employee,
    create_manager,
    employee_demission,
    manager_demission,
)

router = APIRouter(prefix="/users", tags=["User management"])


@router.post("/employee/create")
def create_employee_route(
    operator: OperatorValidation,
    login_confirmation: int,
    db: Session = Depends(get_db),
):
    """Endpoint to create an employee."""
    return create_employee(
        operator=operator, login_confirmation=login_confirmation, db=db
    )


@router.post("/manager/create")
def create_manager_route(
    manager: ManagerAdministratorValidation,
    login_confirmation: int,
    db: Session = Depends(get_db),
):
    """Endpoint to create a manager."""
    return create_manager(manager=manager, login_confirmation=login_confirmation, db=db)


@router.post("/employee/demit")
def employee_demission_route(
    employee_number: int,
    login_confirmation: int,
    db: Session = Depends(get_db),
):
    """Endpoint to demit an employee."""
    return employee_demission(
        my_number=employee_number, login_confirmation=login_confirmation, db=db
    )


@router.post("/manager/demit")
def manager_demission_route(
    manager_number: int,
    login_confirmation: int,
    db: Session = Depends(get_db),
):
    """Endpoint to demit a manager."""
    return manager_demission(
        my_number=manager_number, login_confirmation=login_confirmation, db=db
    )
