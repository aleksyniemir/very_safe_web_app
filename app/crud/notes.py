from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

import app.schemas as schemas
import app.models as models
import app.crud as crud
from app.dependecies import *
from app.crud.security import *
from app.crud  import *

templates = Jinja2Templates(directory="app/templates")

def get_note_by_id(db: Session, note_id: int):
    stmt = select(models.Note).where(models.Note.id==note_id)
    return db.scalar(stmt)

def get_all_notes(db: Session):
    stmt = select(models.Note)
    return db.scalars(stmt).all()

def get_current_users_notes_id(db: Session, current_user: schemas.User):
    stmt = select(models.Note).where(models.Note.owner_id == current_user.id)
    notes = db.scalars(stmt).all()
    notes_id = []
    for note in notes:
        notes_id.append(schemas.NoteBase.from_orm(note))
    notes_id_to_print = []
    for schema in notes_id:
        notes_id_to_print.append({"id" : schema.id, "public": schema.public})
    return notes_id_to_print



def add_note(db: Session, user: schemas.User, note: str, password: str | None = None):
    if password:
        hashed_password = crud.get_password_hash(password)
        public = False
        markdown_encrypted = crud.get_encrypted_markdown(note, password) 
    else:
        hashed_password = None
        public = True
        markdown_encrypted = note
    new_note = models.Note(
        markdown_encrypted=markdown_encrypted,
        public=public,
        hashed_password=hashed_password,
        owner_id=user.id
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

