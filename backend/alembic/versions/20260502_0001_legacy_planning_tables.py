"""Legacy placeholder for early planning persistence revision.

Revision ID: 20260502_0001
Revises: 20260427_0001
Create Date: 2026-05-02 14:45:00
"""

from __future__ import annotations


# revision identifiers, used by Alembic.
revision = "20260502_0001"
down_revision = "20260427_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Compatibility shim for local databases created from an earlier branch."""


def downgrade() -> None:
    """Compatibility shim for local databases created from an earlier branch."""
