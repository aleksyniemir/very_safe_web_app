from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
import os

import app.schemas as schemas
import app.models as models
from app.dependecies import *
from app.crud.security import *
from app.crud  import *

templates = Jinja2Templates(directory="app/templates")
    
def get_user(db: Session, id: int):
    stmt = select(models.User).where(models.User.id == id)
    user = db.scalar(stmt)
    return user

def get_user_by_username(db: Session, username: str):
    stmt = select(models.User).where(models.User.username == username)
    user = db.scalar(stmt)
    return user


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_current_user(db: Session = Depends(get_db)):
    token = os.environ["TOKEN"]
    print("TOKEN IN get_current_user " + str(token))
    if token == "empty":
        return 
    try:
        payload = jwt.decode(eval(token)["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            return 
        token_data = schemas.TokenData(username=username)
    except JWTError:
        return 
    user = get_user_by_username(db, token_data.username)
    if not user:
        return 
    return user
