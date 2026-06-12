import pytest
from starlette.testclient import TestClient

from main import app
from vision.gestures.samples import GESTURES


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def landmarks_for(gesture_id: str = "hello") -> list[dict]:
    """Return 21 landmark dicts from the real gesture reference array."""
    pts = GESTURES[gesture_id].tolist()
    return [{"x": float(p[0]), "y": float(p[1]), "z": float(p[2])} for p in pts]
