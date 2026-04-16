from __future__ import annotations

import uuid
from typing import Iterable

from models.profile import AgeGroup, Profile, Role, User


class ProfileService:
    """
    in-memory profile + owner-account store. phase 5 has no auth or db yet —
    every process run starts with one seeded parent and two child profiles so
    the ui has something to switch between.
    """

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._profiles: dict[str, Profile] = {}
        self._seed()

    # --- seeds ------------------------------------------------------------

    def _seed(self) -> None:
        parent = User(id="user-home-1", name="home", role=Role.parent)
        self._users[parent.id] = parent

        seeds: list[Profile] = [
            Profile(
                id="profile-parent-1",
                user_id=parent.id,
                display_name="parent",
                avatar="brand",
                age_group=AgeGroup.adult,
                role=Role.parent,
            ),
            Profile(
                id="profile-alex",
                user_id=parent.id,
                display_name="alex",
                avatar="mint",
                age_group=AgeGroup.early,
                role=Role.child,
            ),
            Profile(
                id="profile-sam",
                user_id=parent.id,
                display_name="sam",
                avatar="peach",
                age_group=AgeGroup.middle,
                role=Role.child,
            ),
        ]
        for p in seeds:
            self._profiles[p.id] = p

    # --- reads ------------------------------------------------------------

    def list_profiles(self, user_id: str | None = None) -> list[Profile]:
        profiles: Iterable[Profile] = self._profiles.values()
        if user_id is not None:
            profiles = (p for p in profiles if p.user_id == user_id)
        return sorted(profiles, key=lambda p: p.created_at)

    def get_profile(self, profile_id: str) -> Profile | None:
        return self._profiles.get(profile_id)

    def exists(self, profile_id: str) -> bool:
        return profile_id in self._profiles

    # --- writes -----------------------------------------------------------

    def create_profile(
        self,
        *,
        user_id: str | None,
        display_name: str,
        avatar: str,
        age_group: AgeGroup = AgeGroup.middle,
        role: Role = Role.child,
    ) -> Profile:
        # if no owner account is passed, attach to the default seeded home.
        owner_id = user_id or next(iter(self._users), "user-home-1")
        if owner_id not in self._users:
            self._users[owner_id] = User(id=owner_id, name="home", role=Role.parent)

        profile = Profile(
            id=f"profile-{uuid.uuid4().hex[:8]}",
            user_id=owner_id,
            display_name=display_name,
            avatar=avatar,
            age_group=age_group,
            role=role,
        )
        self._profiles[profile.id] = profile
        return profile


profile_service = ProfileService()
