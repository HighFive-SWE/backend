from __future__ import annotations

from pydantic import BaseModel, Field

from models.profile import AgeGroup, Profile, Role


class ProfileCreateRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=40)
    avatar: str = Field(min_length=1, max_length=24)
    age_group: AgeGroup = AgeGroup.middle
    role: Role = Role.child
    user_id: str | None = None  # optional owner account — falls back to seeded home.


class ProfileResponse(BaseModel):
    profile: Profile


class ProfileListResponse(BaseModel):
    profiles: list[Profile]
