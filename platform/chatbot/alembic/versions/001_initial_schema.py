"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('consent_given', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('consent_timestamp', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone_number')
    )
    op.create_index('idx_phone_active', 'users', ['phone_number', 'is_active'])

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False, server_default='greeting'),
        sa.Column('turn_id', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_profile', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('current_recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('qualification_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index('idx_session_user_active', 'sessions', ['user_id', 'is_active'])
    op.create_index('idx_session_expires', 'sessions', ['expires_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('message_id', sa.String(length=100), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(length=20), nullable=True, server_default='text'),
        sa.Column('media_url', sa.String(length=500), nullable=True),
        sa.Column('intent', sa.String(length=50), nullable=True),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('entities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id')
    )
    op.create_index('idx_message_session_created', 'messages', ['session_id', 'created_at'])
    op.create_index('idx_message_role', 'messages', ['role'])

    # Create qualified_leads table
    op.create_table(
        'qualified_leads',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('qualification_score', sa.Float(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('user_profile', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('recommended_cars', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('conversation_summary', sa.Text(), nullable=True),
        sa.Column('contacted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('contacted_at', sa.DateTime(), nullable=True),
        sa.Column('converted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('converted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_lead_score_priority', 'qualified_leads', ['qualification_score', 'priority'])
    op.create_index('idx_lead_contacted', 'qualified_leads', ['contacted', 'created_at'])

    # Create car_interactions table
    op.create_table(
        'car_interactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('car_id', sa.String(length=50), nullable=False),
        sa.Column('interaction_type', sa.String(length=50), nullable=False),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_car_interaction_session', 'car_interactions', ['session_id', 'created_at'])
    op.create_index('idx_car_interaction_car', 'car_interactions', ['car_id', 'interaction_type'])

    # Create human_handoffs table
    op.create_table(
        'human_handoffs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=100), nullable=False),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('assigned_to', sa.String(length=100), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_handoff_status', 'human_handoffs', ['status', 'created_at'])
    op.create_index('idx_handoff_assigned', 'human_handoffs', ['assigned_to', 'status'])

    # Create metrics_daily table
    op.create_table(
        'metrics_daily',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('total_messages', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_sessions', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_users', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_qualified_leads', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_handoffs', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('avg_response_time_ms', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('avg_qualification_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('nlp_accuracy', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('conversion_rate', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date')
    )
    op.create_index('idx_metrics_date', 'metrics_daily', ['date'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_metrics_date', table_name='metrics_daily')
    op.drop_table('metrics_daily')
    
    op.drop_index('idx_handoff_assigned', table_name='human_handoffs')
    op.drop_index('idx_handoff_status', table_name='human_handoffs')
    op.drop_table('human_handoffs')
    
    op.drop_index('idx_car_interaction_car', table_name='car_interactions')
    op.drop_index('idx_car_interaction_session', table_name='car_interactions')
    op.drop_table('car_interactions')
    
    op.drop_index('idx_lead_contacted', table_name='qualified_leads')
    op.drop_index('idx_lead_score_priority', table_name='qualified_leads')
    op.drop_table('qualified_leads')
    
    op.drop_index('idx_message_role', table_name='messages')
    op.drop_index('idx_message_session_created', table_name='messages')
    op.drop_table('messages')
    
    op.drop_index('idx_session_expires', table_name='sessions')
    op.drop_index('idx_session_user_active', table_name='sessions')
    op.drop_table('sessions')
    
    op.drop_index('idx_phone_active', table_name='users')
    op.drop_table('users')
