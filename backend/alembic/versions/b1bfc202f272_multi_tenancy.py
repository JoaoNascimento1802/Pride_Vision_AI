# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

from alembic import op

revision: str = 'b1bfc202f272'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if 'tenants' not in existing_tables:
        tenant_table = op.create_table('tenants',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=120), nullable=False),
            sa.Column('domain', sa.String(length=120), nullable=True),
            sa.Column('sso_config', sa.JSON(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_tenants_domain'), 'tenants', ['domain'], unique=True)

        op.create_table('tenant_users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('tenant_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('role', sa.String(length=20), nullable=False),
            sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['usuarios.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

        op.bulk_insert(tenant_table, [
            {'id': 1, 'name': 'Default Organization', 'domain': 'default.local', 'sso_config': None}
        ])

        op.execute("""
            INSERT INTO tenant_users (tenant_id, user_id, role)
            SELECT 1, id, role FROM usuarios
        """)

    tables = ['aplicacoes', 'policies', 'integrations']

    for table in tables:
        if table in existing_tables:
            columns = [c['name'] for c in inspector.get_columns(table)]
            if 'tenant_id' not in columns:
                with op.batch_alter_table(table, schema=None) as batch_op:
                    batch_op.add_column(sa.Column('tenant_id', sa.Integer(), server_default='1', nullable=False))
                    batch_op.create_foreign_key(f"fk_{table}_tenant", 'tenants', ['tenant_id'], ['id'])

def downgrade() -> None:
    pass
