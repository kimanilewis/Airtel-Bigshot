"""
Database migrations for Airtel Kenya C2B IPN system using Alembic.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import Enum
import enum

# Revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

# Enum classes for migration
class CustomerStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    PROCESSED = "processed"
    FAILED = "failed"

def upgrade():
    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bill_ref', sa.String(100), nullable=False),
        sa.Column('ref_type', sa.String(50), nullable=False),
        sa.Column('msisdn', sa.String(20), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('id_number', sa.String(50), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('status', sa.Enum(CustomerStatus), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bill_ref', 'ref_type', name='uix_bill_ref_ref_type')
    )
    op.create_index('ix_customers_bill_ref', 'customers', ['bill_ref'])
    op.create_index('ix_customers_msisdn', 'customers', ['msisdn'])
    
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.String(100), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('bill_ref', sa.String(100), nullable=False),
        sa.Column('ref_type', sa.String(50), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('msisdn', sa.String(20), nullable=False),
        sa.Column('merchant_msisdn', sa.String(20), nullable=True),
        sa.Column('payment_date', sa.DateTime(), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False, server_default='KES'),
        sa.Column('status', sa.Enum(TransactionStatus), nullable=False, server_default='PENDING'),
        sa.Column('airtel_reference', sa.String(100), nullable=True),
        sa.Column('mobiquity_reference', sa.String(100), nullable=True),
        sa.Column('raw_payload', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id')
    )
    op.create_index('ix_transactions_bill_ref', 'transactions', ['bill_ref'])
    op.create_index('ix_transactions_transaction_id', 'transactions', ['transaction_id'])
    
    # Create validation_results table
    op.create_table(
        'validation_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('is_valid', sa.Boolean(), nullable=False),
        sa.Column('validation_message', sa.String(255), nullable=True),
        sa.Column('validation_date', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create processing_results table
    op.create_table(
        'processing_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('is_processed', sa.Boolean(), nullable=False),
        sa.Column('processing_message', sa.String(255), nullable=True),
        sa.Column('processing_date', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create users table for JWT authentication
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

def downgrade():
    # Drop tables in reverse order
    op.drop_table('users')
    op.drop_table('processing_results')
    op.drop_table('validation_results')
    op.drop_table('transactions')
    op.drop_table('customers')
