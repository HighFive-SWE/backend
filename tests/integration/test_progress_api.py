"""Integration tests for POST /progress and GET /progress/{profile_id}."""

import uuid


def _progress_payload(**overrides) -> dict:
    defaults = {
        "profile_id": "profile-alex",
        "routine_id": "greet-family",
        "gesture_id": "hello",
        "accuracy": 0.85,
        "band": "correct",
        "attempts": 1,
        "succeeded": True,
    }
    return {**defaults, **overrides}


# ── record ─────────────────────────────────────────────────────────────────────

def test_record_progress_returns_200(client):
    resp = client.post("/progress", json=_progress_payload())
    assert resp.status_code == 200


def test_record_progress_body_has_record(client):
    body = client.post("/progress", json=_progress_payload()).json()
    assert "record" in body


def test_record_progress_body_has_summary(client):
    body = client.post("/progress", json=_progress_payload()).json()
    assert "summary" in body


def test_record_progress_body_has_xp_gained(client):
    body = client.post("/progress", json=_progress_payload()).json()
    assert "xp_gained" in body


def test_record_progress_body_has_new_achievements(client):
    body = client.post("/progress", json=_progress_payload()).json()
    assert "new_achievements" in body
    assert isinstance(body["new_achievements"], list)


def test_record_progress_xp_gained_is_positive(client):
    body = client.post("/progress", json=_progress_payload(succeeded=True)).json()
    assert body["xp_gained"] > 0


def test_record_progress_xp_gained_zero_on_failure(client):
    body = client.post("/progress", json=_progress_payload(accuracy=0.1, band="incorrect", succeeded=False)).json()
    assert body["xp_gained"] == 0


def test_record_progress_unknown_profile_returns_404(client):
    resp = client.post("/progress", json=_progress_payload(profile_id="nonexistent-profile"))
    assert resp.status_code == 404


def test_record_progress_invalid_band_returns_422(client):
    resp = client.post("/progress", json=_progress_payload(band="excellent"))
    assert resp.status_code == 422


def test_record_progress_accuracy_out_of_range_returns_422(client):
    resp = client.post("/progress", json=_progress_payload(accuracy=1.5))
    assert resp.status_code == 422


def test_record_progress_attempts_zero_returns_422(client):
    resp = client.post("/progress", json=_progress_payload(attempts=0))
    assert resp.status_code == 422


def test_record_progress_invalid_incorrect_point_returns_422(client):
    resp = client.post("/progress", json=_progress_payload(incorrect_points=[21]))
    assert resp.status_code == 422


def test_record_progress_completed_routine_flag(client):
    body = client.post("/progress", json=_progress_payload(completed_routine=True)).json()
    assert body["summary"]["routines_completed"]


# ── idempotency ───────────────────────────────────────────────────────────────

def test_idempotency_same_key_returns_same_response(client):
    key = f"idem-{uuid.uuid4().hex[:12]}"
    payload = _progress_payload(idempotency_key=key)
    first = client.post("/progress", json=payload).json()
    second = client.post("/progress", json=payload).json()
    assert first["record"]["gesture_id"] == second["record"]["gesture_id"]
    assert first["summary"]["total_attempts"] == second["summary"]["total_attempts"]


def test_idempotency_different_keys_both_recorded(client):
    key_a = f"idem-a-{uuid.uuid4().hex[:12]}"
    key_b = f"idem-b-{uuid.uuid4().hex[:12]}"
    resp_a = client.post("/progress", json=_progress_payload(idempotency_key=key_a))
    resp_b = client.post("/progress", json=_progress_payload(idempotency_key=key_b))
    assert resp_a.status_code == 200
    assert resp_b.status_code == 200
    assert resp_a.json()["summary"]["total_attempts"] < resp_b.json()["summary"]["total_attempts"]


# ── get progress ──────────────────────────────────────────────────────────────

def test_get_progress_returns_200(client):
    resp = client.get("/progress/profile-alex")
    assert resp.status_code == 200


def test_get_progress_body_has_summary(client):
    body = client.get("/progress/profile-alex").json()
    assert "summary" in body


def test_get_progress_body_has_recent(client):
    body = client.get("/progress/profile-alex").json()
    assert "recent" in body
    assert isinstance(body["recent"], list)


def test_get_progress_summary_has_expected_fields(client):
    summary = client.get("/progress/profile-alex").json()["summary"]
    assert "total_attempts" in summary
    assert "avg_accuracy" in summary
    assert "total_xp" in summary
    assert "level" in summary
    assert "current_streak" in summary
    assert "daily_goal" in summary


def test_get_progress_nonempty_after_recording(client):
    client.post("/progress", json=_progress_payload())
    body = client.get("/progress/profile-alex").json()
    assert body["summary"]["total_attempts"] > 0


def test_get_progress_custom_limit(client):
    resp = client.get("/progress/profile-alex?limit=3")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["recent"]) <= 3


def test_get_progress_limit_zero_returns_422(client):
    resp = client.get("/progress/profile-alex?limit=0")
    assert resp.status_code == 422
