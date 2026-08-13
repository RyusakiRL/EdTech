"""Data validation based em class models"""

from pydantic import BaseModel, ConfigDict


class ManagerAdministratorValidation(BaseModel):
    """Data validation for user creation in SQL"""

    name_user: str
    password_model: str
    my_number: int


class OperatorValidation(BaseModel):
    """Data validation for operator creation in SQL"""

    name_user: str
    my_number: int
