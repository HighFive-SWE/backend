"""Integration tests for POST /cv/evaluate and GET /cv/results."""

from tests.integration.conftest import landmarks_for


# ── evaluate ──────────────────────────────────────────────────────────────────

def test_evaluate_returns_200(client):
    payload = {"gesture_id": "hello", "landmarks": landmarks_for("hello")}
    resp = client.post("/cv/evaluate", json=payload)
    assert resp.status_code == 200


def test_evaluate_body_has_accuracy(client):
    payload = {"gesture_id": "hello", "landmarks": landmarks_for("hello")}
    body = client.post("/cv/evaluate", json=payload).json()
    assert "accuracy" in body


def test_evaluate_body_has_band(client):
    payload = {"gesture_id": "hello", "landmarks": landmarks_for("hello")}
    body = client.post("/cv/evaluate", json=payload).json()
    assert "band" in body


def test_evaluate_body_has_suggestion(client):
    payload = {"gesture_id": "hello", "landmarks": landmarks_for("hello")}
    body = client.post("/cv/evaluate", json=payload).json()
    assert "suggestion" in body


def test_evaluate_accuracy_in_range(client):
    payload = {"gesture_id": "hello", "landmarks": landmarks_for("hello")}
    body = client.post("/cv/evaluate", json=payload).json()
    assert 0.0 <= body["accuracy"] <= 1.0


def test_evaluate_band_is_valid(client):
    payload = {"gesture_id": "hello", "landmarks": landmarks_for("hello")}
    body = client.post("/cv/evaluate", json=payload).json()
    assert body["band"] in {"correct", "partial", "incorrect"}


def test_evaluate_identical_gesture_is_correct_band(client):
    payload = {"gesture_id": "hello", "landmarks": landmarks_for("hello")}
    body = client.post("/cv/evaluate", json=payload).json()
    assert body["band"] == "correct"


def test_evaluate_identical_gesture_high_accuracy(client):
    payload = {"gesture_id": "hello", "landmarks": landmarks_for("hello")}
    body = client.post("/cv/evaluate", json=payload).json()
    assert body["accuracy"] > 0.9


def test_evaluate_incorrect_points_is_list(client):
    payload = {"gesture_id": "hello", "landmarks": landmarks_for("hello")}
    body = client.post("/cv/evaluate", json=payload).json()
    assert isinstance(body["incorrect_points"], list)


def test_evaluate_with_user_id_returns_200(client):
    payload = {
        "gesture_id": "hello",
        "landmarks": landmarks_for("hello"),
        "user_id": "user-home-1",
    }
    resp = client.post("/cv/evaluate", json=payload)
    assert resp.status_code == 200


def test_evaluate_unknown_gesture_returns_404(client):
    payload = {"gesture_id": "not-a-real-gesture", "landmarks": landmarks_for("hello")}
    resp = client.post("/cv/evaluate", json=payload)
    assert resp.status_code == 404


def test_evaluate_wrong_landmark_count_returns_422(client):
    bad_landmarks = landmarks_for("hello")[:10]
    payload = {"gesture_id": "hello", "landmarks": bad_landmarks}
    resp = client.post("/cv/evaluate", json=payload)
    assert resp.status_code == 422


def test_evaluate_empty_landmarks_returns_422(client):
    payload = {"gesture_id": "hello", "landmarks": []}
    resp = client.post("/cv/evaluate", json=payload)
    assert resp.status_code == 422


def test_evaluate_missing_gesture_id_returns_422(client):
    payload = {"landmarks": landmarks_for("hello")}
    resp = client.post("/cv/evaluate", json=payload)
    assert resp.status_code == 422


# ── results ───────────────────────────────────────────────────────────────────

def test_recent_results_returns_200(client):
    resp = client.get("/cv/results")
    assert resp.status_code == 200


def test_recent_results_has_results_key(client):
    body = client.get("/cv/results").json()
    assert "results" in body


def test_recent_results_is_list(client):
    body = client.get("/cv/results").json()
    assert isinstance(body["results"], list)


def test_recent_results_nonempty_after_evaluate(client):
    client.post("/cv/evaluate", json={"gesture_id": "hello", "landmarks": landmarks_for("hello")})
    body = client.get("/cv/results").json()
    assert len(body["results"]) > 0


def test_recent_results_first_item_has_gesture_id(client):
    client.post("/cv/evaluate", json={"gesture_id": "water", "landmarks": landmarks_for("water")})
    body = client.get("/cv/results").json()
    assert "gesture_id" in body["results"][0]


def test_recent_results_custom_limit(client):
    resp = client.get("/cv/results?limit=2")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["results"]) <= 2


def test_recent_results_limit_too_large_returns_422(client):
    resp = client.get("/cv/results?limit=999")
    assert resp.status_code == 422


def test_recent_results_limit_zero_returns_422(client):
    resp = client.get("/cv/results?limit=0")
    assert resp.status_code == 422
