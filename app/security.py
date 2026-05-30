import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

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