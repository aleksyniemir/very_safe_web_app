from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    notes = relationship("Note")

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    markdown_encrypted = Column(String)
    public = Column(Boolean)
    hashed_password = Column(String, nullable=True)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    