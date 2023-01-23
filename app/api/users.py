from fastapi import  Request, Form,  APIRouter, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import time

from app.crud import *
from app.dependecies import *
from app.crud.security import *
from app.crud.users import *
import app.schemas as schemas
import app.crud as crud


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_user(
    request: Request, user: schemas.UserCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)
    ):
    if current_user == None:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "login_alert": "your session has expired"
            } 
        )
    user_db_by_username = crud.get_user_by_username(db, username=user.username)
    if user_db_by_username:
        raise HTTPException(status_code=409, detail="Username already exists.")
    new_user = crud.create_user(db, user)
    return new_user



@router.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    time.sleep(2)
    token = get_auth_header_if_correct_credentials(db, username, password)
    if token:
        os.environ["TOKEN"] = str(token) 
        return templates.TemplateResponse("main.html", {
            "request": request,
            "token": token
        })
    else:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "login_alert": "wrong password or username"
            } 
        )  
        
@router.post("/logout")
def logout(request: Request):
    os.environ["TOKEN"] = ""
    return templates.TemplateResponse("login.html", {
            "request": request, 
            "login_alert": "you have been logged out"
            } 
        )  
    


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password_1: str = Form(...),
    password_2: str = Form(...),
    db: Session = Depends(get_db)):
    
    try:
        register_alert = "first and second password must be identical"
        check_if_passwords_are_identical(password_1, password_2)
        register_alert = "username must be created with: a-z, A-Z, 0-9, 6-20 chars"
        check_username(username)
        register_alert = "username is already taken"
        check_if_username_in_db(db, username)
        register_alert = "password must be created with: 6-20 chars, at least one: A-Z, a-z, special character, 0-9"
        check_password(password_1)
        
        new_user = schemas.UserCreate(username=username, password=password_1)
        crud.create_user(db, new_user)
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "login_alert": "you have been registered"
            } 
        )  
    except:
        return templates.TemplateResponse("register.html", {
        "request": request,
        "register_alert": register_alert
        } 
    )  
        

    
    