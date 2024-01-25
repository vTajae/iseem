from alembic import op
import sqlalchemy as sa

def upgrade():
    tokentype = sa.Enum('ACCESS', 'REFRESH', name='tokentype')
    tokentype.create(op.get_bind(), checkfirst=True)

def downgrade():
    op.execute('DROP TYPE IF EXISTS tokentype')
