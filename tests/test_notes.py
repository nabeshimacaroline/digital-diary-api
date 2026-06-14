import pytest

def test_create_note_success(client):
    # ==========================================
    # 1. ARRANGE (Preparar o terreno)
    # ==========================================
    
    # Criação do usuário
    client.post(
        "/users/", 
        json={
            "email": "carol@teste.com", 
            "username": "Carol", 
            "password": "senhaSegura123", 
            "confirm_password": "senhaSegura123"
        }
    )

    # Fazer login
    resposta_login = client.post(
        "/users/login",
        data = {
            "username": "carol@teste.com",
            "password": "senhaSegura123"
        }
    )

    # Pegar a chave e montar o cabeçalho
    token = resposta_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ==========================================
    # 2. ACT
    # ==========================================

    note_payload = {
        "category": "estudos",
        "message_body": "Minha primeira nota automatizada"
        }

    resposta_nota = client.post("/notes/", json=note_payload, headers=headers)

    # ==========================================
    # 3. ASSERT
    # ==========================================

    assert resposta_nota.status_code == 201

    data = resposta_nota.json()
    assert data["category"] == "estudos"
    assert data["message_body"] == "Minha primeira nota automatizada"



# payloads inválidos: (case, body)
invalid_note_payloads = [
    ("category vazio", {"category": "", "message_body": "Minha primeira nota automatizada"}),
    ("message_body vazio", {"category": "estudos", "message_body": ""}),
    ("category ausente", {"message_body": "Minha primeira nota automatizadaTexto válido"}),
    ("message_body ausente", {"category": "estudos"}),
    ("ambos vazios", {"category": "", "message_body": ""}),
]

@pytest.mark.parametrize("case, payload", invalid_note_payloads)
def test_create_note_missing_required_fields(client, case, payload):
    # ==========================================
    # 1. ARRANGE (A mesma preparação do teste anterior)
    # ==========================================
    client.post(
    "/users/",
    json={
    "email": "carol@teste.com",
    "username": "Carol",
    "password": "senhaSegura123",
    "confirm_password": "senhaSegura123"
    })
    resposta_login = client.post(
    "/users/login",
    data={
    "username": "carol@teste.com",
    "password": "senhaSegura123"
    })
    token = resposta_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ==========================================
    # 2. ACT
    # ==========================================
   
    resposta_nota = client.post("/notes/", json=payload, headers=headers)
        
    # ==========================================
    # 3. ASSERT
    # ==========================================

    assert resposta_nota.status_code == 422
