from __future__ import annotations

from models.routine import Routine, RoutineStep

# only gesture ids registered in /vision/gestures/samples.py can power live cv.
# routine designs prefer shorter shapes for starter flows and mix more complex
# shapes in the longer scenario routines.
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
    Routine(
        id="basic-conversation",
        name="basic conversation",
        description="greet, thank, apologise — the politeness loop every learner needs.",
        scenario_tag="daily",
        steps=[
            RoutineStep(
                gesture_id="hello",
                prompt="sign 'hello'",
                hint="open palm up — say hi.",
            ),
            RoutineStep(
                gesture_id="thank_you",
                prompt="sign 'thank you'",
                hint="flat hand from chin outward, palm toward you.",
            ),
            RoutineStep(
                gesture_id="please",
                prompt="sign 'please'",
                hint="soft hand at chest, small circle motion.",
            ),
            RoutineStep(
                gesture_id="sorry",
                prompt="sign 'sorry'",
                hint="closed fist on chest — small circle.",
            ),
        ],
    ),
    Routine(
        id="at-home",
        name="at home",
        description="everyday needs around the house — food, water, rest.",
        scenario_tag="home",
        steps=[
            RoutineStep(
                gesture_id="hello",
                prompt="start with 'hello'",
                hint="open palm wave.",
            ),
            RoutineStep(
                gesture_id="food",
                prompt="ask for 'food'",
                hint="pinch fingertips together, tap toward the mouth.",
            ),
            RoutineStep(
                gesture_id="water",
                prompt="ask for 'water'",
                hint="'w' shape, thumb across palm.",
            ),
            RoutineStep(
                gesture_id="sleep",
                prompt="sign 'sleep'",
                hint="soft fingers drifting down the face.",
            ),
        ],
    ),
    Routine(
        id="emergency-help",
        name="emergency help",
        description="urgent signs — help, stop, pain. practise them steady.",
        scenario_tag="safety",
        steps=[
            RoutineStep(
                gesture_id="help",
                prompt="sign 'help'",
                hint="thumb up on a closed fist, lifted on the other palm.",
            ),
            RoutineStep(
                gesture_id="stop",
                prompt="sign 'stop'",
                hint="flat palm facing out, fingers straight up.",
            ),
            RoutineStep(
                gesture_id="pain",
                prompt="sign 'pain'",
                hint="index out, a short firm jab forward.",
            ),
        ],
    ),
    # phase 8 expansion
    Routine(
        id="school-day",
        name="school day",
        description="signs you might use before, during, or after school.",
        scenario_tag="daily",
        steps=[
            RoutineStep(
                gesture_id="hello",
                prompt="greet your teacher",
                hint="open palm wave.",
            ),
            RoutineStep(
                gesture_id="school",
                prompt="sign 'school'",
                hint="flat palms clapping — calling attention.",
            ),
            RoutineStep(
                gesture_id="friend",
                prompt="sign 'friend'",
                hint="hook index fingers and swap.",
            ),
            RoutineStep(
                gesture_id="finished",
                prompt="sign 'finished'",
                hint="open palms flipped outward — day's done.",
            ),
        ],
    ),
    Routine(
        id="doctor-visit",
        name="doctor visit",
        description="practise telling the doctor what you need.",
        scenario_tag="safety",
        steps=[
            RoutineStep(
                gesture_id="hello",
                prompt="greet the doctor",
                hint="open palm wave.",
            ),
            RoutineStep(
                gesture_id="doctor",
                prompt="sign 'doctor'",
                hint="'d' hand tapped on the wrist.",
            ),
            RoutineStep(
                gesture_id="pain",
                prompt="sign 'pain'",
                hint="index out — firm jab.",
            ),
            RoutineStep(
                gesture_id="help",
                prompt="ask for 'help'",
                hint="thumb up fist, lifted.",
            ),
            RoutineStep(
                gesture_id="thank_you",
                prompt="sign 'thank you'",
                hint="flat hand from chin outward.",
            ),
        ],
    ),
    Routine(
        id="play-time",
        name="play time",
        description="hang out with friends — invite, play, and wrap up.",
        scenario_tag="family",
        steps=[
            RoutineStep(
                gesture_id="come",
                prompt="beckon a friend",
                hint="index finger beckoning — palm up.",
            ),
            RoutineStep(
                gesture_id="play",
                prompt="sign 'play'",
                hint="'y' hand — thumb and pinky out, shake.",
            ),
            RoutineStep(
                gesture_id="more",
                prompt="ask for 'more'",
                hint="pinched fingertips tapped together.",
            ),
            RoutineStep(
                gesture_id="finished",
                prompt="sign 'finished'",
                hint="open palms flipped outward.",
            ),
        ],
    ),
]


MIN_STEPS = 2
MAX_STEPS = 6


def _known_gesture_ids() -> set[str]:
    from core import vision_path  # noqa: F401
    from vision import GESTURES  # type: ignore[import-not-found]
    return set(GESTURES.keys())


class RoutineService:
    def __init__(self, seed: list[Routine] | None = None) -> None:
        self._routines: dict[str, Routine] = {r.id: r for r in (seed or _SEED)}
        self._counter = 0

    def list_routines(self) -> list[Routine]:
        return list(self._routines.values())

    def get(self, routine_id: str) -> Routine:
        try:
            return self._routines[routine_id]
        except KeyError as exc:
            raise KeyError(f"routine '{routine_id}' not found") from exc

    def create(
        self,
        name: str,
        description: str,
        steps: list[RoutineStep],
        created_by: str,
    ) -> Routine:
        self._validate_steps(steps)
        self._counter += 1
        rid = f"custom-{self._counter}-{created_by[:8]}"
        routine = Routine(
            id=rid,
            name=name,
            description=description,
            scenario_tag="custom",
            steps=steps,
            created_by=created_by,
            is_custom=True,
        )
        self._routines[rid] = routine
        return routine

    def update(
        self,
        routine_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        steps: list[RoutineStep] | None = None,
    ) -> Routine:
        routine = self.get(routine_id)
        if not routine.is_custom:
            raise ValueError("seed routines cannot be edited")
        if steps is not None:
            self._validate_steps(steps)
        updated = routine.model_copy(
            update={
                k: v
                for k, v in {"name": name, "description": description, "steps": steps}.items()
                if v is not None
            }
        )
        self._routines[routine_id] = updated
        return updated

    def delete(self, routine_id: str) -> None:
        routine = self.get(routine_id)
        if not routine.is_custom:
            raise ValueError("seed routines cannot be deleted")
        del self._routines[routine_id]

    def _validate_steps(self, steps: list[RoutineStep]) -> None:
        if len(steps) < MIN_STEPS:
            raise ValueError(f"routine needs at least {MIN_STEPS} steps")
        if len(steps) > MAX_STEPS:
            raise ValueError(f"routine can have at most {MAX_STEPS} steps")
        known = _known_gesture_ids()
        for step in steps:
            if step.gesture_id not in known:
                raise ValueError(f"unknown gesture '{step.gesture_id}'")


routine_service = RoutineService()
