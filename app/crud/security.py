import re
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import  HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from Crypto.Cipher import AES
import hashlib
import json
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

import app.models as models
import app.schemas as schemas
import app.crud as crud
from app.dependecies import *
from app.crud  import *

SECRET_KEY = "41cf6049116ed36440bd2fc311485f89d3a485bf05e97a3ac03412566abb21f0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["argon2"]) #, deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    print("jwt token ", to_encode)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_auth_header_if_correct_credentials(db: Session, username: str, password: str):
    try:
        check_username(username)
        check_password(password)
        
        user = authenticate_user(db, username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = create_access_token(data={"sub": username})
        return {"access_token": token, "token_type": "bearer"}    
    except:
        return False

def check_username(username: str):
    # a-z, A-Z, 0-9, 6-20 chars
    assert username.isalnum()
    assert 6 <= len(username) <= 20
    return True

def check_password(password: str):
    # 6-20 chars, at least one: A-Z, a-z, special character, 0-9 
    reg_exp = '^(?=\S{6,20}$)(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])'
    assert re.search(reg_exp, password) != None   
    return True

def check_if_passwords_are_identical(password_1: str, password_2: str):
    if password_1 == password_2:
        return True
    else: 
        raise ValueError("passwords must be identical")

def authenticate_user(db:Session, username: str, password: str):
    user = crud.get_user_by_username(db=db, username=username)
    if not user:
        return False
    if not verify_password(plain_password=password, hashed_password=user.hashed_password):
        return False
    return user


def encrypt_markdown(plaintext, key):
    encobj = AES.new(key, AES.MODE_GCM)
    ciphertext,authTag=encobj.encrypt_and_digest(plaintext)
    res_dict = {
        "ciphertext": str(list(ciphertext)),
        "authTag": str(list(authTag)),
        "nonce": str(list(encobj.nonce))
    }
    return json.dumps(res_dict)

def get_encrypted_markdown(note: str, password: str):
    key = hashlib.sha256(password.encode()).digest()
    encrypted_markdown = encrypt_markdown(note.encode(), key)
    return encrypted_markdown

def get_decrypted_markdown(note: schemas.NoteWithPassword, password: str):
    if verify_password(password, note.hashed_password):
        key = hashlib.sha256(password.encode()).digest()
        decrypted_markdown = decrypt_markdown(note.markdown_encrypted, key)
        return decrypted_markdown.decode()
    else:
        return False

def decrypt_markdown(ciphertext, key):
    ciphertext_dict = json.loads(ciphertext)
    authTag = bytes(eval(ciphertext_dict["authTag"]))
    ciphertext = bytes(eval(ciphertext_dict["ciphertext"]))
    nonce = bytes(eval(ciphertext_dict["nonce"]))
    encobj = AES.new(key,  AES.MODE_GCM, nonce)
    return encobj.decrypt_and_verify(ciphertext, authTag)

def check_if_username_in_db(db: Session, username: str):
    stmt = select(models.User).where(models.User.username == username)
    user = db.scalar(stmt)
    if user:
        raise ValueError("Duplicate username")
    else: 
        return False




