from pydantic import BaseModel, Field


class PointOfInterestResponse(BaseModel):
    id: int = Field(description="Internal point of interest identifier.", examples=[3001])
    city_id: int = Field(description="Internal city identifier.", examples=[3])
    name: str = Field(description="Point of interest name.", examples=["Казанский кремль"])
    category: str = Field(description="Normalized internal category.", examples=["history"])
    subcategory: str = Field(description="More specific internal subcategory.", examples=["museum_complex"])
    latitude: float = Field(description="POI latitude.", examples=[55.7996])
    longitude: float = Field(description="POI longitude.", examples=[49.1055])
    address: str = Field(description="Human-readable address.", examples=["Кремль"])
    description: str = Field(description="Short POI description.")
    opening_hours: str | None = Field(
        default=None,
        description="Opening hours in source format if available.",
        examples=["10:00-18:00"],
    )
    website: str | None = Field(
        default=None,
        description="Official or reference website if available.",
        examples=["https://kazan-kremlin.ru"],
    )
    phone: str | None = Field(
        default=None,
        description="Contact phone if available.",
        examples=["+7 (843) 292-70-70"],
    )
    source: str = Field(description="Data source identifier.", examples=["manual_seed"])
    external_id: str = Field(
        description="Stable source-specific POI identifier.",
        examples=["kazan-kremlin"],
    )
    wikidata_id: str | None = Field(
        default=None,
        description="Linked Wikidata Q-id if available.",
        examples=["Q171223"],
    )
    osm_tags: dict[str, str] = Field(
        description="Source-like OSM tags used for category mapping.",
        examples=[{"tourism": "museum"}],
    )
    estimated_price_level: str = Field(
        description="Estimated price level for planning constraints.",
        examples=["medium"],
    )
    average_cost_rub: int = Field(
        ge=0,
        description="Approximate expected cost in Russian rubles.",
        examples=[1200],
    )
    estimated_visit_minutes: int = Field(
        ge=0,
        description="Approximate visit duration in minutes.",
        examples=[90],
    )
    popularity_score: float = Field(
        ge=0,
        le=1,
        description="Normalized popularity estimate from 0 to 1.",
        examples=[0.92],
    )
    data_quality_score: float = Field(
        ge=0,
        le=1,
        description="Normalized confidence/data quality estimate from 0 to 1.",
        examples=[0.86],
    )
    interests: list[str] = Field(
        description="Interest tags used by the recommendation engine.",
        examples=[["history", "architecture", "culture"]],
    )
