"""detail model changes

Revision ID: 2c46aed6316c
Revises: 2ed771a761a4
Create Date: 2025-01-17 15:47:01.055547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c46aed6316c'
down_revision: Union[str, None] = '2ed771a761a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
