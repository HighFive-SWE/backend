from __future__ import annotations

import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Deque

from models.progress import Achievement, DailyGoal, ProgressRecord, ProgressSummary


# --- xp / level ------------------------------------------------------------

XP_PER_STEP = 10
XP_PER_ROUTINE = 50
XP_PERFECT_BONUS = 20
PERFECT_ACCURACY_THRESHOLD = 0.95

# level = floor(sqrt(xp / 50)) — rising gap between levels keeps milestones feeling earned.
def level_for(xp: int) -> int:
    return int(math.floor(math.sqrt(max(xp, 0) / 50)))


def xp_for_level(level: int) -> int:
    return (level * level) * 50


# --- daily goal ------------------------------------------------------------

DEFAULT_DAILY_TARGET = 3


# --- day boundary ------------------------------------------------------------

def _local_day(at: datetime, tz_offset_minutes: int) -> date:
    """the learner's calendar day for a utc instant, given minutes east of utc."""
    return (at.astimezone(timezone.utc) + timedelta(minutes=tz_offset_minutes)).date()


# --- achievements ----------------------------------------------------------

@dataclass(frozen=True)
class AchievementDef:
    code: str
    title: str
    description: str


ACHIEVEMENT_CATALOG: dict[str, AchievementDef] = {
    "first_step": AchievementDef(
        code="first_step",
        title="first step",
        description="completed your first sign.",
    ),
    "first_routine": AchievementDef(
        code="first_routine",
        title="first scenario",
        description="finished a whole routine end-to-end.",
    ),
    "three_day_streak": AchievementDef(
        code="three_day_streak",
        title="three-day streak",
        description="showed up three days in a row.",
    ),
    "ten_perfect_steps": AchievementDef(
        code="ten_perfect_steps",
        title="ten clean signs",
        description="ten steps at 95%+ accuracy.",
    ),
}


# --- per-profile state -----------------------------------------------------

@dataclass
class ProfileState:
    current_streak: int = 0
    longest_streak: int = 0
    last_active_date: date | None = None
    total_xp: int = 0
    perfect_steps: int = 0
    daily_date: date | None = None
    daily_progress: int = 0
    daily_target: int = DEFAULT_DAILY_TARGET
    achievements: dict[str, Achievement] = field(default_factory=dict)
    # all-time counters, maintained on the write path so the summary stays
    # truthful after the per-profile log deque starts evicting old records.
    total_attempts: int = 0
    successes: int = 0
    accuracy_sum: float = 0.0
    best_accuracy: float = 0.0
    # last tz offset the client reported — used so summary's "today" (daily
    # goal) agrees with the day boundary the write path used.
    tz_offset_minutes: int = 0


# --- service ---------------------------------------------------------------

class ProgressService:
    """
    in-memory per-profile progress log with phase 4 gamification layer
    (streaks, xp, levels, daily goal, achievements). phase 5 keyed all
    storage by profile_id so each learner has isolated progress.
    """

    def __init__(self, per_profile_capacity: int = 500) -> None:
        self._per_profile_capacity = per_profile_capacity
        self._logs: dict[str, Deque[ProgressRecord]] = defaultdict(
            lambda: deque(maxlen=per_profile_capacity)
        )
        self._completed_routines: dict[str, set[str]] = defaultdict(set)
        self._state: dict[str, ProfileState] = defaultdict(ProfileState)

    # --- write path -------------------------------------------------------

    def record(
        self,
        record: ProgressRecord,
        *,
        completed_routine: bool = False,
    ) -> ProgressRecord:
        self._logs[record.profile_id].append(record)

        state = self._state[record.profile_id]
        state.total_attempts += 1
        state.accuracy_sum += record.accuracy
        state.best_accuracy = max(state.best_accuracy, record.accuracy)
        if record.succeeded:
            state.successes += 1

        # bucket by the learner's calendar day, not the server's — a kid
        # practising at 5:30pm two evenings running should always read as
        # two consecutive days regardless of where the utc midnight falls.
        state.tz_offset_minutes = record.tz_offset_minutes
        today = _local_day(record.created_at, record.tz_offset_minutes)
        self._bump_streak(state, today)

        if record.succeeded:
            self._award_xp_for_step(state, record)
            self._bump_daily_goal(state, today)
            if record.accuracy >= PERFECT_ACCURACY_THRESHOLD:
                state.perfect_steps += 1

        if completed_routine:
            self._completed_routines[record.profile_id].add(record.routine_id)
            state.total_xp += XP_PER_ROUTINE

        self._check_achievements(state, record, completed_routine)
        return record

    def mark_routine_complete(self, profile_id: str, routine_id: str) -> None:
        self._completed_routines[profile_id].add(routine_id)

    def set_daily_target(self, profile_id: str, target: int) -> None:
        self._state[profile_id].daily_target = target

    # --- read path --------------------------------------------------------

    def list_for(self, profile_id: str, limit: int = 100) -> list[ProgressRecord]:
        if limit <= 0:
            return []
        records = list(self._logs.get(profile_id, ()))[-limit:]
        records.reverse()
        return records

    def all_records(self, profile_id: str) -> list[ProgressRecord]:
        # oldest-first, used by analytics for trend + aggregation.
        return list(self._logs.get(profile_id, ()))

    def summary(self, profile_id: str) -> ProgressSummary:
        state = self._state.get(profile_id, ProfileState())

        # all-time figures come from the running counters, not the log — the
        # deque caps at per_profile_capacity and would silently turn these
        # into rolling-window stats for an active learner.
        total = state.total_attempts
        successes = state.successes
        avg_accuracy = round(state.accuracy_sum / total, 4) if total else 0.0
        best = round(state.best_accuracy, 4)

        level = level_for(state.total_xp)
        floor_xp = xp_for_level(level)
        next_level_xp = xp_for_level(level + 1)
        xp_into_level = max(state.total_xp - floor_xp, 0)
        xp_to_next = max(next_level_xp - floor_xp, 1)

        # daily goal resets lazily — if today's different from stored date,
        # reset the counter. "today" uses the learner's last-reported offset
        # so it agrees with the day boundary the write path used.
        today = _local_day(datetime.now(timezone.utc), state.tz_offset_minutes)
        if state.daily_date != today:
            daily_progress = 0
        else:
            daily_progress = state.daily_progress

        return ProgressSummary(
            profile_id=profile_id,
            total_attempts=total,
            successes=successes,
            avg_accuracy=avg_accuracy,
            best_accuracy=best,
            routines_completed=sorted(self._completed_routines.get(profile_id, set())),
            current_streak=state.current_streak,
            longest_streak=state.longest_streak,
            last_active_date=state.last_active_date,
            total_xp=state.total_xp,
            level=level,
            xp_into_level=xp_into_level,
            xp_to_next_level=xp_to_next,
            achievements=sorted(
                state.achievements.values(),
                key=lambda a: a.unlocked_at,
            ),
            daily_goal=DailyGoal(
                target=state.daily_target,
                progress=daily_progress,
                date=today,
            ),
            streak_days=state.current_streak,
        )

    # --- helpers ----------------------------------------------------------

    def _bump_streak(self, state: ProfileState, today: date) -> None:
        last = state.last_active_date
        if last is None:
            state.current_streak = 1
        elif last == today:
            pass  # same-day activity doesn't move the streak.
        elif last == today - timedelta(days=1):
            state.current_streak += 1
        else:
            state.current_streak = 1
        state.longest_streak = max(state.longest_streak, state.current_streak)
        state.last_active_date = today

    def _award_xp_for_step(self, state: ProfileState, record: ProgressRecord) -> None:
        state.total_xp += XP_PER_STEP
        if record.accuracy >= PERFECT_ACCURACY_THRESHOLD:
            state.total_xp += XP_PERFECT_BONUS

    def _bump_daily_goal(self, state: ProfileState, today: date) -> None:
        if state.daily_date != today:
            state.daily_date = today
            state.daily_progress = 0
        state.daily_progress += 1

    def _check_achievements(
        self,
        state: ProfileState,
        record: ProgressRecord,
        completed_routine: bool,
    ) -> None:
        def unlock(code: str) -> None:
            if code in state.achievements:
                return
            definition = ACHIEVEMENT_CATALOG[code]
            state.achievements[code] = Achievement(
                code=definition.code,
                title=definition.title,
                description=definition.description,
                unlocked_at=datetime.now(timezone.utc),
            )

        if record.succeeded:
            unlock("first_step")
        if completed_routine:
            unlock("first_routine")
        if state.current_streak >= 3:
            unlock("three_day_streak")
        if state.perfect_steps >= 10:
            unlock("ten_perfect_steps")


progress_service = ProgressService()
