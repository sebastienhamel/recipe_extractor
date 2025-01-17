"""add details model

Revision ID: 2ed771a761a4
Revises: d90025934c24
Create Date: 2025-01-17 11:46:55.857350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ed771a761a4'
down_revision: Union[str, None] = 'd90025934c24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
