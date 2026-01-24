from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from pydantic import BaseModel
from typing import Optional

# Quick & Dirty Auth for Hackathon (Plaintext/Simple hashing if possible, but keep it simple)
# For production, use bcrypt + JWT. Here we will use simple session simulation or just return user ID.

router = APIRouter(tags=["Auth"])

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user" # 'user' or 'authority'

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # In a real app, HASH THIS PASSWORD!
    fake_hashed_password = user.password + "notreallyhashed"
    
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=fake_hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id, "role": new_user.role}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Check user
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
        
    # Verify password (mock)
    if db_user.hashed_password != user.password + "notreallyhashed":
         raise HTTPException(status_code=400, detail="Invalid credentials")
         
    return {
        "access_token": f"fake-token-{db_user.id}", 
        "token_type": "bearer", 
        "user_id": db_user.id,
        "name": db_user.name,
        "role": db_user.role
    }
