from pydantic import BaseModel, Field


class CityBase(BaseModel):
    id: int = Field(description="Internal city identifier.", examples=[3])
    name: str = Field(description="City name.", examples=["Казань"])
    region: str = Field(description="Russian region name.", examples=["Республика Татарстан"])
    country: str = Field(description="Country name.", examples=["Россия"])
    latitude: float = Field(description="City center latitude.", examples=[55.7961])
    longitude: float = Field(description="City center longitude.", examples=[49.1064])
    population: int = Field(description="Approximate city population.", examples=[1300000])
    source: str = Field(description="Data source identifier.", examples=["manual_seed"])
    external_id: str = Field(description="Stable source-specific city identifier.", examples=["kazan"])
    wikidata_id: str | None = Field(
        default=None,
        description="Linked Wikidata Q-id if available.",
        examples=["Q900"],
    )
    osm_id: int | None = Field(
        default=None,
        description="Linked OpenStreetMap object id if available.",
        examples=[123456],
    )


class CityResponse(CityBase):
    pois_count: int = Field(
        description="Number of points of interest currently available for the city.",
        examples=[8],
    )
