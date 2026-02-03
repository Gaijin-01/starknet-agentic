"""
Pydantic schemas for Google Places API requests and responses.

Defines all data models used for place search, details, and location resolution.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class LatLng(BaseModel):
    """Geographic coordinates for a location."""
    lat: float = Field(ge=-90, le=90, description="Latitude in degrees")
    lng: float = Field(ge=-180, le=180, description="Longitude in degrees")


class LocationBias(BaseModel):
    """Location bias for place searches with radius."""
    lat: float = Field(ge=-90, le=90, description="Center latitude")
    lng: float = Field(ge=-180, le=180, description="Center longitude")
    radius_m: float = Field(gt=0, description="Search radius in meters")


class Filters(BaseModel):
    """Filters for place search queries."""
    types: list[str] | None = None
    open_now: bool | None = None
    min_rating: float | None = Field(default=None, ge=0, le=5)
    price_levels: list[int] | None = None
    keyword: str | None = Field(default=None, min_length=1)

    @field_validator("types")
    @classmethod
    def validate_types(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        if len(value) > 1:
            raise ValueError(
                "Only one type is supported. Use query/keyword for additional filtering."
            )
        return value

    @field_validator("price_levels")
    @classmethod
    def validate_price_levels(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return value
        invalid = [level for level in value if level not in range(0, 5)]
        if invalid:
            raise ValueError("price_levels must be integers between 0 and 4.")
        return value

    @field_validator("min_rating")
    @classmethod
    def validate_min_rating(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if (value * 2) % 1 != 0:
            raise ValueError("min_rating must be in 0.5 increments.")
        return value


class SearchRequest(BaseModel):
    """Request for text search places."""
    query: str = Field(min_length=1, description="Text search query")
    location_bias: LocationBias | None = None
    filters: Filters | None = None
    limit: int = Field(default=10, ge=1, le=20)
    page_token: str | None = None


class PlaceSummary(BaseModel):
    """Summary information for a place."""
    place_id: str
    name: str | None = None
    address: str | None = None
    location: LatLng | None = None
    rating: float | None = None
    price_level: int | None = None
    types: list[str] | None = None
    open_now: bool | None = None


class SearchResponse(BaseModel):
    """Response from text search places."""
    results: list[PlaceSummary]
    next_page_token: str | None = None


class LocationResolveRequest(BaseModel):
    """Request to resolve text location to coordinates."""
    location_text: str = Field(min_length=1, description="Location text to resolve")
    limit: int = Field(default=5, ge=1, le=10)


class ResolvedLocation(BaseModel):
    """Resolved location from text."""
    place_id: str
    name: str | None = None
    address: str | None = None
    location: LatLng | None = None
    types: list[str] | None = None


class LocationResolveResponse(BaseModel):
    """Response from location resolve."""
    results: list[ResolvedLocation]


class PlaceDetails(BaseModel):
    """Detailed information about a place."""
    place_id: str
    name: str | None = None
    address: str | None = None
    location: LatLng | None = None
    rating: float | None = None
    price_level: int | None = None
    types: list[str] | None = None
    phone: str | None = None
    website: str | None = None
    hours: list[str] | None = None
    open_now: bool | None = None
