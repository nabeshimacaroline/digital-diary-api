import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi.testclient import TestClient

from app.database import Base, get_db, SessionLocal
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
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    

# Função Duble
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Aplicando a substituição do FastAPI
app.dependency_overrides[get_db] = override_get_db
@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try: 
        yield db
    finally: 
        db.close()


# O Cliente de Teste (nosso robô)
@pytest.fixture()
def client():
    return TestClient(app)


#criação do usuário teste
@pytest.fixture()
def test_user(client):
    # 1. Geramos as credenciais únicas
    codigo = str(uuid.uuid4())[:6]
    email = f"carol_{codigo}@teste.com"
    username = f"Carol_{codigo}"
    password = "senhaSegura123"

    # 2. CAIXA PRETA: Mandamos a própria API criar a usuária.
    # Isso garante que 100% das regras e transações do banco sejam respeitadas.
    response = client.post(
        "/users/",
        json={
            "email": email,
            "username": username,
            "password": password,
            "confirm_password": password
        }
    )
    
    # Armadilha de segurança para a criação
    if response.status_code not in (200, 201):
        raise ValueError(f"Falha ao criar usuária na Fixture! Servidor respondeu: {response.text}")

    # 3. Retornamos as chaves para a fixture authorized_client fazer o login
    return {"email": email, "password": password}

@pytest.fixture
def authorized_client(client, test_user):
    # 1. Fazemos a requisição e guardamos a resposta inteira na variável
    response = client.post(
        "/users/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    
    # 2. A ARMADILHA: Se o login falhar, paramos tudo e imprimimos o erro do servidor!
    if response.status_code != 200:
        raise ValueError(f"Falha no Login! Servidor respondeu: {response.status_code} - {response.text}")

 
    token = response.json()["access_token"]
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client