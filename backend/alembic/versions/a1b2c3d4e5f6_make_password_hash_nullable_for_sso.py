"""make_password_hash_nullable_for_sso

Revision ID: a1b2c3d4e5f6
Revises: eae03169a97c
Create Date: 2026-05-14

SSO users (Microsoft Entra ID) authenticate via id_token and do not
have a platform-managed password. Making this column nullable lets us
create/import such users without storing a sentinel value.
"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "eae03169a97c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(255),
        nullable=True,
    )


def downgrade() -> None:
    # Before reverting, any NULL values must be patched — set a placeholder.
    op.execute("UPDATE users SET password_hash = 'SSO_USER' WHERE password_hash IS NULL")
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(255),
        nullable=False,
    )
