"""create knowledge tables (glossary terms + memory snapshots)

Revision ID: 202606150002
Revises: 202606150001
Create Date: 2026-06-15 00:00:02.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "202606150002"
down_revision: str | None = "202606150001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

glossary_term_scope = postgresql.ENUM(
    "segment", "chapter", "volume", "book", "project",
    name="glossary_term_scope",
    create_type=False,
)
glossary_term_status = postgresql.ENUM(
    "draft", "approved", "deprecated",
    name="glossary_term_status",
    create_type=False,
)
glossary_term_constraint = postgresql.ENUM(
    "hard", "soft",
    name="glossary_term_constraint",
    create_type=False,
)
memory_snapshot_level = postgresql.ENUM(
    "book", "volume", "chapter",
    name="memory_snapshot_level",
    create_type=False,
)


def upgrade() -> None:
    # pgvector must exist before any vector column is created. init.sql installs it on the
    # compose database; this keeps the migration self-sufficient on any fresh database too.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    bind = op.get_bind()
    glossary_term_scope.create(bind, checkfirst=True)
    glossary_term_status.create(bind, checkfirst=True)
    glossary_term_constraint.create(bind, checkfirst=True)
    memory_snapshot_level.create(bind, checkfirst=True)

    op.create_table(
        "glossary_terms",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("target", sa.String(length=255), nullable=False),
        sa.Column(
            "aliases",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("scope", glossary_term_scope, server_default="project", nullable=False),
        sa.Column("status", glossary_term_status, server_default="draft", nullable=False),
        sa.Column(
            "constraint_kind", glossary_term_constraint, server_default="soft", nullable=False
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_glossary_terms_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_glossary_terms")),
    )
    op.create_table(
        "memory_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("level", memory_snapshot_level, nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column(
            "content",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_memory_snapshots_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_memory_snapshots")),
    )


def downgrade() -> None:
    op.drop_table("memory_snapshots")
    op.drop_table("glossary_terms")
    bind = op.get_bind()
    memory_snapshot_level.drop(bind, checkfirst=True)
    glossary_term_constraint.drop(bind, checkfirst=True)
    glossary_term_status.drop(bind, checkfirst=True)
    glossary_term_scope.drop(bind, checkfirst=True)
