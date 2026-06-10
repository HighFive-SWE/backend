"""Integration tests for /profiles (list, get, create)."""


# ── list ──────────────────────────────────────────────────────────────────────

def test_list_profiles_returns_200(client):
    resp = client.get("/profiles")
    assert resp.status_code == 200


def test_list_profiles_body_has_profiles_key(client):
    body = client.get("/profiles").json()
    assert "profiles" in body


def test_list_profiles_is_nonempty(client):
    body = client.get("/profiles").json()
    assert len(body["profiles"]) > 0


def test_list_profiles_items_have_required_fields(client):
    profiles = client.get("/profiles").json()["profiles"]
    for p in profiles:
        assert "id" in p
        assert "display_name" in p
        assert "avatar" in p
        assert "role" in p
        assert "age_group" in p


def test_list_profiles_filter_by_user_id(client):
    profiles = client.get("/profiles?user_id=user-home-1").json()["profiles"]
    assert all(p["user_id"] == "user-home-1" for p in profiles)


def test_list_profiles_unknown_user_id_returns_empty(client):
    profiles = client.get("/profiles?user_id=no-such-user").json()["profiles"]
    assert profiles == []


def test_list_profiles_seeded_profiles_present(client):
    profiles = client.get("/profiles").json()["profiles"]
    ids = {p["id"] for p in profiles}
    assert "profile-alex" in ids
    assert "profile-sam" in ids


# ── get by id ─────────────────────────────────────────────────────────────────

def test_get_seeded_profile_returns_200(client):
    resp = client.get("/profiles/profile-alex")
    assert resp.status_code == 200


def test_get_seeded_profile_body_has_profile_key(client):
    body = client.get("/profiles/profile-alex").json()
    assert "profile" in body


def test_get_seeded_profile_correct_id(client):
    profile = client.get("/profiles/profile-alex").json()["profile"]
    assert profile["id"] == "profile-alex"


def test_get_nonexistent_profile_returns_404(client):
    resp = client.get("/profiles/does-not-exist-xyz")
    assert resp.status_code == 404


def test_get_nonexistent_profile_body_has_detail(client):
    body = client.get("/profiles/does-not-exist-xyz").json()
    assert "detail" in body


# ── create ────────────────────────────────────────────────────────────────────

def test_create_profile_returns_200(client):
    payload = {"display_name": "test-kid", "avatar": "mint", "role": "child", "age_group": "early"}
    resp = client.post("/profiles", json=payload)
    assert resp.status_code == 200


def test_create_profile_body_has_profile_key(client):
    payload = {"display_name": "test-kid-2", "avatar": "peach"}
    body = client.post("/profiles", json=payload).json()
    assert "profile" in body


def test_create_profile_has_assigned_id(client):
    payload = {"display_name": "test-kid-3", "avatar": "lilac"}
    profile = client.post("/profiles", json=payload).json()["profile"]
    assert profile["id"]
    assert profile["id"].startswith("profile-")


def test_create_profile_display_name_preserved(client):
    payload = {"display_name": "robin", "avatar": "brand"}
    profile = client.post("/profiles", json=payload).json()["profile"]
    assert profile["display_name"] == "robin"


def test_create_profile_with_user_id(client):
    payload = {"display_name": "owned-kid", "avatar": "mint", "user_id": "user-home-1"}
    profile = client.post("/profiles", json=payload).json()["profile"]
    assert profile["user_id"] == "user-home-1"


def test_create_profile_missing_display_name_returns_422(client):
    payload = {"avatar": "mint"}
    resp = client.post("/profiles", json=payload)
    assert resp.status_code == 422


def test_create_profile_missing_avatar_returns_422(client):
    payload = {"display_name": "no-avatar"}
    resp = client.post("/profiles", json=payload)
    assert resp.status_code == 422


def test_created_profile_retrievable_by_id(client):
    payload = {"display_name": "retrievable", "avatar": "peach"}
    created = client.post("/profiles", json=payload).json()["profile"]
    fetched = client.get(f"/profiles/{created['id']}").json()["profile"]
    assert fetched["id"] == created["id"]
    assert fetched["display_name"] == "retrievable"
