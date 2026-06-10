"""Integration tests for GET /health."""


def test_health_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_body_has_status(client):
    body = client.get("/health").json()
    assert "status" in body


def test_health_status_is_ok(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"


def test_health_body_has_env(client):
    body = client.get("/health").json()
    assert "env" in body


def test_health_env_is_string(client):
    body = client.get("/health").json()
    assert isinstance(body["env"], str)


def test_health_content_type_is_json(client):
    resp = client.get("/health")
    assert "application/json" in resp.headers["content-type"]


def test_health_response_includes_request_id_header(client):
    resp = client.get("/health")
    assert "x-request-id" in resp.headers
