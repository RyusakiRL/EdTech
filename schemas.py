"""Data validation based em class models"""

from pydantic import BaseModel, ConfigDict, Field


class ManagerAdministratorValidation(BaseModel):
    """Data validation for manager and administrator creation in SQL"""

    name_user: str = Field(min_length=3, max_length=50)
    password_model: str
    my_number: int


class OperatorValidation(BaseModel):
    """Data validation for operator creation in SQL"""

    name_user: str = Field(min_length=3, max_length=50)
    my_number: int


class DepartmentValidation(BaseModel):
    """Data validation for department creation in SQL"""

    department_title: str = Field(min_length=3, max_length=100)
    users_id: int


class ProductValidation(BaseModel):
    """Data validation for product creation in SQL"""

    product_name: str = Field(min_length=3, max_length=100)
    base_price: float = Field(gt=0, description="Base price must be greater than zero")


class InventoryMovementValidation(BaseModel):
    """Data validation for moving products in/out of inventory"""

    product_id: int
    departments_id: int
    movement_type: str = Field(description="Must be 'IN' or 'OUT'")
    quantity: int = Field(gt=0, description="Quantity must be greater than zero")


class CardValidation(BaseModel):
    """Data validation for card creation in SQL"""

    users_id: int
