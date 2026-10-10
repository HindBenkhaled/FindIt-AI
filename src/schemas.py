"""Validated input and explicit public/private API contracts."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.config import CAMPUS_LOCATIONS, CATEGORIES, HANDOVER_LOCATIONS

ReportType = Literal["lost", "found"]
Method = Literal["keyword", "baseline", "text", "image", "text_image", "full"]
ClaimStatus = Literal["pending", "approved", "rejected"]


class ItemCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    report_type: ReportType
    name: str = Field(min_length=2, max_length=120)
    category: str
    description: str = Field(min_length=3, max_length=3000)
    location: str | None
    location_detail: str | None = Field(default=None, max_length=300)
    event_date: date | None = None
    identifying_details: str | None = Field(default=None, max_length=2000)
    handover_location: str | None = None

    @field_validator("category")
    @classmethod
    def known_category(cls, value: str) -> str:
        if value not in CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(CATEGORIES)}")
        return value

    @field_validator("location")
    @classmethod
    def known_location(cls, value: str | None) -> str:
        if not value:
            raise ValueError("Campus location is required")
        if value not in CAMPUS_LOCATIONS:
            raise ValueError(f"Location must be one of: {', '.join(CAMPUS_LOCATIONS)}")
        return value

    @field_validator("location_detail", "identifying_details")
    @classmethod
    def blank_optional_text(cls, value: str | None) -> str | None:
        return value or None

    @field_validator("handover_location")
    @classmethod
    def known_handover(cls, value: str | None) -> str | None:
        if value and value not in HANDOVER_LOCATIONS:
            raise ValueError(f"Handover location must be one of: {', '.join(HANDOVER_LOCATIONS)}")
        return value or None


class ItemRead(ItemCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    image_path: str | None
    created_at: datetime


class PublicItemPreview(BaseModel):
    id: int
    report_type: ReportType
    name: str
    category: str
    description: str | None
    location: str | None
    event_date: date | None
    image_available: bool
    created_at: datetime


class MatchRead(BaseModel):
    item: PublicItemPreview
    score: float
    label: str
    components: dict[str, float | None]
    effective_weights: dict[str, float]


class MatchesRead(BaseModel):
    query_id: int
    method: Method
    candidate_count: int
    excluded_count: int
    matches: list[MatchRead]
    note: str = "Ranking scores are heuristic similarities, not calibrated probabilities."


class ClaimCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    lost_report_id: int
    found_report_id: int
    verification_response: str = Field(min_length=10, max_length=3000)


class ClaimPublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lost_report_id: int
    found_report_id: int
    status: ClaimStatus
    collection_point: str | None
    created_at: datetime


class ClaimStaffRead(ClaimPublicRead):
    verification_response: str
    lost_item: ItemRead
    found_item: ItemRead


class ClaimReview(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    status: Literal["approved", "rejected"]
    collection_point: str | None = None

    @field_validator("collection_point")
    @classmethod
    def valid_collection_point(cls, value: str | None) -> str | None:
        if value and value not in HANDOVER_LOCATIONS:
            raise ValueError(f"Collection point must be one of: {', '.join(HANDOVER_LOCATIONS)}")
        return value or None
