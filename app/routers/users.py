from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.security import get_password_hash, verify_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=201)
def creat_user(payload:UserCreate, db: Session = Depends(get_db)):
    #Checagem de Email
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    #Checagem de username
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    pw_hashed = get_password_hash(payload.password)

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=pw_hashed
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user