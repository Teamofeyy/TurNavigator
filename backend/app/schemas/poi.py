from datetime import datetime

from pydantic import BaseModel, Field


class POIImage(BaseModel):
    provider: str = Field(
        description="Image source provider, for example wikimedia or opentripmap.",
        examples=["wikimedia"],
    )
    original_url: str | None = Field(
        default=None,
        description="URL of original or high-resolution image.",
        examples=["https://upload.wikimedia.org/.../example.jpg"],
    )
    thumbnail_url: str | None = Field(
        default=None,
        description="URL of resized preview image.",
        examples=["https://upload.wikimedia.org/.../320px-example.jpg"],
    )
    source_page_url: str | None = Field(
        default=None,
        description="Human-readable source page with attribution and license information.",
        examples=["https://commons.wikimedia.org/wiki/File:Example.jpg"],
    )
    license: str | None = Field(
        default=None,
        description="Image license if known.",
        examples=["CC BY-SA 4.0"],
    )
    author: str | None = Field(
        default=None,
        description="Image author if known.",
        examples=["Ivan Ivanov"],
    )
    attribution_text: str | None = Field(
        default=None,
        description="Prepared attribution text for frontend display.",
        examples=["Photo: Ivan Ivanov, CC BY-SA 4.0"],
    )
    width: int | None = Field(default=None, description="Original image width in pixels.")
    height: int | None = Field(default=None, description="Original image height in pixels.")
    is_primary: bool = Field(
        default=True,
        description="Whether the image is the primary image for the POI.",
    )


class POISourceLink(BaseModel):
    provider: str = Field(
        description="External source provider name.",
        examples=["opentripmap"],
    )
    external_id: str = Field(
        description="Identifier of the POI in the external source.",
        examples=["R4682064"],
    )
    url: str | None = Field(
        default=None,
        description="Human-readable or API URL for this source record if available.",
        examples=["https://www.wikidata.org/wiki/Q171223"],
    )
    license: str | None = Field(
        default=None,
        description="Known license associated with this source payload.",
        examples=["ODbL"],
    )
    last_synced_at: datetime | None = Field(
        default=None,
        description="Timestamp when the data from this source was last synchronized.",
    )


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
    wikipedia_title: str | None = Field(
        default=None,
        description="Wikipedia article title if linked.",
        examples=["Казанский кремль"],
    )
    wikipedia_url: str | None = Field(
        default=None,
        description="Wikipedia article URL if linked.",
        examples=["https://ru.wikipedia.org/wiki/Казанский_кремль"],
    )
    wikimedia_commons: str | None = Field(
        default=None,
        description="Wikimedia Commons file or category id if linked.",
        examples=["Category:Kazan Kremlin"],
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
    interest_source: str = Field(
        default="manual",
        description="How interest tags were assigned: manual, automatic, or mixed.",
        examples=["manual+automatic"],
    )
    primary_image: POIImage | None = Field(
        default=None,
        description="Primary image metadata for the POI.",
    )
    images: list[POIImage] = Field(
        default_factory=list,
        description="All available image candidates with attribution metadata.",
    )
    source_links: list[POISourceLink] = Field(
        default_factory=list,
        description="Provenance links to external source records used for this POI.",
    )
    data_freshness_days: int = Field(
        default=30,
        ge=0,
        description="How old the current cached POI record is in days.",
        examples=[7],
    )
    last_enriched_at: datetime | None = Field(
        default=None,
        description="Timestamp when the POI was last enriched from external sources.",
    )
