# type: ignore
"""init

Revision ID: b33b7f1955fc
Revises: 
Create Date: 2025-04-07 23:17:34.453849+00:00

"""
from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op
from advanced_alchemy.types import EncryptedString, EncryptedText, GUID, ORA_JSONB, DateTimeUTC
from sqlalchemy import Text  # noqa: F401

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ["downgrade", "upgrade", "schema_upgrades", "schema_downgrades", "data_upgrades", "data_downgrades"]

sa.GUID = GUID
sa.DateTimeUTC = DateTimeUTC
sa.ORA_JSONB = ORA_JSONB
sa.EncryptedString = EncryptedString
sa.EncryptedText = EncryptedText

# revision identifiers, used by Alembic.
revision = 'b33b7f1955fc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        #with op.get_context().autocommit_block():
        schema_upgrades()
        data_upgrades()

def downgrade() -> None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        #with op.get_context().autocommit_block():
        data_downgrades()
        schema_downgrades()

def schema_upgrades() -> None:
    """schema upgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False, comment='User email address.'),
    sa.Column('password', sa.String(length=255), nullable=False, comment='User password (encrypted or hashed).'),
    sa.Column('role', sa.Enum('DEVELOPER', 'ADMIN', 'MANAGER', 'USER', 'GUEST', name='roletype', native_enum=False, length=50), nullable=False, comment='User role in the system.'),
    sa.Column('created_at', sa.DateTimeUTC(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTimeUTC(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email', name='uq_user_email')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index('idx_user_email', ['email'], unique=False)

    op.create_table('session',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
    sa.Column('user_id', sa.BIGINT(), nullable=False, comment='Foreign key referencing the User table.'),
    sa.Column('refresh_token', sa.String(length=255), nullable=False, comment='Refresh Token (encrypted or hashed).'),
    sa.Column('fingerprint', sa.String(length=255), nullable=False, comment='Browser fingerprint.'),
    sa.Column('user_agent', sa.String(length=255), nullable=False, comment="Users's user-agent string."),
    sa.Column('ip', sa.String(length=15), nullable=False, comment="User's IP address."),
    sa.Column('expires_at', sa.DateTimeUTC(timezone=True), nullable=False, comment='Expiration date and time of the refresh token (ISO 8601 format).'),
    sa.Column('created_at', sa.DateTimeUTC(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTimeUTC(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['auth.user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refresh_token', name='uq_refresh_session_refresh_token')
    )
    # ### end Alembic commands ###

def schema_downgrades() -> None:
    """schema downgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('session')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('idx_user_email')

    op.drop_table('user')
    # ### end Alembic commands ###

def data_upgrades() -> None:
    """Add any optional data upgrade migrations here!"""

def data_downgrades() -> None:
    """Add any optional data downgrade migrations here!"""
