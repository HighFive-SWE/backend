from pydantic import BaseModel

from models.lesson import Lesson


class LessonsResponse(BaseModel):
    lessons: list[Lesson]


class HealthResponse(BaseModel):
    status: str
    env: str
