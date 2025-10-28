"""Seed test data

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 10:30:00.000000

"""
from typing import Sequence, Union
from datetime import datetime, timedelta

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert seed data for testing"""
    
    # Define tables for bulk insert
    users_table = table(
        'users',
        column('id', sa.Integer),
        column('phone_number', sa.String),
        column('name', sa.String),
        column('email', sa.String),
        column('consent_given', sa.Boolean),
        column('consent_timestamp', sa.DateTime),
        column('created_at', sa.DateTime),
        column('is_active', sa.Boolean),
    )
    
    sessions_table = table(
        'sessions',
        column('id', sa.Integer),
        column('session_id', sa.String),
        column('user_id', sa.Integer),
        column('state', sa.String),
        column('turn_id', sa.Integer),
        column('user_profile', sa.JSON),
        column('qualification_score', sa.Float),
        column('created_at', sa.DateTime),
        column('expires_at', sa.DateTime),
        column('is_active', sa.Boolean),
    )
    
    messages_table = table(
        'messages',
        column('id', sa.Integer),
        column('message_id', sa.String),
        column('session_id', sa.Integer),
        column('role', sa.String),
        column('content', sa.Text),
        column('message_type', sa.String),
        column('intent', sa.String),
        column('sentiment', sa.String),
        column('confidence', sa.Float),
        column('created_at', sa.DateTime),
    )
    
    qualified_leads_table = table(
        'qualified_leads',
        column('id', sa.Integer),
        column('user_id', sa.Integer),
        column('session_id', sa.String),
        column('qualification_score', sa.Float),
        column('priority', sa.String),
        column('user_profile', sa.JSON),
        column('conversation_summary', sa.Text),
        column('contacted', sa.Boolean),
        column('created_at', sa.DateTime),
    )
    
    # Insert test users
    now = datetime.utcnow()
    op.bulk_insert(
        users_table,
        [
            {
                'id': 1,
                'phone_number': '+5511999999001',
                'name': 'João Silva',
                'email': 'joao.silva@example.com',
                'consent_given': True,
                'consent_timestamp': now,
                'created_at': now,
                'is_active': True,
            },
            {
                'id': 2,
                'phone_number': '+5511999999002',
                'name': 'Maria Santos',
                'email': 'maria.santos@example.com',
                'consent_given': True,
                'consent_timestamp': now,
                'created_at': now,
                'is_active': True,
            },
            {
                'id': 3,
                'phone_number': '+5511999999003',
                'name': 'Pedro Oliveira',
                'email': 'pedro.oliveira@example.com',
                'consent_given': True,
                'consent_timestamp': now,
                'created_at': now,
                'is_active': True,
            },
        ]
    )
    
    # Insert test sessions
    expires_at = now + timedelta(hours=24)
    op.bulk_insert(
        sessions_table,
        [
            {
                'id': 1,
                'session_id': 'session_001',
                'user_id': 1,
                'state': 'collecting_profile',
                'turn_id': 3,
                'user_profile': {
                    'orcamento_min': 40000,
                    'orcamento_max': 60000,
                    'uso_principal': 'trabalho',
                    'city': 'São Paulo',
                    'state': 'SP',
                },
                'qualification_score': 45.0,
                'created_at': now,
                'expires_at': expires_at,
                'is_active': True,
            },
            {
                'id': 2,
                'session_id': 'session_002',
                'user_id': 2,
                'state': 'showing_recommendations',
                'turn_id': 8,
                'user_profile': {
                    'orcamento_min': 80000,
                    'orcamento_max': 120000,
                    'uso_principal': 'família',
                    'city': 'Rio de Janeiro',
                    'state': 'RJ',
                    'prioridades': {
                        'seguranca': 5,
                        'espaco': 5,
                        'conforto': 4,
                    },
                },
                'qualification_score': 75.0,
                'created_at': now,
                'expires_at': expires_at,
                'is_active': True,
            },
        ]
    )
    
    # Insert test messages
    op.bulk_insert(
        messages_table,
        [
            {
                'id': 1,
                'message_id': 'msg_001',
                'session_id': 1,
                'role': 'user',
                'content': 'Olá, quero comprar um carro',
                'message_type': 'text',
                'intent': 'greeting',
                'sentiment': 'neutral',
                'confidence': 0.95,
                'created_at': now,
            },
            {
                'id': 2,
                'message_id': 'msg_002',
                'session_id': 1,
                'role': 'assistant',
                'content': 'Olá! Bem-vindo ao FacilIAuto! Qual é o seu orçamento?',
                'message_type': 'text',
                'intent': None,
                'sentiment': 'positive',
                'confidence': None,
                'created_at': now + timedelta(seconds=1),
            },
            {
                'id': 3,
                'message_id': 'msg_003',
                'session_id': 1,
                'role': 'user',
                'content': 'Tenho até 50 mil reais',
                'message_type': 'text',
                'intent': 'budget_inquiry',
                'sentiment': 'neutral',
                'confidence': 0.92,
                'created_at': now + timedelta(seconds=30),
            },
            {
                'id': 4,
                'message_id': 'msg_004',
                'session_id': 2,
                'role': 'user',
                'content': 'Preciso de um carro para minha família',
                'message_type': 'text',
                'intent': 'car_recommendation',
                'sentiment': 'neutral',
                'confidence': 0.88,
                'created_at': now,
            },
        ]
    )
    
    # Insert test qualified lead
    op.bulk_insert(
        qualified_leads_table,
        [
            {
                'id': 1,
                'user_id': 2,
                'session_id': 'session_002',
                'qualification_score': 75.0,
                'priority': 'high',
                'user_profile': {
                    'orcamento_min': 80000,
                    'orcamento_max': 120000,
                    'uso_principal': 'família',
                    'city': 'Rio de Janeiro',
                    'state': 'RJ',
                    'prioridades': {
                        'seguranca': 5,
                        'espaco': 5,
                        'conforto': 4,
                    },
                },
                'conversation_summary': 'Cliente procura SUV para família, prioriza segurança e espaço',
                'contacted': False,
                'created_at': now,
            },
        ]
    )


def downgrade() -> None:
    """Remove seed data"""
    # Delete in reverse order due to foreign keys
    op.execute("DELETE FROM qualified_leads WHERE id IN (1)")
    op.execute("DELETE FROM messages WHERE id IN (1, 2, 3, 4)")
    op.execute("DELETE FROM sessions WHERE id IN (1, 2)")
    op.execute("DELETE FROM users WHERE id IN (1, 2, 3)")
