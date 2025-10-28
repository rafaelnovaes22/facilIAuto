"""Unit tests for idempotency utilities."""

import time
from unittest.mock import MagicMock, patch

import pytest

from src.utils.idempotency import (
    DebounceManager,
    DeduplicationManager,
    IdempotencyManager,
    debounce_task,
    deduplicate_job,
)


class TestIdempotencyManager:
    """Tests for IdempotencyManager."""

    @pytest.fixture
    def redis_mock(self):
        """Create a mock Redis client."""
        mock = MagicMock()
        mock.exists.return_value = 0
        mock.get.return_value = None
        mock.set.return_value = True
        mock.delete.return_value = True
        return mock

    @pytest.fixture
    def manager(self, redis_mock):
        """Create IdempotencyManager with mock Redis."""
        return IdempotencyManager(redis_client=redis_mock)

    def test_generate_idempotency_key(self, manager):
        """Test idempotency key generation."""
        key = manager.generate_idempotency_key(
            session_id="session123",
            turn_id=5,
            task_name="test_task",
        )
        assert key == "idempotency:test_task:session123:5"

    def test_generate_idempotency_key_without_task_name(self, manager):
        """Test idempotency key generation without task name."""
        key = manager.generate_idempotency_key(
            session_id="session123",
            turn_id=5,
        )
        assert key == "idempotency:session123:5"

    def test_is_processed_false(self, manager, redis_mock):
        """Test is_processed returns False when key doesn't exist."""
        redis_mock.exists.return_value = 0
        assert manager.is_processed("test_key") is False

    def test_is_processed_true(self, manager, redis_mock):
        """Test is_processed returns True when key exists."""
        redis_mock.exists.return_value = 1
        assert manager.is_processed("test_key") is True

    def test_mark_processed_success(self, manager, redis_mock):
        """Test marking task as processed."""
        redis_mock.set.return_value = True
        result = manager.mark_processed("test_key", {"status": "success"}, ttl=3600)
        assert result is True
        redis_mock.set.assert_called_once()

    def test_mark_processed_already_exists(self, manager, redis_mock):
        """Test marking task that's already processed."""
        redis_mock.set.return_value = False
        result = manager.mark_processed("test_key", {"status": "success"}, ttl=3600)
        assert result is False

    def test_get_result_json(self, manager, redis_mock):
        """Test getting result as JSON."""
        redis_mock.get.return_value = '{"status": "success"}'
        result = manager.get_result("test_key")
        assert result == {"status": "success"}

    def test_get_result_not_found(self, manager, redis_mock):
        """Test getting result when key doesn't exist."""
        redis_mock.get.return_value = None
        result = manager.get_result("test_key")
        assert result is None


class TestDebounceManager:
    """Tests for DebounceManager."""

    @pytest.fixture
    def redis_mock(self):
        """Create a mock Redis client."""
        mock = MagicMock()
        mock.set.return_value = True
        mock.rpush.return_value = 1
        mock.llen.return_value = 1
        mock.ttl.return_value = -1
        mock.expire.return_value = True
        mock.lrange.return_value = []
        mock.delete.return_value = True
        return mock

    @pytest.fixture
    def manager(self, redis_mock):
        """Create DebounceManager with mock Redis."""
        return DebounceManager(redis_client=redis_mock)

    def test_generate_debounce_key(self, manager):
        """Test debounce key generation."""
        key = manager.generate_debounce_key(
            user_id="user123",
            event_type="message",
        )
        assert key == "debounce:message:user123"

    def test_should_process_true(self, manager, redis_mock):
        """Test should_process returns True when not debounced."""
        redis_mock.set.return_value = True
        assert manager.should_process("test_key", window_seconds=5) is True

    def test_should_process_false(self, manager, redis_mock):
        """Test should_process returns False when debounced."""
        redis_mock.set.return_value = False
        assert manager.should_process("test_key", window_seconds=5) is False

    def test_accumulate_event(self, manager, redis_mock):
        """Test accumulating events."""
        redis_mock.llen.return_value = 3
        count = manager.accumulate_event(
            "accumulator_key",
            {"message": "test"},
            ttl=10,
        )
        assert count == 3
        redis_mock.rpush.assert_called_once()

    def test_get_accumulated_events(self, manager, redis_mock):
        """Test getting accumulated events."""
        redis_mock.lrange.return_value = ['{"message": "test1"}', '{"message": "test2"}']
        events = manager.get_accumulated_events("accumulator_key", clear=True)
        assert len(events) == 2
        assert events[0]["message"] == "test1"
        assert events[1]["message"] == "test2"
        redis_mock.delete.assert_called_once()

    def test_get_accumulated_events_no_clear(self, manager, redis_mock):
        """Test getting accumulated events without clearing."""
        redis_mock.lrange.return_value = ['{"message": "test"}']
        events = manager.get_accumulated_events("accumulator_key", clear=False)
        assert len(events) == 1
        redis_mock.delete.assert_not_called()


class TestDeduplicationManager:
    """Tests for DeduplicationManager."""

    @pytest.fixture
    def redis_mock(self):
        """Create a mock Redis client."""
        mock = MagicMock()
        mock.exists.return_value = 0
        mock.set.return_value = True
        return mock

    @pytest.fixture
    def manager(self, redis_mock):
        """Create DeduplicationManager with mock Redis."""
        return DeduplicationManager(redis_client=redis_mock)

    def test_generate_job_hash(self, manager):
        """Test job hash generation."""
        hash1 = manager.generate_job_hash(
            "test_task",
            ("arg1",),
            {"key": "value"},
        )
        hash2 = manager.generate_job_hash(
            "test_task",
            ("arg1",),
            {"key": "value"},
        )
        # Same inputs should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex digest

    def test_generate_job_hash_different_inputs(self, manager):
        """Test job hash with different inputs."""
        hash1 = manager.generate_job_hash(
            "test_task",
            ("arg1",),
            {"key": "value1"},
        )
        hash2 = manager.generate_job_hash(
            "test_task",
            ("arg1",),
            {"key": "value2"},
        )
        # Different inputs should produce different hashes
        assert hash1 != hash2

    def test_is_duplicate_false(self, manager, redis_mock):
        """Test is_duplicate returns False when not duplicate."""
        redis_mock.exists.return_value = 0
        assert manager.is_duplicate("test_hash", window_seconds=60) is False

    def test_is_duplicate_true(self, manager, redis_mock):
        """Test is_duplicate returns True when duplicate."""
        redis_mock.exists.return_value = 1
        assert manager.is_duplicate("test_hash", window_seconds=60) is True

    def test_mark_job_success(self, manager, redis_mock):
        """Test marking job successfully."""
        redis_mock.set.return_value = True
        result = manager.mark_job("test_hash", window_seconds=60)
        assert result is True

    def test_mark_job_already_exists(self, manager, redis_mock):
        """Test marking job that already exists."""
        redis_mock.set.return_value = False
        result = manager.mark_job("test_hash", window_seconds=60)
        assert result is False


class TestDebounceDecorator:
    """Tests for debounce_task decorator."""

    def test_debounce_task_decorator(self):
        """Test debounce_task decorator."""
        call_count = 0

        @debounce_task(window_seconds=5)
        def test_func(user_id=None):
            nonlocal call_count
            call_count += 1
            return {"status": "success"}

        with patch("src.utils.idempotency.DebounceManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.should_process.return_value = True

            # First call should execute
            result = test_func(user_id="user123")
            assert result["status"] == "success"
            assert call_count == 1

    def test_debounce_task_decorator_debounced(self):
        """Test debounce_task decorator when debounced."""

        @debounce_task(window_seconds=5)
        def test_func(user_id=None):
            return {"status": "success"}

        with patch("src.utils.idempotency.DebounceManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.should_process.return_value = False

            # Call should be debounced
            result = test_func(user_id="user123")
            assert result["status"] == "debounced"


class TestDeduplicateDecorator:
    """Tests for deduplicate_job decorator."""

    def test_deduplicate_job_decorator(self):
        """Test deduplicate_job decorator."""
        call_count = 0

        @deduplicate_job(window_seconds=60)
        def test_func(arg1, key1=None):
            nonlocal call_count
            call_count += 1
            return {"status": "success"}

        with patch("src.utils.idempotency.DeduplicationManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.is_duplicate.return_value = False
            mock_manager.mark_job.return_value = True

            # First call should execute
            result = test_func("arg1", key1="value1")
            assert result["status"] == "success"
            assert call_count == 1

    def test_deduplicate_job_decorator_duplicate(self):
        """Test deduplicate_job decorator when duplicate."""

        @deduplicate_job(window_seconds=60)
        def test_func(arg1, key1=None):
            return {"status": "success"}

        with patch("src.utils.idempotency.DeduplicationManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.is_duplicate.return_value = True

            # Call should be deduplicated
            result = test_func("arg1", key1="value1")
            assert result["status"] == "duplicate"
