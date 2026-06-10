import pytest

from services.lesson_service import LessonService


@pytest.fixture
def svc():
    return LessonService()


def test_list_lessons_returns_lessons(svc):
    lessons = svc.list_lessons()
    assert len(lessons) > 0


def test_all_26_alphabet_lessons_present(svc):
    ids = {l.id for l in svc.list_lessons()}
    for letter in "abcdefghijklmnopqrstuvwxyz":
        assert f"alphabet-{letter}" in ids, f"missing alphabet-{letter}"


def test_all_lessons_have_valid_difficulty(svc):
    valid = {"starter", "growing", "fluent"}
    for lesson in svc.list_lessons():
        assert lesson.difficulty in valid, f"bad difficulty on {lesson.id}"


def test_all_lessons_have_nonempty_gesture_ids(svc):
    for lesson in svc.list_lessons():
        assert len(lesson.gesture_ids) > 0, f"no gesture_ids on {lesson.id}"


def test_catalog_mutation_does_not_affect_next_call(svc):
    first = svc.list_lessons()
    first.clear()
    second = svc.list_lessons()
    assert len(second) > 0


def test_hello_lesson_present(svc):
    ids = {l.id for l in svc.list_lessons()}
    assert "hello" in ids


def test_core_lessons_present(svc):
    ids = {l.id for l in svc.list_lessons()}
    for expected in ("hello", "water", "help", "stop", "yes", "no"):
        assert expected in ids
