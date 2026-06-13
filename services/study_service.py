from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from views.study_view import StudyDeckStats, StudyStats


@dataclass
class _DeckTally:
    sessions: int = 0
    cards_seen: int = 0


@dataclass
class _ProfileStudy:
    total_sessions: int = 0
    cards_seen: int = 0
    quiz_seen: int = 0
    quiz_correct: int = 0
    last_studied_at: datetime | None = None
    decks: dict[str, _DeckTally] = field(default_factory=dict)


class StudyService:
    """tallies camera-free study sessions per profile.

    the frontend's study section keeps its own spaced-repetition state in
    localstorage; this service only aggregates effort so family and educator
    views can see practice that never touched the camera.
    """

    def __init__(self) -> None:
        self._state: dict[str, _ProfileStudy] = {}

    def record_session(
        self,
        profile_id: str,
        deck: str,
        mode: str,
        cards_seen: int,
        correct: int,
    ) -> StudyStats:
        entry = self._state.setdefault(profile_id, _ProfileStudy())
        entry.total_sessions += 1
        entry.cards_seen += cards_seen
        if mode == "quiz":
            entry.quiz_seen += cards_seen
            entry.quiz_correct += correct
        entry.last_studied_at = datetime.now(timezone.utc)

        tally = entry.decks.setdefault(deck, _DeckTally())
        tally.sessions += 1
        tally.cards_seen += cards_seen

        return self.stats(profile_id)

    def stats(self, profile_id: str) -> StudyStats:
        entry = self._state.get(profile_id, _ProfileStudy())
        return StudyStats(
            profile_id=profile_id,
            total_sessions=entry.total_sessions,
            cards_seen=entry.cards_seen,
            quiz_seen=entry.quiz_seen,
            quiz_correct=entry.quiz_correct,
            decks={
                deck: StudyDeckStats(sessions=t.sessions, cards_seen=t.cards_seen)
                for deck, t in entry.decks.items()
            },
            last_studied_at=entry.last_studied_at,
        )


study_service = StudyService()
