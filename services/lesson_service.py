from models.lesson import Lesson

# static catalog for phase 1 — replaced by a db-backed repo in phase 2.
_SEED: list[Lesson] = [
    Lesson(
        id="hello",
        title="hello",
        description="wave an open palm beside your temple, then move it outward.",
        difficulty="starter",
        tags=["greetings", "daily"],
    ),
    Lesson(
        id="thank-you",
        title="thank you",
        description="flat hand touches chin and moves forward, like blowing a kiss.",
        difficulty="starter",
        tags=["family", "manners"],
    ),
    Lesson(
        id="more",
        title="more",
        description="tap fingertips together twice — both hands pinched flat.",
        difficulty="growing",
        tags=["mealtime", "requests"],
    ),
    Lesson(
        id="please",
        title="please",
        description="flat hand draws a small circle over the chest.",
        difficulty="starter",
        tags=["manners", "daily"],
    ),
    Lesson(
        id="friend",
        title="friend",
        description="hook both index fingers together, then switch which one is on top.",
        difficulty="growing",
        tags=["people", "family"],
    ),
]


class LessonService:
    def list_lessons(self) -> list[Lesson]:
        return list(_SEED)


lesson_service = LessonService()
