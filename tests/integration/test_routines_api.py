"""Integration tests for /routines (list, get, create, update, delete)."""

import pytest


# ── list ──────────────────────────────────────────────────────────────────────

def test_list_routines_returns_200(client):
    resp = client.get("/routines")
    assert resp.status_code == 200


def test_list_routines_body_has_routines_key(client):
    body = client.get("/routines").json()
    assert "routines" in body


def test_list_routines_is_nonempty(client):
    body = client.get("/routines").json()
    assert len(body["routines"]) > 0


def test_routine_item_has_required_fields(client):
    routines = client.get("/routines").json()["routines"]
    for r in routines:
        assert "id" in r
        assert "name" in r
        assert "description" in r
        assert "steps" in r
        assert isinstance(r["steps"], list)


def test_routine_steps_have_gesture_id_and_prompt(client):
    routines = client.get("/routines").json()["routines"]
    for r in routines:
        for step in r["steps"]:
            assert "gesture_id" in step
            assert "prompt" in step
            assert "hint" in step


# ── get by id ─────────────────────────────────────────────────────────────────

def test_get_seed_routine_returns_200(client):
    resp = client.get("/routines/greet-family")
    assert resp.status_code == 200


def test_get_seed_routine_body_has_routine_key(client):
    body = client.get("/routines/greet-family").json()
    assert "routine" in body


def test_get_seed_routine_has_correct_id(client):
    routine = client.get("/routines/greet-family").json()["routine"]
    assert routine["id"] == "greet-family"


def test_get_nonexistent_routine_returns_404(client):
    resp = client.get("/routines/does-not-exist-xyz")
    assert resp.status_code == 404


def test_get_nonexistent_routine_body_has_detail(client):
    body = client.get("/routines/does-not-exist-xyz").json()
    assert "detail" in body


# ── create / update / delete ──────────────────────────────────────────────────

def test_create_routine_full_crud(client):
    payload = {
        "name": "integration test routine",
        "description": "created by integration tests",
        "created_by": "profile-alex",
        "steps": [
            {"gesture_id": "hello", "prompt": "say hello", "hint": "open palm"},
            {"gesture_id": "water", "prompt": "ask for water", "hint": "w shape"},
        ],
    }
    # create
    resp = client.post("/routines", json=payload)
    assert resp.status_code == 201
    routine_id = resp.json()["routine"]["id"]
    assert routine_id.startswith("custom-")

    # get it back
    get_resp = client.get(f"/routines/{routine_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["routine"]["name"] == "integration test routine"

    # update it
    update_resp = client.put(f"/routines/{routine_id}", json={"name": "updated name"})
    assert update_resp.status_code == 200
    assert update_resp.json()["routine"]["name"] == "updated name"

    # delete it
    del_resp = client.delete(f"/routines/{routine_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["ok"] is True

    # confirm it's gone
    gone_resp = client.get(f"/routines/{routine_id}")
    assert gone_resp.status_code == 404


def test_create_routine_unknown_profile_returns_404(client):
    payload = {
        "name": "orphan routine",
        "description": "no owner",
        "created_by": "nonexistent-profile",
        "steps": [
            {"gesture_id": "hello", "prompt": "hi", "hint": "wave"},
            {"gesture_id": "water", "prompt": "water", "hint": "w"},
        ],
    }
    resp = client.post("/routines", json=payload)
    assert resp.status_code == 404


def test_create_routine_too_few_steps_returns_422(client):
    payload = {
        "name": "too short",
        "description": "just one step",
        "created_by": "profile-alex",
        "steps": [
            {"gesture_id": "hello", "prompt": "hi", "hint": "wave"},
        ],
    }
    resp = client.post("/routines", json=payload)
    assert resp.status_code == 422


def test_create_routine_unknown_gesture_returns_422(client):
    payload = {
        "name": "bad gesture",
        "description": "uses a made-up gesture",
        "created_by": "profile-alex",
        "steps": [
            {"gesture_id": "not-a-real-gesture", "prompt": "???", "hint": "???"},
            {"gesture_id": "hello", "prompt": "hi", "hint": "wave"},
        ],
    }
    resp = client.post("/routines", json=payload)
    assert resp.status_code == 422


def test_update_seed_routine_returns_422(client):
    resp = client.put("/routines/greet-family", json={"name": "renamed"})
    assert resp.status_code == 422


def test_delete_seed_routine_returns_422(client):
    resp = client.delete("/routines/greet-family")
    assert resp.status_code == 422
