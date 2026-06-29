import pytest
from freezegun import freeze_time

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

