from fastapi import  Request, Form,  APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from bleach import Cleaner

from app.crud.users import *
import app.crud as crud
from app.dependecies import *
from app.crud.security import *

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")
 
@router.get("/notes")
def get_all_notes(request: Request, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user == None:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "login_alert": "your session has expired"
            } 
        )
    return crud.get_all_notes

@router.get("/notes/your_notes")
def get_your_notes(request: Request, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user == None:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "login_alert": "your session has expired"
            } 
        )
    notes_id = crud.get_current_users_notes_id(db, current_user)
    print(notes_id)
    return templates.TemplateResponse("your_notes.html", {
            "request": request, 
            "notes": notes_id
            } 
        )

@router.get("/notes/get/{note_id}/{is_public}")
def read_note(request: Request, note_id: int, is_public: bool, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    note = crud.get_note_by_id(db, note_id)
    if is_public:
        # read note
        return templates.TemplateResponse("read_note.html", {
            "request": request, 
            "note": note.markdown_encrypted
            }
        )
    else:
        # go to password page
        return templates.TemplateResponse("note_password.html", {
            "request": request,
            "note_id": note.id
            }
        )



@router.post("/notes/search_by_id")
def search_note_by_id(request: Request, note_id: int =  Form(...), current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    note = crud.get_note_by_id(db, note_id)
    if note.public:
        # read note
        return templates.TemplateResponse("read_note.html", {
            "request": request, 
            "note": note.markdown_encrypted
            }
        )
    else:
        # go to password page
        return templates.TemplateResponse("note_password.html", {
            "request": request,
            "note_id": note.id
            }
        )

@router.post("/notes/get/{note_id}")
def read_note_with_password(note_id: int, request: Request, password: str = Form(...), current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        crud.check_password(password)
        note = crud.get_note_by_id(db, note_id)
        
        markdown_decrypted = crud.get_decrypted_markdown(note, password)
        if markdown_decrypted:
            try:
                return templates.TemplateResponse("read_note.html", {
                    "request": request, 
                    "note": markdown_decrypted
                    }
                )
            except:
                return templates.TemplateResponse("note_password.html", {
                    "request": request,
                    "note_id": note_id,
                    "wrong_password_alert": "problem with loading markdown"
                    }
                )
                
        else:
            return templates.TemplateResponse("note_password.html", {
            "request": request,
            "note_id": note_id,
            "wrong_password_alert": "wrong password, try again"
            }
        )
    except:
        return templates.TemplateResponse("note_password.html", {
            "request": request,
            "note_id": note_id,
            "wrong_password_alert": "wrong password, try again"
            }
        )

@router.post("/notes/create/with_password", status_code=status.HTTP_201_CREATED)
def create_note(request: Request, note: str = Form(...), password: str = Form(...), current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user == None:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "login_alert": "your session has expired"
            } 
        )
    if len(note) == 0 or len(note) >= 8192:
        error_msg = "Note length must be between 1 and 8192"
        return templates.TemplateResponse("create_note.html", {
            "request": request,
            "error_msg": error_msg,
            "with_password": True
            }
        )
    try:
        crud.check_password(password)
    except:
        return templates.TemplateResponse("create_note.html", {
            "request": request,
            "with_password": True,
            "error_msg": "Password must contain at least one A-Z, a-z, \
                special character, number, and have between 6-20 characters"
            }
        )
        
    cleaner = Cleaner(
        tags=['h1', 'h2', 'h3', 'h4', 'h5', 'a', 'strong', 'em', 'p', 'img'],
        attributes={'a': ['href'], 'img': ['src']}
    )
    clean_note = cleaner.clean(note)

    crud.add_note(db, current_user, clean_note, password)
    
    return templates.TemplateResponse("main.html", {
        "request": request,
    })


@router.post("/notes/create/without_password", status_code=status.HTTP_201_CREATED)
def create_note(request: Request, note: str = Form(...),current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user == None:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "login_alert": "your session has expired"
            } 
        )
    if len(note) == 0 or len(note) >= 8192:
        error_msg = "Note length must be between 1 and 8192"
        return templates.TemplateResponse("create_note.html", {
            "request": request,
            "error_msg": error_msg,
            "with_password": False
            }
        )
    cleaner = Cleaner(
        tags=['h1', 'h2', 'h3', 'h4', 'h5', 'a', 'strong', 'em', 'p', 'img'],
        attributes={'a': ['href'], 'img': ['src']}
    )
    clean_note = cleaner.clean(note)
            
    crud.add_note(db, current_user, clean_note)
    
    return templates.TemplateResponse("main.html", {
        "request": request,
    })