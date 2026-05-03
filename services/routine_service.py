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
    # expanded library — additional scenario routines.
    Routine(
        id="morning-routine",
        name="morning routine",
        description="wake-up sequence — greet, ask for breakfast, head out.",
        scenario_tag="home",
        steps=[
            RoutineStep(gesture_id="hello", prompt="say 'hello'", hint="open palm wave."),
            RoutineStep(gesture_id="eat", prompt="ask to 'eat'", hint="flat hand, fingertips tapping toward the mouth."),
            RoutineStep(gesture_id="drink", prompt="ask to 'drink'", hint="c-shape hand tilted back to your lips."),
            RoutineStep(gesture_id="school", prompt="sign 'school'", hint="flat palms clapping twice."),
            RoutineStep(gesture_id="go", prompt="sign 'go'", hint="index finger out, thumb up — off you go."),
        ],
    ),
    Routine(
        id="bedtime-routine",
        name="bedtime routine",
        description="wind-down — finish the day, ask for water, head to bed.",
        scenario_tag="home",
        steps=[
            RoutineStep(gesture_id="finished", prompt="sign 'finished'", hint="open palms flipped outward."),
            RoutineStep(gesture_id="water", prompt="ask for 'water'", hint="'w' shape, thumb across palm."),
            RoutineStep(gesture_id="tired", prompt="sign 'tired'", hint="fingers droop at the second knuckle."),
            RoutineStep(gesture_id="sleep", prompt="sign 'sleep'", hint="soft fingers drift down the face."),
        ],
    ),
    Routine(
        id="feelings-checkin",
        name="feelings check-in",
        description="name what you feel — pain, tired, finished, or more.",
        scenario_tag="feelings",
        steps=[
            RoutineStep(gesture_id="hello", prompt="start with 'hello'", hint="open palm wave."),
            RoutineStep(gesture_id="tired", prompt="sign 'tired'", hint="fingers drooping at the knuckle."),
            RoutineStep(gesture_id="pain", prompt="sign 'pain'", hint="index out — short firm jab."),
            RoutineStep(gesture_id="help", prompt="ask for 'help'", hint="thumb up fist, lifted on the other palm."),
            RoutineStep(gesture_id="thank_you", prompt="say 'thank you'", hint="flat hand from chin outward."),
        ],
    ),
    Routine(
        id="polite-pair",
        name="polite pair",
        description="the two-word combo every kid hears — please and thank you.",
        scenario_tag="manners",
        steps=[
            RoutineStep(gesture_id="please", prompt="sign 'please'", hint="soft hand at the chest, small circle."),
            RoutineStep(gesture_id="thank_you", prompt="sign 'thank you'", hint="flat hand from chin outward."),
        ],
    ),
    Routine(
        id="yes-no-warmup",
        name="yes / no warmup",
        description="answer fast — yes, no, wait, finished.",
        scenario_tag="communication",
        steps=[
            RoutineStep(gesture_id="yes", prompt="sign 'yes'", hint="closed fist, gentle nod motion."),
            RoutineStep(gesture_id="no", prompt="sign 'no'", hint="index and middle out, snap to thumb."),
            RoutineStep(gesture_id="wait", prompt="sign 'wait'", hint="fingers half-curled, small wiggle."),
            RoutineStep(gesture_id="finished", prompt="sign 'finished'", hint="open palms flipped outward."),
        ],
    ),
    Routine(
        id="greeting-tour",
        name="greeting tour",
        description="warm-up that touches every introduction sign.",
        scenario_tag="daily",
        steps=[
            RoutineStep(gesture_id="hello", prompt="sign 'hello'", hint="open palm wave."),
            RoutineStep(gesture_id="friend", prompt="sign 'friend'", hint="hook index fingers, swap which is on top."),
            RoutineStep(gesture_id="family", prompt="sign 'family'", hint="pinch hand sweeping in a circle."),
            RoutineStep(gesture_id="school", prompt="sign 'school'", hint="flat palms clapping twice."),
            RoutineStep(gesture_id="thank_you", prompt="sign 'thank you'", hint="flat hand from chin outward."),
        ],
    ),
    Routine(
        id="snack-time",
        name="snack time",
        description="ask for what you want — eat, drink, more, finished.",
        scenario_tag="mealtime",
        steps=[
            RoutineStep(gesture_id="please", prompt="start with 'please'", hint="soft hand at the chest, small circle."),
            RoutineStep(gesture_id="eat", prompt="ask to 'eat'", hint="fingertips tap toward the mouth."),
            RoutineStep(gesture_id="drink", prompt="ask to 'drink'", hint="c-shape hand tilted to your lips."),
            RoutineStep(gesture_id="more", prompt="ask for 'more'", hint="pinched fingertips tapped together."),
            RoutineStep(gesture_id="finished", prompt="sign 'finished'", hint="open palms flipped outward."),
        ],
    ),
    Routine(
        id="safety-drill",
        name="safety drill",
        description="the urgent set — stop, help, pain, doctor.",
        scenario_tag="safety",
        steps=[
            RoutineStep(gesture_id="stop", prompt="sign 'stop'", hint="flat palm forward, fingers up, held still."),
            RoutineStep(gesture_id="help", prompt="sign 'help'", hint="thumb up fist lifted on the other palm."),
            RoutineStep(gesture_id="pain", prompt="sign 'pain'", hint="index out — short firm jab."),
            RoutineStep(gesture_id="doctor", prompt="sign 'doctor'", hint="'d' hand tapped on the wrist."),
        ],
    ),
    Routine(
        id="house-tour",
        name="house tour",
        description="walking signs around the house — home, bathroom, sleep.",
        scenario_tag="home",
        steps=[
            RoutineStep(gesture_id="home", prompt="sign 'home'", hint="pinched fingertips from cheek to jaw."),
            RoutineStep(gesture_id="bathroom", prompt="sign 'bathroom'", hint="fist with thumb between index and middle, shake."),
            RoutineStep(gesture_id="sleep", prompt="sign 'sleep'", hint="soft fingers drifting down the face."),
            RoutineStep(gesture_id="finished", prompt="sign 'finished'", hint="open palms flipped outward."),
        ],
    ),
    Routine(
        id="come-and-go",
        name="come and go",
        description="directions in motion — come, go, wait, more.",
        scenario_tag="communication",
        steps=[
            RoutineStep(gesture_id="come", prompt="sign 'come'", hint="index finger beckoning, palm up."),
            RoutineStep(gesture_id="wait", prompt="sign 'wait'", hint="fingers half-curled, small wiggle."),
            RoutineStep(gesture_id="go", prompt="sign 'go'", hint="index out, thumb up — off you go."),
            RoutineStep(gesture_id="more", prompt="ask for 'more'", hint="pinched fingertips tapped together."),
        ],
    ),
    # alphabet practice routines — small letter clusters that stay under the
    # 6-step backend cap and ladder by hand-shape similarity.
    Routine(
        id="alphabet-vowels",
        name="vowels — a · e · i · o · u",
        description="the five vowels in a row — same anchor, five different shapes.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_a", prompt="sign 'a'", hint="closed fist with the thumb resting along the side."),
            RoutineStep(gesture_id="letter_e", prompt="sign 'e'", hint="fingers fold flat; thumb tucks across the fingertips."),
            RoutineStep(gesture_id="letter_i", prompt="sign 'i'", hint="fist with the thumb across; lift only the pinky."),
            RoutineStep(gesture_id="letter_o", prompt="sign 'o'", hint="all fingertips touch the thumb to form a round o."),
            RoutineStep(gesture_id="letter_u", prompt="sign 'u'", hint="index and middle straight up and touching."),
        ],
    ),
    Routine(
        id="alphabet-easy-five",
        name="easy five — a · b · c · l · y",
        description="starter shapes that are visually distinct and easy to hold.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_a", prompt="sign 'a'", hint="closed fist, thumb along the side."),
            RoutineStep(gesture_id="letter_b", prompt="sign 'b'", hint="four fingers up flat, thumb across the palm."),
            RoutineStep(gesture_id="letter_c", prompt="sign 'c'", hint="fingers and thumb curve like a c."),
            RoutineStep(gesture_id="letter_l", prompt="sign 'l'", hint="thumb out sideways, index straight up."),
            RoutineStep(gesture_id="letter_y", prompt="sign 'y'", hint="thumb and pinky out, middle three folded."),
        ],
    ),
    Routine(
        id="alphabet-pairs-mn",
        name="tricky pair — m vs n",
        description="two letters that share a thumb-tucked shape; nail the difference.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_m", prompt="sign 'm' (three fingers over thumb)", hint="fold index, middle, and ring down over the thumb."),
            RoutineStep(gesture_id="letter_n", prompt="sign 'n' (two fingers over thumb)", hint="fold only index and middle over the thumb."),
            RoutineStep(gesture_id="letter_t", prompt="now 't' — thumb peeks between fingers", hint="thumb tip pops up between index and middle knuckles."),
        ],
    ),
    Routine(
        id="alphabet-pairs-kp",
        name="tricky pair — k vs p",
        description="same hand shape, different palm direction.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_k", prompt="sign 'k' — index up, middle out", hint="v-shape with thumb in the gap; palm faces forward."),
            RoutineStep(gesture_id="letter_p", prompt="sign 'p' — same shape, palm down", hint="tip the whole hand so the index aims at the floor."),
        ],
    ),
    Routine(
        id="alphabet-pairs-gq",
        name="tricky pair — g vs q",
        description="another rotation pair — g points forward, q points down.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_g", prompt="sign 'g'", hint="fist on its side; thumb and index point forward."),
            RoutineStep(gesture_id="letter_q", prompt="sign 'q'", hint="same shape, but tipped so it points at the floor."),
        ],
    ),
    Routine(
        id="alphabet-pairs-uv",
        name="tricky pair — u vs v",
        description="two fingers up — together for u, spread for v.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_u", prompt="sign 'u'", hint="index and middle straight up, touching."),
            RoutineStep(gesture_id="letter_v", prompt="sign 'v'", hint="index and middle up, but split apart."),
        ],
    ),
    Routine(
        id="spell-mom",
        name="spell 'mom'",
        description="your first family word — three letters, three shapes.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_m", prompt="1/3 · sign 'm'", hint="fold three fingers down over the thumb."),
            RoutineStep(gesture_id="letter_o", prompt="2/3 · sign 'o'", hint="fingertips touch the thumb to form an o."),
            RoutineStep(gesture_id="letter_m", prompt="3/3 · sign 'm' again", hint="back to the m shape — pause, hold, breathe."),
        ],
    ),
    Routine(
        id="spell-dad",
        name="spell 'dad'",
        description="another family word — d to a and back.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_d", prompt="1/3 · sign 'd'", hint="index up; the other three curl to meet the thumb pad."),
            RoutineStep(gesture_id="letter_a", prompt="2/3 · sign 'a'", hint="closed fist, thumb along the side."),
            RoutineStep(gesture_id="letter_d", prompt="3/3 · sign 'd' again", hint="back to the d shape."),
        ],
    ),
    Routine(
        id="spell-yes",
        name="spell 'yes'",
        description="fingerspell what you also know as a single sign.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_y", prompt="1/3 · sign 'y'", hint="thumb and pinky out, middle three folded."),
            RoutineStep(gesture_id="letter_e", prompt="2/3 · sign 'e'", hint="fingers fold flat; thumb tucks across them."),
            RoutineStep(gesture_id="letter_s", prompt="3/3 · sign 's'", hint="tight fist, thumb wrapped over the front."),
        ],
    ),
    Routine(
        id="spell-cat",
        name="spell 'cat'",
        description="starter animal — three crisp letters.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_c", prompt="1/3 · sign 'c'", hint="fingers and thumb curve into a c."),
            RoutineStep(gesture_id="letter_a", prompt="2/3 · sign 'a'", hint="closed fist, thumb along the side."),
            RoutineStep(gesture_id="letter_t", prompt="3/3 · sign 't'", hint="thumb peeks between index and middle knuckles."),
        ],
    ),
    Routine(
        id="spell-dog",
        name="spell 'dog'",
        description="another animal — d, then o, then g.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_d", prompt="1/3 · sign 'd'", hint="index up; others curl to meet the thumb."),
            RoutineStep(gesture_id="letter_o", prompt="2/3 · sign 'o'", hint="round 'o' — fingertips meet the thumb."),
            RoutineStep(gesture_id="letter_g", prompt="3/3 · sign 'g'", hint="fist on its side, thumb and index forward."),
        ],
    ),
    Routine(
        id="spell-fox",
        name="spell 'fox'",
        description="shape jump — f, o, x — three very different hands.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_f", prompt="1/3 · sign 'f'", hint="thumb and index pinch; middle/ring/pinky stay tall."),
            RoutineStep(gesture_id="letter_o", prompt="2/3 · sign 'o'", hint="round 'o' — fingertips meet the thumb."),
            RoutineStep(gesture_id="letter_x", prompt="3/3 · sign 'x'", hint="fist with the index out and bent at the knuckle."),
        ],
    ),
    Routine(
        id="spell-zoo",
        name="spell 'zoo'",
        description="trace a z, then double 'o' — three shapes, two repeated.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_z", prompt="1/3 · sign 'z'", hint="point with the index and trace a clean z."),
            RoutineStep(gesture_id="letter_o", prompt="2/3 · sign 'o'", hint="round 'o' — fingertips meet the thumb."),
            RoutineStep(gesture_id="letter_o", prompt="3/3 · sign 'o' again", hint="hold the same 'o' shape — pause for the gap."),
        ],
    ),
    Routine(
        id="spell-hi",
        name="spell 'hi'",
        description="your shortest spell-along — just two letters.",
        scenario_tag="alphabet",
        steps=[
            RoutineStep(gesture_id="letter_h", prompt="1/2 · sign 'h'", hint="index and middle stacked, pointing sideways."),
            RoutineStep(gesture_id="letter_i", prompt="2/2 · sign 'i'", hint="fist with the thumb across; lift only the pinky."),
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
