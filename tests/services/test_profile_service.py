import pytest

from models.profile import AgeGroup, Role
from services.profile_service import ProfileService


@pytest.fixture
def svc():
    return ProfileService()


# ── seeded data ───────────────────────────────────────────────────────────────

def test_seed_creates_profiles(svc):
    # one parent plus a roster of child learners.
    assert len(svc.list_profiles()) == 6


def test_seed_profile_ids_present(svc):
    ids = {p.id for p in svc.list_profiles()}
    assert "profile-parent-1" in ids
    assert "profile-alex" in ids
    assert "profile-sam" in ids


def test_all_seed_profiles_belong_to_same_user(svc):
    user_ids = {p.user_id for p in svc.list_profiles()}
    assert len(user_ids) == 1


# ── list_profiles ─────────────────────────────────────────────────────────────

def test_list_profiles_with_user_id_filter(svc):
    all_profiles = svc.list_profiles()
    user_id = all_profiles[0].user_id
    filtered = svc.list_profiles(user_id=user_id)
    assert len(filtered) == 6


def test_list_profiles_unknown_user_returns_empty(svc):
    assert svc.list_profiles(user_id="nobody") == []


# ── get_profile / exists ─────────────────────────────────────────────────────

def test_get_profile_returns_correct_profile(svc):
    p = svc.get_profile("profile-alex")
    assert p is not None
    assert p.display_name == "alex"


def test_get_profile_unknown_returns_none(svc):
    assert svc.get_profile("not-a-profile") is None


def test_exists_true_for_seeded_profile(svc):
    assert svc.exists("profile-parent-1") is True


def test_exists_false_for_unknown(svc):
    assert svc.exists("ghost") is False


# ── create_profile ────────────────────────────────────────────────────────────

def test_create_profile_returns_profile(svc):
    p = svc.create_profile(user_id="u1", display_name="nova", avatar="blue")
    assert p.display_name == "nova"


def test_create_profile_unique_ids(svc):
    p1 = svc.create_profile(user_id="u1", display_name="a", avatar="x")
    p2 = svc.create_profile(user_id="u1", display_name="b", avatar="y")
    assert p1.id != p2.id


def test_create_profile_none_user_id_falls_back_to_default(svc):
    p = svc.create_profile(user_id=None, display_name="guest", avatar="grey")
    assert p.user_id is not None


def test_create_profile_appears_in_list(svc):
    svc.create_profile(user_id="u1", display_name="nova", avatar="blue")
    ids = {p.display_name for p in svc.list_profiles()}
    assert "nova" in ids


def test_create_profile_with_age_group(svc):
    p = svc.create_profile(user_id="u1", display_name="kid", avatar="mint",
                            age_group=AgeGroup.early)
    assert p.age_group == AgeGroup.early


def test_create_profile_with_role(svc):
    p = svc.create_profile(user_id="u1", display_name="admin", avatar="brand",
                            role=Role.parent)
    assert p.role == Role.parent
