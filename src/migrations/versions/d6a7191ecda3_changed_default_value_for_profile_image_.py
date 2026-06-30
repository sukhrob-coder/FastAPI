"""changed_default_value_for_profile_image_url

Revision ID: d6a7191ecda3
Revises: 20260627_0421
Create Date: 2026-06-27 08:19:28.625092

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd6a7191ecda3'
down_revision: str | None = '20260627_0421'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(None, 'post', ['id'])
    op.create_unique_constraint(None, 'token_blacklist', ['id'])
    
    op.alter_column('user', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
               
    op.alter_column('user', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               nullable=False)


def downgrade() -> None:
    op.alter_column('user', 'updated_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
               
    op.alter_column('user', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
               
    op.drop_constraint(None, 'token_blacklist', type_='unique')
    op.drop_constraint(None, 'post', type_='unique')