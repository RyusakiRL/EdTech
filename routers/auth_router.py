"""Router for authentication-related endpoints."""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db

from services.auth_service import login

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login_route(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """System route of login"""
    login_name = form_data.username
    login_password = form_data.password
    return login(db=db, username=login_name, password=login_password)
