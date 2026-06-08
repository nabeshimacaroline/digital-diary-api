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


