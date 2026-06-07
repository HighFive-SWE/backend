from unittest.mock import patch

import pytest

from models.routine import Routine, RoutineStep
from services.routine_service import RoutineService, MIN_STEPS, MAX_STEPS

_KNOWN = {"hello", "water", "food", "help", "stop", "yes", "no", "thank_you",
          "please", "sorry", "pain", "tired", "sleep", "more", "finished"}


def _make_steps(*gesture_ids: str) -> list[RoutineStep]:
    return [RoutineStep(gesture_id=g, prompt=f"sign {g}", hint="") for g in gesture_ids]


@pytest.fixture
def svc():
    with patch("services.routine_service._known_gesture_ids", return_value=_KNOWN):
        yield RoutineService(seed=[])


def _make_custom(svc, name="test", steps=None, created_by="user-1"):
    if steps is None:
        steps = _make_steps("hello", "water")
    with patch("services.routine_service._known_gesture_ids", return_value=_KNOWN):
        return svc.create(name=name, description="d", steps=steps, created_by=created_by)


# ── create ────────────────────────────────────────────────────────────────────

def test_create_returns_routine(svc):
    r = _make_custom(svc)
    assert isinstance(r, Routine)


def test_create_routine_is_custom(svc):
    r = _make_custom(svc)
    assert r.is_custom is True


def test_create_routine_appears_in_list(svc):
    r = _make_custom(svc)
    ids = {x.id for x in svc.list_routines()}
    assert r.id in ids


def test_create_too_few_steps_raises(svc):
    with patch("services.routine_service._known_gesture_ids", return_value=_KNOWN):
        with pytest.raises(ValueError, match="at least"):
            svc.create("x", "d", _make_steps("hello"), "u")


def test_create_too_many_steps_raises(svc):
    gestures = list(_KNOWN)[:MAX_STEPS + 1]
    with patch("services.routine_service._known_gesture_ids", return_value=_KNOWN):
        with pytest.raises(ValueError, match="at most"):
            svc.create("x", "d", _make_steps(*gestures), "u")


def test_create_unknown_gesture_raises(svc):
    with patch("services.routine_service._known_gesture_ids", return_value=_KNOWN):
        with pytest.raises(ValueError, match="unknown gesture"):
            svc.create("x", "d", _make_steps("hello", "not-a-gesture"), "u")


# ── get ───────────────────────────────────────────────────────────────────────

def test_get_returns_routine(svc):
    r = _make_custom(svc)
    assert svc.get(r.id).id == r.id


def test_get_unknown_raises(svc):
    with pytest.raises(KeyError):
        svc.get("no-such-id")


# ── update ────────────────────────────────────────────────────────────────────

def test_update_name(svc):
    r = _make_custom(svc)
    updated = svc.update(r.id, name="new name")
    assert updated.name == "new name"


def test_update_description(svc):
    r = _make_custom(svc)
    updated = svc.update(r.id, description="new desc")
    assert updated.description == "new desc"


def test_update_steps(svc):
    r = _make_custom(svc)
    new_steps = _make_steps("hello", "food")
    with patch("services.routine_service._known_gesture_ids", return_value=_KNOWN):
        updated = svc.update(r.id, steps=new_steps)
    assert len(updated.steps) == 2


# ── delete ────────────────────────────────────────────────────────────────────

def test_delete_removes_routine(svc):
    r = _make_custom(svc)
    svc.delete(r.id)
    with pytest.raises(KeyError):
        svc.get(r.id)


# ── seed protection ───────────────────────────────────────────────────────────

def test_seed_routine_cannot_be_edited():
    seed = [Routine(id="seed-1", name="seed", description="d",
                    scenario_tag="daily", steps=_make_steps("hello", "water"))]
    svc = RoutineService(seed=seed)
    with pytest.raises(ValueError, match="seed routines cannot be edited"):
        svc.update("seed-1", name="new")


def test_seed_routine_cannot_be_deleted():
    seed = [Routine(id="seed-1", name="seed", description="d",
                    scenario_tag="daily", steps=_make_steps("hello", "water"))]
    svc = RoutineService(seed=seed)
    with pytest.raises(ValueError, match="seed routines cannot be deleted"):
        svc.delete("seed-1")
