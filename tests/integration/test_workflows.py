"""
Cross-endpoint integration tests that exercise multiple routes together.
Each test exercises a realistic user flow end-to-end.
"""

import uuid

from tests.integration.conftest import landmarks_for


# ── profile → progress → analytics ───────────────────────────────────────────

def test_new_profile_then_progress_then_analytics(client):
    # 1. create a fresh profile
    profile = client.post(
        "/profiles",
        json={"display_name": "workflow-kid", "avatar": "mint"},
    ).json()["profile"]
    pid = profile["id"]

    # 2. record a successful step
    resp = client.post(
        "/progress",
        json={
            "profile_id": pid,
            "routine_id": "greet-family",
            "gesture_id": "hello",
            "accuracy": 0.90,
            "band": "correct",
            "attempts": 1,
            "succeeded": True,
        },
    )
    assert resp.status_code == 200
    progress_body = resp.json()
    assert progress_body["xp_gained"] > 0

    # 3. analytics must reflect that attempt
    analytics = client.get(f"/analytics/{pid}").json()["analytics"]
    assert analytics["sample_size"] == 1
    assert analytics["avg_accuracy"] == 0.9


def test_cv_evaluate_then_progress_summary_consistent(client):
    # 1. evaluate gesture
    cv_body = client.post(
        "/cv/evaluate",
        json={"gesture_id": "hello", "landmarks": landmarks_for("hello")},
    ).json()
    accuracy = cv_body["accuracy"]
    band = cv_body["band"]

    # 2. record that result as progress
    resp = client.post(
        "/progress",
        json={
            "profile_id": "profile-alex",
            "routine_id": "greet-family",
            "gesture_id": "hello",
            "accuracy": accuracy,
            "band": band,
            "attempts": 1,
            "succeeded": band == "correct",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["record"]["accuracy"] == accuracy


def test_create_routine_then_record_progress_against_it(client):
    # 1. create a custom routine
    routine = client.post(
        "/routines",
        json={
            "name": "workflow routine",
            "description": "test flow",
            "created_by": "profile-alex",
            "steps": [
                {"gesture_id": "hello", "prompt": "say hello", "hint": "open palm"},
                {"gesture_id": "water", "prompt": "ask for water", "hint": "w shape"},
            ],
        },
    ).json()["routine"]
    routine_id = routine["id"]

    # 2. record progress against it
    resp = client.post(
        "/progress",
        json={
            "profile_id": "profile-alex",
            "routine_id": routine_id,
            "gesture_id": "hello",
            "accuracy": 0.80,
            "band": "correct",
            "attempts": 1,
            "succeeded": True,
            "completed_routine": True,
        },
    )
    assert resp.status_code == 200
    assert routine_id in resp.json()["summary"]["routines_completed"]

    # cleanup
    client.delete(f"/routines/{routine_id}")


def test_progress_first_step_unlocks_achievement(client):
    # create an isolated profile so we can guarantee "first_step" fires
    profile_id = client.post(
        "/profiles",
        json={"display_name": "achiever", "avatar": "peach"},
    ).json()["profile"]["id"]

    resp = client.post(
        "/progress",
        json={
            "profile_id": profile_id,
            "routine_id": "greet-family",
            "gesture_id": "hello",
            "accuracy": 0.85,
            "band": "correct",
            "attempts": 1,
            "succeeded": True,
        },
    )
    assert resp.status_code == 200
    codes = [a["code"] for a in resp.json()["new_achievements"]]
    assert "first_step" in codes


def test_idempotent_progress_does_not_double_count(client):
    profile_id = client.post(
        "/profiles",
        json={"display_name": "idem-flow", "avatar": "lilac"},
    ).json()["profile"]["id"]

    key = f"flow-{uuid.uuid4().hex[:12]}"
    payload = {
        "profile_id": profile_id,
        "routine_id": "greet-family",
        "gesture_id": "hello",
        "accuracy": 0.80,
        "band": "correct",
        "attempts": 1,
        "succeeded": True,
        "idempotency_key": key,
    }

    first = client.post("/progress", json=payload).json()
    second = client.post("/progress", json=payload).json()

    # both succeed but state is recorded only once
    assert first["summary"]["total_attempts"] == second["summary"]["total_attempts"]
    assert first["summary"]["total_xp"] == second["summary"]["total_xp"]


def test_profile_appears_in_list_after_creation(client):
    profile = client.post(
        "/profiles",
        json={"display_name": "listed-kid", "avatar": "brand", "user_id": "user-home-1"},
    ).json()["profile"]
    pid = profile["id"]

    all_ids = {p["id"] for p in client.get("/profiles").json()["profiles"]}
    assert pid in all_ids

    filtered_ids = {
        p["id"] for p in client.get("/profiles?user_id=user-home-1").json()["profiles"]
    }
    assert pid in filtered_ids


def test_cv_results_reflect_multiple_gestures(client):
    for gesture in ("hello", "water", "stop"):
        client.post(
            "/cv/evaluate",
            json={"gesture_id": gesture, "landmarks": landmarks_for(gesture)},
        )

    results = client.get("/cv/results").json()["results"]
    gesture_ids_seen = {r["gesture_id"] for r in results}
    assert {"hello", "water", "stop"}.issubset(gesture_ids_seen)
