"""upgrade_question_bank_metadata

Revision ID: 0144ba5aca6b
Revises: bd4b041b5ffe
Create Date: 2026-06-30 08:51:46.283024

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0144ba5aca6b"
down_revision: Union[str, Sequence[str], None] = "bd4b041b5ffe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema.
    """

    op.add_column(
        "question_bank",
        sa.Column(
            "skills",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
    )

    op.add_column(
        "question_bank",
        sa.Column(
            "technologies",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
    )

    op.add_column(
        "question_bank",
        sa.Column(
            "expected_concepts",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
    )

    op.add_column(
        "question_bank",
        sa.Column(
            "has_follow_up",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    """
    Downgrade schema.
    """

    op.drop_column(
        "question_bank",
        "has_follow_up",
    )

    op.drop_column(
        "question_bank",
        "expected_concepts",
    )

    op.drop_column(
        "question_bank",
        "technologies",
    )

    op.drop_column(
        "question_bank",
        "skills",
    )