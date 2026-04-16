from __future__ import annotations

from fastapi import HTTPException

from services.profile_service import ProfileService, profile_service
from views.profile_view import ProfileCreateRequest, ProfileListResponse, ProfileResponse


class ProfileController:
    def __init__(self, service: ProfileService = profile_service) -> None:
        self._service = service

    def list(self, user_id: str | None = None) -> ProfileListResponse:
        return ProfileListResponse(profiles=self._service.list_profiles(user_id))

    def get(self, profile_id: str) -> ProfileResponse:
        profile = self._service.get_profile(profile_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="profile not found")
        return ProfileResponse(profile=profile)

    def create(self, payload: ProfileCreateRequest) -> ProfileResponse:
        profile = self._service.create_profile(
            user_id=payload.user_id,
            display_name=payload.display_name,
            avatar=payload.avatar,
            age_group=payload.age_group,
            role=payload.role,
        )
        return ProfileResponse(profile=profile)


profile_controller = ProfileController()
