"""Integration tests for GET /analytics/{profile_id}."""


def _seed_progress(client, profile_id: str, gesture_id: str = "hello", n: int = 1) -> None:
    payload = {
        "profile_id": profile_id,
        "routine_id": "greet-family",
        "gesture_id": gesture_id,
        "accuracy": 0.75,
        "band": "correct",
        "attempts": 1,
        "succeeded": True,
    }
    for _ in range(n):
        client.post("/progress", json=payload)


# ── basic response shape ──────────────────────────────────────────────────────

def test_get_analytics_returns_200(client):
    resp = client.get("/analytics/profile-alex")
    assert resp.status_code == 200


def test_get_analytics_body_has_analytics_key(client):
    body = client.get("/analytics/profile-alex").json()
    assert "analytics" in body


def test_get_analytics_has_profile_id(client):
    analytics = client.get("/analytics/profile-alex").json()["analytics"]
    assert analytics["profile_id"] == "profile-alex"


def test_get_analytics_has_required_fields(client):
    analytics = client.get("/analytics/profile-alex").json()["analytics"]
    assert "sample_size" in analytics
    assert "avg_accuracy" in analytics
    assert "success_rate" in analytics
    assert "weak_gestures" in analytics
    assert "trend" in analytics
    assert "finger_heat" in analytics


def test_get_analytics_unknown_profile_returns_404(client):
    resp = client.get("/analytics/no-such-profile")
    assert resp.status_code == 404


def test_get_analytics_sample_size_non_negative(client):
    analytics = client.get("/analytics/profile-alex").json()["analytics"]
    assert analytics["sample_size"] >= 0


def test_get_analytics_avg_accuracy_in_range(client):
    analytics = client.get("/analytics/profile-alex").json()["analytics"]
    assert 0.0 <= analytics["avg_accuracy"] <= 1.0


def test_get_analytics_success_rate_in_range(client):
    analytics = client.get("/analytics/profile-alex").json()["analytics"]
    assert 0.0 <= analytics["success_rate"] <= 1.0


# ── populated data ────────────────────────────────────────────────────────────

def test_get_analytics_sample_size_grows_after_progress(client):
    before = client.get("/analytics/profile-sam").json()["analytics"]["sample_size"]
    _seed_progress(client, "profile-sam", gesture_id="water", n=2)
    after = client.get("/analytics/profile-sam").json()["analytics"]["sample_size"]
    assert after == before + 2


def test_get_analytics_trend_nonempty_after_progress(client):
    _seed_progress(client, "profile-sam", gesture_id="stop")
    analytics = client.get("/analytics/profile-sam").json()["analytics"]
    assert len(analytics["trend"]) > 0


def test_get_analytics_trend_items_have_gesture_id(client):
    _seed_progress(client, "profile-sam", gesture_id="yes")
    analytics = client.get("/analytics/profile-sam").json()["analytics"]
    for point in analytics["trend"]:
        assert "gesture_id" in point
        assert "accuracy" in point
        assert "succeeded" in point


def test_get_analytics_finger_heat_has_five_fingers(client):
    _seed_progress(client, "profile-sam")
    analytics = client.get("/analytics/profile-sam").json()["analytics"]
    assert len(analytics["finger_heat"]) == 5
    fingers = {fh["finger"] for fh in analytics["finger_heat"]}
    assert fingers == {"thumb", "index", "middle", "ring", "pinky"}


def test_get_analytics_weak_gestures_respects_limit(client):
    _seed_progress(client, "profile-sam", gesture_id="no", n=3)
    resp = client.get("/analytics/profile-sam?weak_limit=2")
    assert resp.status_code == 200
    analytics = resp.json()["analytics"]
    assert len(analytics["weak_gestures"]) <= 2


def test_get_analytics_trend_respects_window(client):
    _seed_progress(client, "profile-sam", gesture_id="help", n=5)
    analytics = client.get("/analytics/profile-sam?trend_window=3").json()["analytics"]
    assert len(analytics["trend"]) <= 3


def test_get_analytics_weak_limit_too_large_returns_422(client):
    resp = client.get("/analytics/profile-alex?weak_limit=999")
    assert resp.status_code == 422


def test_get_analytics_trend_window_zero_returns_422(client):
    resp = client.get("/analytics/profile-alex?trend_window=0")
    assert resp.status_code == 422
