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

def test_get_notes_isolation(client):
    # ==========================================
    # 1. ARRANGE (A preparação do palco)
    # ==========================================
    
    # Criando o Usuário 1 (Carol) e pegando o token
    client.post(
        "/users/",
        json={
        "email": "carol@teste.com", 
        "username": "Carol", 
        "password": "senhaSegura123", 
        "confirm_password": "senhaSegura123"
        })
    token_carol = client.post(
        "/users/login", 
        data={
        "username": "carol@teste.com", 
        "password": "senhaSegura123"
        }).json()["access_token"]
    headers_carol = {"Authorization": f"Bearer {token_carol}"}

    # Criando o Usuário 2 (João) e pegando o token
    client.post(
        "/users/", 
        json={
        "email": "joao@teste.com",
        "username": "Joao", 
        "password": "senhaSegura123", 
        "confirm_password": "senhaSegura123"
        })
    token_joao = client.post(
        "/users/login", 
        data={
        "username": "joao@teste.com", 
        "password": "senhaSegura123"
        }).json()["access_token"]
    headers_joao = {"Authorization": f"Bearer {token_joao}"}

    # Criando 1 Nota para a Carol
    client.post("/notes/", json={"category": "pessoal", "message_body": "Nota secreta da Carol"}, headers=headers_carol)
    
    # Criando 2 Notas para o João
    client.post("/notes/", json={"category": "trabalho", "message_body": "Nota do Joao 1"}, headers=headers_joao)
    client.post("/notes/", json={"category": "trabalho", "message_body": "Nota do Joao 2"}, headers=headers_joao)

    # ==========================================
    # 2. ACT
    # ==========================================
    # O nosso robô (fingindo ser a Carol), vai chamar a rota GET /notes/
    # Escreva a linha para fazer essa requisição usando o client:
    resposta_listagem_carol = client.get("/notes/", headers=headers_carol)

    # ==========================================
    # 3. ASSERT
    # ==========================================
    # O banco de dados tem 3 notas no total. Mas a Carol só tem 1.
    # 1. Verifique se o status_code é 200 (Sucesso)
    # 2. Extraia o JSON da resposta (que será uma lista do Python)
    # 3. Verifique se o tamanho dessa lista é exatamente 1 (Garantindo que as 2 notas do João não vieram)
    # 4. Verifique se o message_body da nota que veio é "Nota secreta da Carol"
    
    assert resposta_listagem_carol.status_code == 200

    notes_carol = resposta_listagem_carol.json()

    assert len(notes_carol) == 1
    assert notes_carol[0]["message_body"] == "Nota secreta da Carol"

def test_unauthenticated_access_returns_401(client):

    # ==========================================
    # 1. ARRANGE (A preparação do palco)
    # ==========================================

    #Carol
    client.post(
        "/users/", 
        json={
            "email": "carol@teste.com",
            "username": "carol",
            "password": "senhaSegura123",
            "confirm_password": "senhaSegura123"
        }
    )
    token_carol = client.post(
        "/users/login",
        data={
        "username": "carol@teste.com",
        "password": "senhaSegura123"
        }
    ).json()["access_token"]
    headers_carol = {"Authorization": f"Bearer {token_carol}"}

    #Joao
    client.post(
        "/users/",
        json={
            "email": "joao@teste.com",
            "username": "joao",
            "password": "senhaSegura123",
            "confirm_password": "senhaSegura123"
        }
    )
    token_joao = client.post(
        "/users/login",
        data={
            "username": "joao@teste.com",
            "password": "senhaSegura123"
        }
    ).json()["access_token"]
    headers_joao = {"Authorization": f"Bearer {token_joao}"}

    #nota joao
    resposta_nota_joao = client.post("/notes/", json={"category": "estudos", "message_body": "Nota secreta 1534"}, headers=headers_joao)
    id_joao = resposta_nota_joao.json()["id"]

    # ==========================================
    # 2. ACT
    # ==========================================
    #tentativa da Carol de acessar notas de joao

    resposta_nota_carol = client.get(f"/notes/{id_joao}", headers=headers_carol)

    # ==========================================
    # 3. ASSERT
    # ==========================================

    assert resposta_nota_carol.status_code == 404

rotas_protegidas_notas = [
    ("POST", "/notes/"),
    ("GET", "/notes/"),
    ("GET", "/notes/1"),
    ("PATCH", "/notes/1"),
    ("DELETE", "/notes/1")
]

@pytest.mark.parametrize("method, route", rotas_protegidas_notas)
def test_create_note_missing_required_fields(client, method, route):
    

    # ==========================================
    # 2. ACT
    # ==========================================
   
    resposta = client.request(method, route)
        
    # ==========================================
    # 3. ASSERT
    # ==========================================

    assert resposta.status_code == 401

def test_update_note_success(client):
# ==========================================
# 1. ARRANGE
# ==========================================    
    client.post(
        "/users/",
        json={
            "email": "carol@teste.com",
            "username": "Carol",
            "password": "senhaSegura123",
            "confirm_password": "senhaSegura123"
        }
    )
    token_carol = client.post(
        "/users/login",
        data={
            "username": "carol@teste.com",
            "password": "senhaSegura123"
        }
    ).json()["access_token"]
    headers_carol = {"Authorization": f"Bearer {token_carol}"}

    nota_carol = client.post("/notes/", json={"category": "estudos", "message_body": "Nota original"}, headers=headers_carol)
    id_carol = nota_carol.json()["id"]

# ==========================================
# 2. ACT
# ==========================================  
 #tentativa de atualização

    payload_atualizacao =  {"message_body": "Nota atualizada com sucesso!"}

    atualizacao_nota = client.patch(f"/notes/{id_carol}", json=payload_atualizacao, headers=headers_carol)

# ==========================================
# 3. ASSERT
# ==========================================
    assert atualizacao_nota.status_code == 200

    nota_atualizada = atualizacao_nota.json()
    assert nota_atualizada["message_body"] == "Nota atualizada com sucesso!"

    conferencia_banco = client.get(f"/notes/{id_carol}", headers=headers_carol)
    assert conferencia_banco.json()["message_body"] == "Nota atualizada com sucesso!"

def test_update_other_user_note_returns_404(client):
# ==========================================
# 1. ARRANGE
# ==========================================    
    client.post(
        "/users/",
        json={
            "email": "carol@teste.com",
            "username": "Carol",
            "password": "senhaSegura123",
            "confirm_password": "senhaSegura123"
        }
    )
    token_carol = client.post(
        "/users/login",
        data={
            "username": "carol@teste.com",
            "password": "senhaSegura123"
        }
    ).json()["access_token"]
    headers_carol = {"Authorization": f"Bearer {token_carol}"}

    client.post(
        "/users/",
        json={
            "email": "joao@teste.com",
            "username": "Joao",
            "password": "senhaSegura123",
            "confirm_password": "senhaSegura123"
        }
    )
    token_joao = client.post(
        "/users/login",
        data={
            "username": "joao@teste.com",
            "password": "senhaSegura123"
        }
    ).json()["access_token"]
    headers_joao = {"Authorization": f"Bearer {token_joao}"}

    nota_joao = client.post("/notes/", json={"category": "estudos", "message_body": "Nota secreta João."}, headers=headers_joao)
    id_joao = nota_joao.json()["id"]

# ==========================================
# 2. ACT
# ==========================================   
    payload_carol = {"message_body": "Hacker Carol esteve aqui"}

    update_attempt_carol = client.patch(f"/notes/{id_joao}", json=payload_carol, headers=headers_carol)

# ==========================================
# 3. ASSERT
# ==========================================   
    assert update_attempt_carol.status_code == 404

def test_delete_note_success(client):
# ==========================================
# 1. ARRANGE
# ========================================== 
    client.post(
        "/users/",
        json={
            "email": "carol@teste.com",
            "username": "Carol",
            "password": "senhaSegura123",
            "confirm_password": "senhaSegura123"
        }
    )
    token_carol = client.post(
        "/users/login",
        data={
            "username": "carol@teste.com",
            "password": "senhaSegura123"
        }
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token_carol}"}

    nota_carol = client.post("/notes/", json={"category": "estudos", "message_body": "Nota teste 123"}, headers=headers)
    id_carol = nota_carol.json()["id"]

# ==========================================
# 2. ACT
# ==========================================
    tentativa_delecao_nota = client.delete(f"/notes/{id_carol}", headers=headers)

# ==========================================
# 3. ASSERT
# ==========================================
    assert tentativa_delecao_nota.status_code == 204
    
    conferencia_banco = client.get(f"/notes/{id_carol}", headers=headers)
    assert conferencia_banco.status_code == 404

def test_delete_other_user_note_returns_404(client):
# ==========================================
# 1. ARRANGE
# ==========================================   
    client.post(
        "/users/",
        json={
            "email": "carol@teste.com",
            "username": "Carol",
            "password": "senhaSegura123",
            "confirm_password": "senhaSegura123"
        }
    )
    token_carol = client.post(
        "/users/login",
        data={
            "username": "carol@teste.com",
            "password": "senhaSegura123"
        }
    ).json()["access_token"]
    headers_carol = {"Authorization": f"Bearer {token_carol}"}

    client.post(
        "/users/",
        json={
            "email": "joao@teste.com",
            "username": "Joao",
            "password": "senhaSegura123",
            "confirm_password": "senhaSegura123"
        }
    )
    token_joao = client.post(
        "/users/login",
        data={
            "username": "joao@teste.com",
            "password": "senhaSegura123"
        }
    ).json()["access_token"]
    headers_joao = {"Authorization": f"Bearer {token_joao}"}

    nota_joao = client.post("/notes/", json={"category": "estudos", "message_body": "Nota secreta João."}, headers=headers_joao)
    id_joao = nota_joao.json()["id"]

# ==========================================
# 2. ACT
# ==========================================
    tentativa_delecao_carol = client.delete(f"/notes/{id_joao}", headers=headers_carol)

# ==========================================
# 3. ASSERT
# ==========================================
    assert tentativa_delecao_carol.status_code == 404

    checagem_banco_joao = client.get(f"/notes/{id_joao}", headers=headers_joao)
    assert checagem_banco_joao.json()["message_body"] == "Nota secreta João."