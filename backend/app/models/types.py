from __future__ import annotations

from sqlalchemy import JSON, Text
from sqlalchemy.dialects.postgresql import JSONB


def json_column_type():
    return JSON().with_variant(JSONB(astext_type=Text()), "postgresql")
