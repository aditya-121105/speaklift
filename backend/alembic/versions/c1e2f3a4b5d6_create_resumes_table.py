"""create resumes table

Revision ID: c1e2f3a4b5d6
Revises: 0144ba5aca6b
Create Date: 2026-07-03 12:00:00.000000

Sprint C.1 — Resume Storage Foundation

Creates the `resumes` table and its associated PostgreSQL enum types.

Enum types
----------
storageprovider  — LOCAL | S3 | AZURE | GCS
uploadstatus     — PENDING | COMPLETED | FAILED
parsingstatus    — PENDING | PROCESSING | COMPLETED | FAILED | SKIPPED

Implementation note
-------------------
We use raw SQL via op.execute() throughout rather than sa.Enum() objects.
This is the most reliable approach in Alembic when enum types may already
exist (e.g. created by a prior failed migration), since sa.Enum with
`create_type=False` still triggers the `_on_table_create` event and
attempts a CREATE TYPE statement.

Using sa.Text() for enum columns in the migration while the ORM model
uses sa.Enum() is safe — the DB column type is already the enum; SQLAlchemy
maps the enum label string correctly at runtime.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1e2f3a4b5d6"
down_revision: Union[str, Sequence[str], None] = "0144ba5aca6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_enum_if_not_exists(name: str, values: list[str]) -> None:
    """Create a PostgreSQL enum type only if it does not already exist.

    PostgreSQL 16 does not support CREATE TYPE IF NOT EXISTS.
    We check pg_type via a PL/pgSQL DO block instead.
    """
    values_sql = ", ".join(f"'{v}'" for v in values)
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{name}') THEN
                CREATE TYPE {name} AS ENUM ({values_sql});
            END IF;
        END
        $$;
        """
    )


def upgrade() -> None:
    """Create enum types (idempotent) then create the resumes table."""

    _create_enum_if_not_exists("storageprovider", ["LOCAL", "S3", "AZURE", "GCS"])
    _create_enum_if_not_exists("uploadstatus", ["PENDING", "COMPLETED", "FAILED"])
    _create_enum_if_not_exists(
        "parsingstatus",
        ["PENDING", "PROCESSING", "COMPLETED", "FAILED", "SKIPPED"],
    )

    # Use raw SQL for the table creation to avoid SQLAlchemy Enum() triggering
    # automatic CREATE TYPE statements, which would fail if the type already exists.
    op.execute(
        """
        CREATE TABLE resumes (
            id              SERIAL PRIMARY KEY,
            user_id         INTEGER NOT NULL
                                REFERENCES users(id) ON DELETE CASCADE,

            original_filename   VARCHAR(255) NOT NULL,
            stored_filename     VARCHAR(255) NOT NULL,
            file_extension      VARCHAR(10)  NOT NULL,
            mime_type           VARCHAR(100) NOT NULL,
            file_size_bytes     BIGINT       NOT NULL,

            storage_provider    storageprovider NOT NULL DEFAULT 'LOCAL',
            storage_path        TEXT            NOT NULL,

            upload_status       uploadstatus    NOT NULL DEFAULT 'PENDING',
            parsing_status      parsingstatus   NOT NULL DEFAULT 'PENDING',

            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            parsed_at   TIMESTAMPTZ
        )
        """
    )

    op.create_index(
        "ix_resumes_user_id",
        "resumes",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the resumes table and its enum types."""
    op.drop_index("ix_resumes_user_id", table_name="resumes")
    op.drop_table("resumes")

    op.execute("DROP TYPE IF EXISTS parsingstatus")
    op.execute("DROP TYPE IF EXISTS uploadstatus")
    op.execute("DROP TYPE IF EXISTS storageprovider")
