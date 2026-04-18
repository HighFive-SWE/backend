from fastapi import APIRouter, Path, Query

from controllers.profile_controller import profile_controller
from views.profile_view import ProfileCreateRequest, ProfileListResponse, ProfileResponse

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("", response_model=ProfileListResponse)
def list_profiles(
    user_id: str | None = Query(default=None, max_length=64),
) -> ProfileListResponse:
    return profile_controller.list(user_id)


@router.post("", response_model=ProfileResponse)
def create_profile(payload: ProfileCreateRequest) -> ProfileResponse:
    return profile_controller.create(payload)


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: str = Path(max_length=64)) -> ProfileResponse:
    return profile_controller.get(profile_id)
