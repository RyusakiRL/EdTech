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
