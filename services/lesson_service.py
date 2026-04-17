from models.lesson import Lesson

# static catalog for phase 1-6 — replaced by a db-backed repo later.
# every lesson that binds to a gesture id in /vision/gestures/samples.py will
# render the live mirror; the rest stay as card-only content for now.
_SEED: list[Lesson] = [
    Lesson(
        id="hello",
        title="hello",
        description="wave an open palm beside your temple, then move it outward.",
        difficulty="starter",
        tags=["greetings", "daily"],
        gesture_ids=["hello"],
        scenario_tag="daily",
    ),
    Lesson(
        id="thank-you",
        title="thank you",
        description="flat hand touches chin and moves forward, like blowing a kiss.",
        difficulty="starter",
        tags=["manners", "daily"],
        gesture_ids=["thank_you"],
        scenario_tag="daily",
    ),
    Lesson(
        id="please",
        title="please",
        description="soft open hand circling at the chest — gentle and polite.",
        difficulty="starter",
        tags=["manners", "daily"],
        gesture_ids=["please"],
        scenario_tag="daily",
    ),
    Lesson(
        id="sorry",
        title="sorry",
        description="closed fist on the chest — small circle, eyes soft.",
        difficulty="starter",
        tags=["manners", "feelings"],
        gesture_ids=["sorry"],
        scenario_tag="daily",
    ),
    Lesson(
        id="water",
        title="water",
        description="form a 'w' with three fingers; tap it against your chin.",
        difficulty="starter",
        tags=["mealtime", "needs"],
        gesture_ids=["water"],
        scenario_tag="daily",
    ),
    Lesson(
        id="food",
        title="food",
        description="pinch all fingertips together, tap toward the mouth.",
        difficulty="starter",
        tags=["mealtime", "needs"],
        gesture_ids=["food"],
        scenario_tag="mealtime",
    ),
    Lesson(
        id="help",
        title="help",
        description="thumb-up fist lifted on the other palm, raised together.",
        difficulty="growing",
        tags=["safety", "needs"],
        gesture_ids=["help"],
        scenario_tag="safety",
    ),
    Lesson(
        id="stop",
        title="stop",
        description="flat palm facing out, fingers straight up — held still.",
        difficulty="starter",
        tags=["safety", "daily"],
        gesture_ids=["stop"],
        scenario_tag="safety",
    ),
    Lesson(
        id="yes",
        title="yes",
        description="closed fist, gentle nodding motion.",
        difficulty="starter",
        tags=["daily", "communication"],
        gesture_ids=["yes"],
        scenario_tag="daily",
    ),
    Lesson(
        id="no",
        title="no",
        description="index and middle extended, snap down to meet the thumb.",
        difficulty="starter",
        tags=["daily", "communication"],
        gesture_ids=["no"],
        scenario_tag="daily",
    ),
    Lesson(
        id="bathroom",
        title="bathroom",
        description="fist with thumb peeking between index and middle — small shake.",
        difficulty="growing",
        tags=["needs", "daily"],
        gesture_ids=["bathroom"],
        scenario_tag="home",
    ),
    Lesson(
        id="pain",
        title="pain",
        description="index finger points firmly toward where it hurts.",
        difficulty="growing",
        tags=["safety", "feelings"],
        gesture_ids=["pain"],
        scenario_tag="safety",
    ),
    Lesson(
        id="tired",
        title="tired",
        description="fingers droop at the second knuckle — loose and heavy.",
        difficulty="growing",
        tags=["feelings", "daily"],
        gesture_ids=["tired"],
        scenario_tag="home",
    ),
    Lesson(
        id="play",
        title="play",
        description="'y' hand — thumb and pinky out, middle fingers curled; gentle shake.",
        difficulty="growing",
        tags=["family", "fun"],
        gesture_ids=["play"],
        scenario_tag="family",
    ),
    Lesson(
        id="sleep",
        title="sleep",
        description="soft fingers drift down the face, palm turning inward.",
        difficulty="growing",
        tags=["home", "daily"],
        gesture_ids=["sleep"],
        scenario_tag="home",
    ),
]


class LessonService:
    def list_lessons(self) -> list[Lesson]:
        return list(_SEED)


lesson_service = LessonService()
