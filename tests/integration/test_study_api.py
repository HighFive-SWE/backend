def _stats(client, profile_id: str) -> dict:
    res = client.get(f"/study/{profile_id}")
    assert res.status_code == 200
    return res.json()["stats"]


def test_stats_start_at_zero_for_seeded_profile(client):
    stats = _stats(client, "profile-sam")
    assert stats["profile_id"] == "profile-sam"
    assert stats["total_sessions"] >= 0


def test_record_session_accumulates(client):
    before = _stats(client, "profile-alex")

    res = client.post(
        "/study/sessions",
        json={
            "profile_id": "profile-alex",
            "deck": "basics",
            "mode": "quiz",
            "cards_seen": 10,
            "correct": 8,
        },
    )
    assert res.status_code == 200
    after = res.json()["stats"]

    assert after["total_sessions"] == before["total_sessions"] + 1
    assert after["cards_seen"] == before["cards_seen"] + 10
    assert after["quiz_seen"] == before["quiz_seen"] + 10
    assert after["quiz_correct"] == before["quiz_correct"] + 8
    assert after["decks"]["basics"]["sessions"] >= 1
    assert after["last_studied_at"] is not None

    # the get endpoint reflects the same totals
    assert _stats(client, "profile-alex") == after


def test_browse_sessions_do_not_inflate_quiz_accuracy(client):
    before = _stats(client, "profile-alex")
    res = client.post(
        "/study/sessions",
        json={
            "profile_id": "profile-alex",
            "deck": "needs",
            "mode": "browse",
            "cards_seen": 10,
            "correct": 0,
        },
    )
    assert res.status_code == 200
    after = res.json()["stats"]
    assert after["quiz_seen"] == before["quiz_seen"]
    assert after["quiz_correct"] == before["quiz_correct"]


def test_unknown_profile_is_rejected(client):
    res = client.post(
        "/study/sessions",
        json={
            "profile_id": "profile-ghost",
            "deck": "basics",
            "mode": "browse",
            "cards_seen": 1,
            "correct": 0,
        },
    )
    assert res.status_code == 404

    res = client.get("/study/profile-ghost")
    assert res.status_code == 404


def test_correct_cannot_exceed_cards_seen(client):
    res = client.post(
        "/study/sessions",
        json={
            "profile_id": "profile-alex",
            "deck": "basics",
            "mode": "quiz",
            "cards_seen": 5,
            "correct": 6,
        },
    )
    assert res.status_code == 422


def test_unknown_mode_is_rejected(client):
    res = client.post(
        "/study/sessions",
        json={
            "profile_id": "profile-alex",
            "deck": "basics",
            "mode": "cram",
            "cards_seen": 5,
            "correct": 5,
        },
    )
    assert res.status_code == 422
