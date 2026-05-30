from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, LoginRequest, Token
from app.security import get_password_hash, verify_password, create_access_token    

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

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 1. Procurar no banco se há cadastro do email enviado pelo usuário
    user = db.query(User).filter(User.email == payload.email).first()

    # 2. Validação
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 3. Usuário valido ->informação da autorização para a geração do Token
    access_token = create_access_token(data={"sub":user.email})

    # 4. Envio para a criação (Schemas)
    return {"access_token": access_token, "token_type":"bearer"}