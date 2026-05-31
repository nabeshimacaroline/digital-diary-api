import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError # Importação nova do PyJWT
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models import User

# ==========================================
# 1. AS CONSTANTES 
# ==========================================

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # A pulseirinha vale por 30 minutos

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================================
# 2. HASHING
# ==========================================

def get_password_hash(password: str) ->str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ==========================================
# 3. CRIAÇÃO DE TOKEN
# ==========================================

def create_access_token(data: dict) -> str:
    # Cópia dos dados do utilizador para não estragar o original
    to_encode = data.copy()
    
    # Calculo de que horas serão daqui a 30 minutos
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Colar a etiqueta de validade ("exp") na cópia
    to_encode.update({"exp": expire})
    
    # PyJWT pega nos dados, na nossa chave secreta e tritura tudo num Token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# 1. O LEITOR ÓPTICO DO TORNIQUETE
# Avisamos o FastAPI onde é que os utilizadores vão buscar a pulseira
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# 2. O SEGURANÇA DA PISTA DE DANÇA
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Preparamos o erro padrão caso algo corra mal
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Passo A: O segurança tenta ler a pulseira (descodificar o JWT)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") # Extraímos o email que guardámos lá dentro
        
        if email is None:
            raise credentials_exception
            
    except InvalidTokenError:
        # Passo B: Se a pulseira for falsa, estiver adulterada ou caducada, barramos!
        raise credentials_exception
        
    # Passo C: O email é válido! Vamos à base de dados buscar o dono (utilizador)
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise credentials_exception
        
    # Passo D: O utilizador existe e a pulseira é válida. Pode entrar!
    return user