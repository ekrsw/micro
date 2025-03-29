"""initial migration

Revision ID: 001
Revises: 
Create Date: 2025-03-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create category table
    op.create_table(
        'category',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
    )
    
    # Create product table
    op.create_table(
        'product',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False, default=0),
        sa.Column('sku', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
    )
    
    # Create product_category association table
    op.create_table(
        'product_category',
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('product.id'), primary_key=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('category.id'), primary_key=True),
    )


def downgrade():
    op.drop_table('product_category')
    op.drop_table('product')
    op.drop_table('category')