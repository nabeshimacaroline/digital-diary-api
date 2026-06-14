import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import get_password_hash

# O motor do banco falso (em memória RAM)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# A fabrica de sessões do banco falso
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A Fixture (Setup e Teardown)
@pytest.fixture(autouse=True )
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Função Duble
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Aplicando a substituição do FastAPI
app.dependency_overrides[get_db] = override_get_db

# O Cliente de Teste (nosso robô)
@pytest.fixture()
def client():
    return TestClient(app)


#criação do usuário teste
@pytest.fixture()
def test_user(db_session):

    email = "carol@test.com"
    username = "Carol"
    plain_password = "senhaSegura123"

    user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(plain_password)
        )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    yield{"user": user, "email": email, "password": plain_password}

    try:
        db_session.delete(user)
        db_session.commit()

    except Exception:
        db_session.rollback()