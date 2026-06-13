from services.study_service import StudyService


def test_empty_profile_returns_zeroed_stats():
    service = StudyService()
    stats = service.stats("profile-x")
    assert stats.total_sessions == 0
    assert stats.cards_seen == 0
    assert stats.quiz_seen == 0
    assert stats.quiz_correct == 0
    assert stats.decks == {}
    assert stats.last_studied_at is None


def test_browse_session_counts_cards_but_not_quiz_totals():
    service = StudyService()
    stats = service.record_session("profile-x", deck="basics", mode="browse", cards_seen=9, correct=7)
    assert stats.total_sessions == 1
    assert stats.cards_seen == 9
    assert stats.quiz_seen == 0
    assert stats.quiz_correct == 0
    assert stats.last_studied_at is not None


def test_quiz_session_feeds_quiz_totals():
    service = StudyService()
    stats = service.record_session("profile-x", deck="alphabet", mode="quiz", cards_seen=10, correct=8)
    assert stats.quiz_seen == 10
    assert stats.quiz_correct == 8


def test_decks_are_tallied_independently():
    service = StudyService()
    service.record_session("profile-x", deck="basics", mode="browse", cards_seen=9, correct=0)
    service.record_session("profile-x", deck="basics", mode="quiz", cards_seen=5, correct=4)
    stats = service.record_session("profile-x", deck="needs", mode="browse", cards_seen=10, correct=0)
    assert stats.total_sessions == 3
    assert stats.decks["basics"].sessions == 2
    assert stats.decks["basics"].cards_seen == 14
    assert stats.decks["needs"].sessions == 1
    assert stats.decks["needs"].cards_seen == 10


def test_profiles_do_not_share_state():
    service = StudyService()
    service.record_session("profile-a", deck="basics", mode="browse", cards_seen=3, correct=0)
    assert service.stats("profile-b").total_sessions == 0
