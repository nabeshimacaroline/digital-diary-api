import pytest
from freezegun import freeze_time
from app.enums import StatusEvent

@pytest.fixture(autouse=True)
def freeze_time_for_events():
    with freeze_time("2026-06-27T10:00:00Z"):
        yield


def test_create_event_in_past_date(authorized_client):
# ==========================================
# 1. ARRANGE
# ==========================================
    event_payload = {
        "category": "projeto",
        "message_body": "Tentativa de criação de evento no passado",
        "classification": "tarefa",
        "scheduled_at": "2026-04-25T09:00:05Z"
    }

# ==========================================
# 2. ACT
# ==========================================
    event_attempt = authorized_client.post("/events/", json=event_payload)

# ==========================================
# 3. ASSERT
# ==========================================
    
    assert event_attempt.status_code == 400
    assert event_attempt.json()["detail"] == "Scheduled cannot be a date in the past."

def test_creat_event_success(authorized_client):
# ==========================================
# 1. ARRANGE
# ==========================================
    event_payload = {
        "category": "projeto",
        "message_body": "Teste caminho feliz para criação de eventos",
        "classification": "tarefa",
        "scheduled_at": "2026-07-08T09:00:00Z"
    }
# ==========================================
# 2. ACT
# ==========================================
    event_attempt = authorized_client.post("/events/", json=event_payload)

# ==========================================
# 3. ASSERT
# ==========================================
    assert event_attempt.status_code == 201
    assert event_attempt.json()["status"] == StatusEvent.SCHEDULED

def test_create_event_with_linked_note_success(authorized_client):
# ==========================================
# 1. ARRANGE
# ==========================================
    note_create = authorized_client.post("/notes/", json={
        "category": "projeto",
        "message_body": "Nota mãe"
    })

    assert note_create.status_code == 201

    note_id = note_create.json()["id"]
    payload_event = {
        "note_id": note_id,
        "category": "projeto",
        "message_body": "Teste de criação de Evento vinculado à Nota",
        "classification": "tarefa",
        "scheduled_at": "2026-10-18T10:00:00Z"
    }

# ==========================================
# 2. ACT
# ==========================================
    event_attempt = authorized_client.post("/events/", json=payload_event)

# ==========================================
# 3. ASSERT
# ==========================================
    assert event_attempt.status_code == 201
    assert event_attempt.json()["status"] == StatusEvent.SCHEDULED
    assert event_attempt.json()["note_id"] == note_id   

def test_create_event_with_nonexistent_note_returns_404(authorized_client):
# ==========================================
# 1. ARRANGE
# ==========================================
    event_payload = {
        "note_id": "9999", 
        "category": "projeto",
        "message_body": "Tentativa de criar um evento sem saber o note_id",
        "classification": "tarefa",
        "scheduled_at": "2026-10-18T09:00:00Z"
    }

# ==========================================
# 2. ACT
# ==========================================
    event_attempt = authorized_client.post("/events/", json=event_payload)

# ==========================================
# 3. ASSERT
# ==========================================
    assert event_attempt.status_code == 404

def test_patch_event_with_nonexistent_note_returns_404(authorized_client):
# ==========================================
# 1. ARRANGE
# ==========================================
    note_create = authorized_client.post("/notes/", json={
        "category": "projeto",
        "message_body": "Nota mãe para teste de blindagem em edições"
    })
    assert note_create.status_code == 201
    note_id = note_create.json()["id"]

    event_create = authorized_client.post("/events/", json={
        "note_id": note_id,
        "category": "projeto",
        "message_body": "Evento para edição",
        "classification": "tarefa",
        "scheduled_at": "2026-10-18T03:00:00Z"
    })
    assert event_create.status_code == 201
    event_id = event_create.json()["id"]

# ==========================================
# 2. ACT
# ==========================================
    event_patch_attempt = authorized_client.patch(f"/events/{event_id}", json={
        "note_id": 9999,
        "category": "projeto",
        "message_body": "Tentativa de edição com note_id invalido",
        "classification": "tarefa",
        "scheduled_at": "2026-10-18T03:00:00Z"
    })

# ==========================================
# 3. ASSERT
# ==========================================
    assert event_patch_attempt.status_code == 404
    assert event_patch_attempt.json()["detail"] == "Note not found"