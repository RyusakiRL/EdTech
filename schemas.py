"""Data validation based em class models"""

from pydantic import BaseModel, ConfigDict


class UserValidation(BaseModel):
    """Data validation for user creation in SQL"""

    user_name: str
    password_model: str
    model_config = ConfigDict(from_attributes=True)


class CoursesValidation(BaseModel):
    """Data validation for courses creation in SQL"""

    title_model: str
    description_model: str


class InstructorResponse(BaseModel):
    """Response model for instructors list"""

    name_user: str


class ModelResponseCursos(BaseModel):
    """Response model for data list of courses"""

    course_title: str
    description: str
    instructor: InstructorResponse
