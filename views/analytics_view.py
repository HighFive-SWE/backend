from __future__ import annotations

from pydantic import BaseModel

from models.analytics import AnalyticsSnapshot


class AnalyticsResponse(BaseModel):
    analytics: AnalyticsSnapshot
