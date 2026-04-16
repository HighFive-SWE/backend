from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    parent = "parent"
    child = "child"
    educator = "educator"


class AgeGroup(str, Enum):
    early = "early"       # 4-7
    middle = "middle"     # 8-12
    teen = "teen"         # 13-17
    adult = "adult"


class User(BaseModel):
    id: str
    name: str
    role: Role
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Profile(BaseModel):
    id: str
    user_id: str               # the owner account (parent/educator) this profile belongs under.
    display_name: str
    avatar: str                # "peach" | "mint" | "lilac" | "brand" — client-side palette keys.
    age_group: AgeGroup = AgeGroup.middle
    role: Role = Role.child
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
