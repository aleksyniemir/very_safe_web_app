from fastapi import  Request,  APIRouter, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.crud.users import *
import app.models
import app.schemas
from app.dependecies import *
from app.crud.security import *

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/main", response_class=HTMLResponse)
def main_page(request: Request, current_user = Depends(get_current_user)):
    if current_user == None:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "login_alert": "your session has expired"
            } 
        )
    return templates.TemplateResponse("main.html", {
        "request": request
    })


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "login_alert": ""
        } 
    )
    
@router.get("/notes/create/{with_password}", status_code=status.HTTP_202_ACCEPTED)
def create_note(with_password: bool, request: Request, current_user = Depends(get_current_user)):
    print("with:passwrd " + str(with_password))
    return templates.TemplateResponse("create_note.html", {
        "request": request,
        "with_password": with_password
        } 
    )  
    
@router.get("/register")
def register(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request
        } 
    )  
    
@router.get("/notes/search_by_id")
def search_note_by_id_page(request: Request, current_user = Depends(get_current_user)):
    return templates.TemplateResponse("search_note.html", {
        "request": request
        }
    )