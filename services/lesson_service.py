from models.lesson import Lesson

# static catalog for phase 1-3 — replaced by a db-backed repo later.
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
        id="water",
        title="water",
        description="form a 'w' with three fingers; tap it against your chin.",
        difficulty="starter",
        tags=["mealtime", "needs"],
        gesture_ids=["water"],
        scenario_tag="daily",
    ),
    Lesson(
        id="thank-you",
        title="thank you",
        description="flat hand touches chin and moves forward, like blowing a kiss.",
        difficulty="starter",
        tags=["family", "manners"],
        gesture_ids=[],
        scenario_tag="daily",
    ),
    Lesson(
        id="more",
        title="more",
        description="tap fingertips together twice — both hands pinched flat.",
        difficulty="growing",
        tags=["mealtime", "requests"],
        gesture_ids=[],
        scenario_tag="mealtime",
    ),
    Lesson(
        id="friend",
        title="friend",
        description="hook both index fingers together, then switch which one is on top.",
        difficulty="growing",
        tags=["people", "family"],
        gesture_ids=[],
        scenario_tag="family",
    ),
]


class LessonService:
    def list_lessons(self) -> list[Lesson]:
        return list(_SEED)


lesson_service = LessonService()
