from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# O endereço do nosso banco de dados local
SQLALCHEMY_DATABASE_URL = "sqlite:///./diario.db"

# A Estrada (O parâmetro check_same_thread é uma exigência específica do SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# A Fábrica de Caminhões (Sessões)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# O Molde Base para as nossas futuras tabelas
Base = declarative_base()