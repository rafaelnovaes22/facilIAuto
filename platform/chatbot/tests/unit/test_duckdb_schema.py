"""
Unit tests for DuckDB schema
"""

import pytest
import duckdb
from datetime import datetime

from src.models.duckdb_schema import DuckDBSchema


@pytest.fixture
def duckdb_conn():
    """Create in-memory DuckDB connection for testing"""
    conn = duckdb.connect(":memory:")
    DuckDBSchema.create_tables(conn)
    yield conn
    conn.close()


class TestDuckDBSchema:
    """Tests for DuckDB schema creation"""

    def test_create_tables(self, duckdb_conn):
        """Test that all tables are created"""
        tables = duckdb_conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()

        table_names = [t[0] for t in tables]
        assert "conversation_context" in table_names
        assert "message_history" in table_names
        assert "message_embeddings" in table_names

    def test_conversation_context_schema(self, duckdb_conn):
        """Test conversation_context table schema"""
        columns = duckdb_conn.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = 'conversation_context'"
        ).fetchall()

        column_dict = {col[0]: col[1] for col in columns}
        assert "session_id" in column_dict
        assert "phone_number" in column_dict
        assert "summary" in column_dict
        assert "key_entities" in column_dict
        assert "user_profile" in column_dict


class TestConversationContext:
    """Tests for conversation context operations"""

    def test_insert_conversation_context(self, duckdb_conn):
        """Test inserting conversation context"""
        DuckDBSchema.insert_conversation_context(
            duckdb_conn,
            session_id="session_001",
            phone_number="+5511999999999",
            turn_id=1,
            summary="User asked about car recommendations",
            key_entities={"budget": 50000, "city": "São Paulo"},
            user_profile={"orcamento_min": 40000, "orcamento_max": 60000},
            state="collecting_profile",
        )

        result = duckdb_conn.execute(
            "SELECT * FROM conversation_context WHERE session_id = 'session_001'"
        ).fetchone()

        assert result is not None
        assert result[1] == "session_001"  # session_id
        assert result[2] == "+5511999999999"  # phone_number

    def test_get_conversation_context(self, duckdb_conn):
        """Test retrieving conversation context"""
        # Insert test data
        DuckDBSchema.insert_conversation_context(
            duckdb_conn,
            session_id="session_002",
            phone_number="+5511999999998",
            turn_id=5,
            summary="User interested in SUVs",
            key_entities={"vehicle_type": "SUV"},
            user_profile={"uso_principal": "família"},
            state="showing_recommendations",
        )

        # Retrieve
        context = DuckDBSchema.get_conversation_context(duckdb_conn, "session_002")

        assert context is not None
        assert context["session_id"] == "session_002"
        assert context["turn_id"] == 5
        assert context["summary"] == "User interested in SUVs"


class TestMessageHistory:
    """Tests for message history operations"""

    def test_insert_message_history(self, duckdb_conn):
        """Test inserting message history"""
        DuckDBSchema.insert_message_history(
            duckdb_conn,
            message_id="msg_001",
            session_id="session_003",
            phone_number="+5511999999997",
            role="user",
            content="Quero comprar um carro",
            message_type="text",
            intent="greeting",
            sentiment="neutral",
            confidence=0.95,
            entities=[{"type": "intent", "value": "greeting"}],
            response_time_ms=150,
        )

        result = duckdb_conn.execute(
            "SELECT * FROM message_history WHERE message_id = 'msg_001'"
        ).fetchone()

        assert result is not None
        assert result[1] == "msg_001"  # message_id
        assert result[4] == "user"  # role
        assert result[7] == "greeting"  # intent

    def test_get_message_history(self, duckdb_conn):
        """Test retrieving message history"""
        # Insert multiple messages
        for i in range(5):
            DuckDBSchema.insert_message_history(
                duckdb_conn,
                message_id=f"msg_{i}",
                session_id="session_004",
                phone_number="+5511999999996",
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
            )

        # Retrieve
        history = DuckDBSchema.get_message_history(duckdb_conn, "session_004", limit=10)

        assert len(history) == 5
        assert history[0]["message_id"] in ["msg_0", "msg_1", "msg_2", "msg_3", "msg_4"]


class TestMessageEmbeddings:
    """Tests for message embeddings operations"""

    def test_insert_message_embedding(self, duckdb_conn):
        """Test inserting message embedding"""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 10  # 50-dim vector

        DuckDBSchema.insert_message_embedding(
            duckdb_conn,
            message_id="msg_emb_001",
            session_id="session_005",
            phone_number="+5511999999995",
            content="Test message for embedding",
            embedding=embedding,
            model_name="test-model",
        )

        result = duckdb_conn.execute(
            "SELECT * FROM message_embeddings WHERE message_id = 'msg_emb_001'"
        ).fetchone()

        assert result is not None
        assert result[1] == "msg_emb_001"  # message_id
        assert len(result[4]) == 50  # embedding dimension

    def test_search_similar_messages(self, duckdb_conn):
        """Test semantic search with embeddings"""
        # Insert test embeddings
        base_embedding = [0.1] * 50

        for i in range(3):
            embedding = [0.1 + (i * 0.01)] * 50
            DuckDBSchema.insert_message_embedding(
                duckdb_conn,
                message_id=f"msg_search_{i}",
                session_id="session_006",
                phone_number="+5511999999994",
                content=f"Test message {i}",
                embedding=embedding,
            )

        # Search
        query_embedding = [0.11] * 50
        results = DuckDBSchema.search_similar_messages(
            duckdb_conn, query_embedding, phone_number="+5511999999994", limit=2
        )

        assert len(results) <= 2
        # Results should be ordered by similarity
        if len(results) > 1:
            assert results[0]["similarity"] >= results[1]["similarity"]


class TestAnalytics:
    """Tests for analytics queries"""

    def test_get_analytics_summary(self, duckdb_conn):
        """Test analytics summary"""
        # Insert test data
        for i in range(10):
            DuckDBSchema.insert_message_history(
                duckdb_conn,
                message_id=f"msg_analytics_{i}",
                session_id=f"session_{i % 3}",
                phone_number=f"+551199999999{i % 2}",
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                sentiment="positive" if i % 3 == 0 else "neutral",
                confidence=0.9,
                response_time_ms=100 + (i * 10),
            )

        # Get summary
        summary = DuckDBSchema.get_analytics_summary(
            duckdb_conn, start_date="2020-01-01", end_date="2030-12-31"
        )

        assert summary["total_messages"] == 10
        assert summary["total_sessions"] == 3
        assert summary["total_users"] == 2
        assert summary["avg_response_time_ms"] > 0
        assert summary["positive_messages"] > 0


class TestIndexes:
    """Tests for index creation"""

    def test_conversation_context_indexes(self, duckdb_conn):
        """Test that indexes are created for conversation_context"""
        indexes = duckdb_conn.execute(
            "SELECT index_name FROM duckdb_indexes() WHERE table_name = 'conversation_context'"
        ).fetchall()

        index_names = [idx[0] for idx in indexes]
        assert "idx_context_session" in index_names
        assert "idx_context_phone" in index_names

    def test_message_history_indexes(self, duckdb_conn):
        """Test that indexes are created for message_history"""
        indexes = duckdb_conn.execute(
            "SELECT index_name FROM duckdb_indexes() WHERE table_name = 'message_history'"
        ).fetchall()

        index_names = [idx[0] for idx in indexes]
        assert "idx_history_session" in index_names
        assert "idx_history_phone_created" in index_names
        assert "idx_history_intent" in index_names
