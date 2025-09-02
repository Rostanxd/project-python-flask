"""Add status field to User

Revision ID: 4419892819e6
Revises: f294331aa713
Create Date: 2025-08-17 21:02:42.412549
Updated Date: 2025-09-02 17:41:31.326677

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "4419892819e6"
down_revision = "f294331aa713"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Define the enum once
    generic_enum = sa.Enum("ACTIVE", "INACTIVE", name="userstatusenum")

    if dialect == "postgresql":
        # On PostgreSQL, ensure the enum type exists before using it in ALTER TABLE
        pg_enum = postgresql.ENUM(
            "ACTIVE", "INACTIVE", name="userstatusenum", create_type=True
        )
        pg_enum.create(bind, checkfirst=True)
        enum_type = pg_enum
        default_clause = sa.text("'INACTIVE'::userstatusenum")
    else:
        # SQLite and others can use the generic SQLAlchemy Enum
        enum_type = generic_enum
        default_clause = sa.text("'INACTIVE'")

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "status",
                enum_type,
                nullable=False,
                server_default=default_clause,
            )
        )

    # Drop the server_default if you don't want it for future inserts
    op.alter_column("user", "status", server_default=None, existing_type=enum_type)


def downgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Drop the column first
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("status")

    # Drop the PostgreSQL enum type after the column has been removed
    if dialect == "postgresql":
        pg_enum = postgresql.ENUM("ACTIVE", "INACTIVE", name="userstatusenum")
        pg_enum.drop(bind, checkfirst=True)
