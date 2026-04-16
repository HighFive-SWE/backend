from __future__ import annotations

from models.routine import Routine, RoutineStep

# only gesture ids registered in /vision/gestures/samples.py can power live cv —
# routines stay within that set for phase 3.
_SEED: list[Routine] = [
    Routine(
        id="greet-family",
        name="greet your family",
        description="a gentle wave to say hi — one step, warm vibe.",
        scenario_tag="daily",
        steps=[
            RoutineStep(
                gesture_id="hello",
                prompt="sign 'hello'",
                hint="open palm, fingers up, tip of thumb at temple.",
            ),
        ],
    ),
    Routine(
        id="ask-water",
        name="i need water",
        description="greet, then ask — two steps, a tiny conversation.",
        scenario_tag="daily",
        steps=[
            RoutineStep(
                gesture_id="hello",
                prompt="start with 'hello'",
                hint="open palm, fingers up, gentle wave.",
            ),
            RoutineStep(
                gesture_id="water",
                prompt="now ask for 'water'",
                hint="'w' shape — index, middle, ring up; thumb across palm.",
            ),
        ],
    ),
    Routine(
        id="mealtime-hello-water",
        name="mealtime warmup",
        description="say hello, then ask for water — practice the whole sequence.",
        scenario_tag="mealtime",
        steps=[
            RoutineStep(
                gesture_id="hello",
                prompt="greet",
                hint="open palm — hold for a beat.",
            ),
            RoutineStep(
                gesture_id="water",
                prompt="ask for water",
                hint="three fingers up, thumb tucked in.",
            ),
            RoutineStep(
                gesture_id="hello",
                prompt="wave to close",
                hint="same hello — friendly and relaxed.",
            ),
        ],
    ),
]


class RoutineService:
    def __init__(self, seed: list[Routine] | None = None) -> None:
        self._routines: dict[str, Routine] = {r.id: r for r in (seed or _SEED)}

    def list_routines(self) -> list[Routine]:
        return list(self._routines.values())

    def get(self, routine_id: str) -> Routine:
        try:
            return self._routines[routine_id]
        except KeyError as exc:
            raise KeyError(f"routine '{routine_id}' not found") from exc


routine_service = RoutineService()
