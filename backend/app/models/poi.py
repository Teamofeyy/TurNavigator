from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.types import json_column_type

if TYPE_CHECKING:
    from app.models.city import City


class POI(Base):
    __tablename__ = "pois"
    __table_args__ = (
        UniqueConstraint("source", "external_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subcategory: Mapped[str] = mapped_column(String(128), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    opening_hours: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(512), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="manual_seed")
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    wikidata_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    wikipedia_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    wikipedia_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    wikimedia_commons: Mapped[str | None] = mapped_column(String(255), nullable=True)
    osm_tags: Mapped[dict[str, Any]] = mapped_column(json_column_type(), nullable=False, default=dict)
    estimated_price_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    average_cost_rub: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_visit_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    popularity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    data_quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    interests: Mapped[list[str]] = mapped_column(json_column_type(), nullable=False, default=list)
    interest_source: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    data_freshness_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    last_enriched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    city: Mapped["City"] = relationship(back_populates="pois")
    images: Mapped[list["POIImage"]] = relationship(
        back_populates="poi",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    source_links: Mapped[list["POISourceLink"]] = relationship(
        back_populates="poi",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class POIImage(Base):
    __tablename__ = "poi_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    poi_id: Mapped[int] = mapped_column(
        ForeignKey("pois.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    original_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_page_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    license: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attribution_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    poi: Mapped["POI"] = relationship(back_populates="images")


class POISourceLink(Base):
    __tablename__ = "poi_source_links"
    __table_args__ = (
        UniqueConstraint("poi_id", "provider", "external_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    poi_id: Mapped[int] = mapped_column(
        ForeignKey("pois.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    license: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    poi: Mapped["POI"] = relationship(back_populates="source_links")
