"""Create initial catalog tables.

Revision ID: 20260427_0001
Revises:
Create Date: 2026-04-27 13:05:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260427_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("region", sa.String(length=255), nullable=False),
        sa.Column("country", sa.String(length=255), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("population", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("wikidata_id", sa.String(length=32), nullable=True),
        sa.Column("osm_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cities")),
        sa.UniqueConstraint("external_id", name=op.f("uq_cities_external_id")),
        sa.UniqueConstraint("osm_id", name=op.f("uq_cities_osm_id")),
    )
    op.create_index(op.f("ix_cities_name"), "cities", ["name"], unique=False)
    op.create_index(op.f("ix_cities_wikidata_id"), "cities", ["wikidata_id"], unique=False)

    op.create_table(
        "pois",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("city_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("subcategory", sa.String(length=128), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("opening_hours", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=512), nullable=True),
        sa.Column("phone", sa.String(length=128), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("wikidata_id", sa.String(length=32), nullable=True),
        sa.Column("wikipedia_title", sa.String(length=255), nullable=True),
        sa.Column("wikipedia_url", sa.String(length=512), nullable=True),
        sa.Column("wikimedia_commons", sa.String(length=255), nullable=True),
        sa.Column("osm_tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("estimated_price_level", sa.String(length=32), nullable=False),
        sa.Column("average_cost_rub", sa.Integer(), nullable=False),
        sa.Column("estimated_visit_minutes", sa.Integer(), nullable=False),
        sa.Column("popularity_score", sa.Float(), nullable=False),
        sa.Column("data_quality_score", sa.Float(), nullable=False),
        sa.Column("interests", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("interest_source", sa.String(length=32), nullable=False),
        sa.Column("data_freshness_days", sa.Integer(), nullable=False),
        sa.Column("last_enriched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"], name=op.f("fk_pois_city_id_cities"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pois")),
        sa.UniqueConstraint("source", "external_id", name=op.f("uq_pois_source")),
    )
    op.create_index(op.f("ix_pois_category"), "pois", ["category"], unique=False)
    op.create_index(op.f("ix_pois_city_id"), "pois", ["city_id"], unique=False)
    op.create_index(op.f("ix_pois_name"), "pois", ["name"], unique=False)
    op.create_index(op.f("ix_pois_wikidata_id"), "pois", ["wikidata_id"], unique=False)

    op.create_table(
        "poi_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("poi_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("original_url", sa.String(length=1024), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=1024), nullable=True),
        sa.Column("source_page_url", sa.String(length=1024), nullable=True),
        sa.Column("license", sa.String(length=255), nullable=True),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("attribution_text", sa.Text(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["poi_id"], ["pois.id"], name=op.f("fk_poi_images_poi_id_pois"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_poi_images")),
    )
    op.create_index(op.f("ix_poi_images_poi_id"), "poi_images", ["poi_id"], unique=False)

    op.create_table(
        "poi_source_links",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("poi_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=True),
        sa.Column("license", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["poi_id"], ["pois.id"], name=op.f("fk_poi_source_links_poi_id_pois"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_poi_source_links")),
        sa.UniqueConstraint("poi_id", "provider", "external_id", name=op.f("uq_poi_source_links_poi_id")),
    )
    op.create_index(op.f("ix_poi_source_links_poi_id"), "poi_source_links", ["poi_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_poi_source_links_poi_id"), table_name="poi_source_links")
    op.drop_table("poi_source_links")
    op.drop_index(op.f("ix_poi_images_poi_id"), table_name="poi_images")
    op.drop_table("poi_images")
    op.drop_index(op.f("ix_pois_wikidata_id"), table_name="pois")
    op.drop_index(op.f("ix_pois_name"), table_name="pois")
    op.drop_index(op.f("ix_pois_city_id"), table_name="pois")
    op.drop_index(op.f("ix_pois_category"), table_name="pois")
    op.drop_table("pois")
    op.drop_index(op.f("ix_cities_wikidata_id"), table_name="cities")
    op.drop_index(op.f("ix_cities_name"), table_name="cities")
    op.drop_table("cities")
