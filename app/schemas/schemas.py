from fastapi import Form
from pydantic import BaseModel
from typing import List, Optional

# USERS

class UserBase(BaseModel):
    username: str
    
    class Config:
        orm_model = True

class UserWithPassword(UserBase):
    hashed_password: str
    
class User(UserBase):
    id: int
    notes: List['Note']

class UserCreate(UserBase):
    password: str


# NOTES

class NoteBase(BaseModel):
    id: int
    public: bool
    
    class Config:
        orm_mode=True
    
class NoteCreate(NoteBase):
    password: Optional[str]
    markdown: str
    
class Note(NoteBase):
    owner_id: int
    markdown_encrypted: str
    
class NoteWithPassword(Note):
    hashed_password: Optional[str]

class NotesList(BaseModel):
    notes: List[int]
    
# TOKENS

class Token(BaseModel):
    access_token: str
    token_type: str    

class TokenData(BaseModel):
    username: str | None = None


User.update_forward_refs()

