"""Integration tests for GET /lessons."""


def test_list_lessons_returns_200(client):
    resp = client.get("/lessons")
    assert resp.status_code == 200


def test_list_lessons_body_has_lessons_key(client):
    body = client.get("/lessons").json()
    assert "lessons" in body


def test_list_lessons_returns_list(client):
    body = client.get("/lessons").json()
    assert isinstance(body["lessons"], list)


def test_list_lessons_is_nonempty(client):
    body = client.get("/lessons").json()
    assert len(body["lessons"]) > 0


def test_lesson_item_has_required_fields(client):
    lessons = client.get("/lessons").json()["lessons"]
    for lesson in lessons:
        assert "id" in lesson
        assert "title" in lesson
        assert "description" in lesson
        assert "difficulty" in lesson


def test_lesson_difficulty_values_are_valid(client):
    valid = {"starter", "growing", "fluent"}
    lessons = client.get("/lessons").json()["lessons"]
    for lesson in lessons:
        assert lesson["difficulty"] in valid, f"unexpected difficulty: {lesson['difficulty']}"


def test_lessons_ids_are_unique(client):
    lessons = client.get("/lessons").json()["lessons"]
    ids = [lesson["id"] for lesson in lessons]
    assert len(ids) == len(set(ids))


def test_lessons_gesture_ids_are_lists(client):
    lessons = client.get("/lessons").json()["lessons"]
    for lesson in lessons:
        assert isinstance(lesson.get("gesture_ids", []), list)
