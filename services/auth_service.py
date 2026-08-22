"""Login service module for handling user authentication and token generation."""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import User
from security import verify_password, create_token_jwt


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
