"""
Tests for State Manager.

Tests SQLite schema, vehicle hash management, checkpoint system,
and scraping run history.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from scraper.state_manager import StateManager
from scraper.models import Checkpoint, ScrapingResult


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def state_manager(temp_db):
    """Create StateManager instance with temporary database"""
    return StateManager(db_path=temp_db)


class TestStateManagerInitialization:
    """Test State Manager initialization and schema creation"""
    
    def test_creates_database_file(self, temp_db):
        """Test that database file is created"""
        manager = StateManager(db_path=temp_db)
        assert Path(temp_db).exists()
    
    def test_creates_tables(self, state_manager):
        """Test that all required tables are created"""
        with state_manager._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check vehicles table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='vehicles'
            """)
            assert cursor.fetchone() is not None
            
            # Check checkpoints table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='checkpoints'
            """)
            assert cursor.fetchone() is not None
            
            # Check scraping_runs table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='scraping_runs'
            """)
            assert cursor.fetchone() is not None
    
    def test_creates_indexes(self, state_manager):
        """Test that indexes are created for performance"""
        with state_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index'
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            
            # Check key indexes exist
            assert 'idx_vehicles_hash' in indexes
            assert 'idx_vehicles_status' in indexes
            assert 'idx_checkpoints_timestamp' in indexes
            assert 'idx_runs_start_time' in indexes


class TestVehicleHashManagement:
    """Test vehicle hash storage and change detection"""
    
    def test_save_new_vehicle_hash(self, state_manager):
        """Test saving hash for new vehicle"""
        vehicle_id = "test_vehicle_1"
        content_hash = "abc123def456"
        
        state_manager.save_vehicle_hash(vehicle_id, content_hash)
        
        stored_hash = state_manager.get_vehicle_hash(vehicle_id)
        assert stored_hash == content_hash
    
    def test_update_existing_vehicle_hash(self, state_manager):
        """Test updating hash for existing vehicle"""
        vehicle_id = "test_vehicle_1"
        old_hash = "old_hash_123"
        new_hash = "new_hash_456"
        
        # Save initial hash
        state_manager.save_vehicle_hash(vehicle_id, old_hash)
        assert state_manager.get_vehicle_hash(vehicle_id) == old_hash
        
        # Update hash
        state_manager.save_vehicle_hash(vehicle_id, new_hash)
        assert state_manager.get_vehicle_hash(vehicle_id) == new_hash
    
    def test_get_nonexistent_vehicle_hash(self, state_manager):
        """Test getting hash for vehicle that doesn't exist"""
        result = state_manager.get_vehicle_hash("nonexistent_vehicle")
        assert result is None
    
    def test_has_changed_new_vehicle(self, state_manager):
        """Test change detection for new vehicle"""
        vehicle_id = "new_vehicle"
        content_hash = "hash123"
        
        # New vehicle should be detected as changed
        assert state_manager.has_changed(vehicle_id, content_hash) is True
    
    def test_has_changed_unchanged_vehicle(self, state_manager):
        """Test change detection for unchanged vehicle"""
        vehicle_id = "test_vehicle"
        content_hash = "hash123"
        
        # Save hash
        state_manager.save_vehicle_hash(vehicle_id, content_hash)
        
        # Same hash should not be detected as changed
        assert state_manager.has_changed(vehicle_id, content_hash) is False
    
    def test_has_changed_modified_vehicle(self, state_manager):
        """Test change detection for modified vehicle"""
        vehicle_id = "test_vehicle"
        old_hash = "old_hash"
        new_hash = "new_hash"
        
        # Save old hash
        state_manager.save_vehicle_hash(vehicle_id, old_hash)
        
        # Different hash should be detected as changed
        assert state_manager.has_changed(vehicle_id, new_hash) is True
    
    def test_save_vehicle_with_metadata(self, state_manager):
        """Test saving vehicle hash with metadata"""
        vehicle_id = "test_vehicle"
        content_hash = "hash123"
        metadata = {"source": "robustcar", "page": 1}
        
        state_manager.save_vehicle_hash(vehicle_id, content_hash, metadata)
        
        # Verify hash was saved
        assert state_manager.get_vehicle_hash(vehicle_id) == content_hash
    
    def test_mark_vehicle_unavailable(self, state_manager):
        """Test marking vehicle as unavailable"""
        vehicle_id = "test_vehicle"
        content_hash = "hash123"
        
        # Save vehicle
        state_manager.save_vehicle_hash(vehicle_id, content_hash)
        
        # Mark as unavailable
        state_manager.mark_vehicle_unavailable(vehicle_id)
        
        # Verify status changed
        with state_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM vehicles WHERE id = ?", (vehicle_id,))
            status = cursor.fetchone()['status']
            assert status == 'unavailable'
    
    def test_get_active_vehicle_ids(self, state_manager):
        """Test getting list of active vehicles"""
        # Save multiple vehicles
        state_manager.save_vehicle_hash("vehicle_1", "hash1")
        state_manager.save_vehicle_hash("vehicle_2", "hash2")
        state_manager.save_vehicle_hash("vehicle_3", "hash3")
        
        # Mark one as unavailable
        state_manager.mark_vehicle_unavailable("vehicle_2")
        
        # Get active vehicles
        active_ids = state_manager.get_active_vehicle_ids()
        
        assert len(active_ids) == 2
        assert "vehicle_1" in active_ids
        assert "vehicle_3" in active_ids
        assert "vehicle_2" not in active_ids


class TestCheckpointManagement:
    """Test checkpoint save/load functionality"""
    
    def test_save_checkpoint(self, state_manager):
        """Test saving checkpoint"""
        checkpoint = Checkpoint(
            id="checkpoint_1",
            timestamp=datetime.now(),
            processed_count=50,
            success_count=48,
            error_count=2,
            last_vehicle_id="vehicle_50",
            metadata={"page": 5}
        )
        
        state_manager.save_checkpoint(checkpoint)
        
        # Verify checkpoint was saved
        loaded = state_manager.load_checkpoint("checkpoint_1")
        assert loaded is not None
        assert loaded.id == checkpoint.id
        assert loaded.processed_count == 50
        assert loaded.success_count == 48
        assert loaded.error_count == 2
        assert loaded.last_vehicle_id == "vehicle_50"
    
    def test_load_nonexistent_checkpoint(self, state_manager):
        """Test loading checkpoint that doesn't exist"""
        result = state_manager.load_checkpoint("nonexistent")
        assert result is None
    
    def test_get_latest_checkpoint(self, state_manager):
        """Test getting most recent checkpoint"""
        # Save multiple checkpoints
        checkpoint1 = Checkpoint(
            id="checkpoint_1",
            timestamp=datetime(2025, 10, 30, 10, 0, 0),
            processed_count=50
        )
        checkpoint2 = Checkpoint(
            id="checkpoint_2",
            timestamp=datetime(2025, 10, 30, 11, 0, 0),
            processed_count=100
        )
        checkpoint3 = Checkpoint(
            id="checkpoint_3",
            timestamp=datetime(2025, 10, 30, 12, 0, 0),
            processed_count=150
        )
        
        state_manager.save_checkpoint(checkpoint1)
        state_manager.save_checkpoint(checkpoint2)
        state_manager.save_checkpoint(checkpoint3)
        
        # Get latest
        latest = state_manager.get_latest_checkpoint()
        assert latest is not None
        assert latest.id == "checkpoint_3"
        assert latest.processed_count == 150
    
    def test_get_latest_checkpoint_empty(self, state_manager):
        """Test getting latest checkpoint when none exist"""
        result = state_manager.get_latest_checkpoint()
        assert result is None
    
    def test_delete_old_checkpoints(self, state_manager):
        """Test deleting old checkpoints"""
        # Save 15 checkpoints
        for i in range(15):
            checkpoint = Checkpoint(
                id=f"checkpoint_{i}",
                timestamp=datetime(2025, 10, 30, 10 + i, 0, 0),
                processed_count=i * 10
            )
            state_manager.save_checkpoint(checkpoint)
        
        # Delete old ones, keep 5
        state_manager.delete_old_checkpoints(keep_count=5)
        
        # Verify only 5 remain
        with state_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM checkpoints")
            count = cursor.fetchone()['count']
            assert count == 5
        
        # Verify the most recent ones were kept
        latest = state_manager.get_latest_checkpoint()
        assert latest.id == "checkpoint_14"


class TestScrapingRunHistory:
    """Test scraping run storage and retrieval"""
    
    def test_save_scraping_run(self, state_manager):
        """Test saving scraping run result"""
        result = ScrapingResult(
            id="run_1",
            start_time=datetime(2025, 10, 30, 10, 0, 0),
            end_time=datetime(2025, 10, 30, 10, 30, 0),
            mode="full",
            total_processed=100,
            total_success=95,
            total_errors=5,
            total_skipped=0,
            metrics={"avg_time": 1.5}
        )
        
        state_manager.save_scraping_run(result)
        
        # Verify run was saved
        loaded = state_manager.get_scraping_run("run_1")
        assert loaded is not None
        assert loaded['id'] == "run_1"
        assert loaded['mode'] == "full"
        assert loaded['total_processed'] == 100
        assert loaded['total_success'] == 95
    
    def test_get_nonexistent_run(self, state_manager):
        """Test getting run that doesn't exist"""
        result = state_manager.get_scraping_run("nonexistent")
        assert result is None
    
    def test_get_recent_runs(self, state_manager):
        """Test getting recent runs"""
        # Save multiple runs
        for i in range(5):
            result = ScrapingResult(
                id=f"run_{i}",
                start_time=datetime(2025, 10, 30, 10 + i, 0, 0),
                mode="incremental" if i % 2 == 0 else "full",
                total_processed=100 + i * 10
            )
            state_manager.save_scraping_run(result)
        
        # Get recent runs
        recent = state_manager.get_recent_runs(limit=3)
        
        assert len(recent) == 3
        # Should be in reverse chronological order
        assert recent[0]['id'] == "run_4"
        assert recent[1]['id'] == "run_3"
        assert recent[2]['id'] == "run_2"


class TestStatistics:
    """Test statistics and reporting"""
    
    def test_get_statistics_empty(self, state_manager):
        """Test statistics with empty database"""
        stats = state_manager.get_statistics()
        
        assert stats['total_vehicles'] == 0
        assert stats['active_vehicles'] == 0
        assert stats['unavailable_vehicles'] == 0
        assert stats['total_checkpoints'] == 0
        assert stats['total_runs'] == 0
        assert stats['latest_run'] is None
    
    def test_get_statistics_with_data(self, state_manager):
        """Test statistics with data"""
        # Add vehicles
        state_manager.save_vehicle_hash("vehicle_1", "hash1")
        state_manager.save_vehicle_hash("vehicle_2", "hash2")
        state_manager.save_vehicle_hash("vehicle_3", "hash3")
        state_manager.mark_vehicle_unavailable("vehicle_3")
        
        # Add checkpoint
        checkpoint = Checkpoint(id="cp_1", processed_count=50)
        state_manager.save_checkpoint(checkpoint)
        
        # Add run
        result = ScrapingResult(
            id="run_1",
            start_time=datetime(2025, 10, 30, 10, 0, 0),
            mode="full",
            total_processed=100
        )
        state_manager.save_scraping_run(result)
        
        # Get statistics
        stats = state_manager.get_statistics()
        
        assert stats['total_vehicles'] == 3
        assert stats['active_vehicles'] == 2
        assert stats['unavailable_vehicles'] == 1
        assert stats['total_checkpoints'] == 1
        assert stats['total_runs'] == 1
        assert stats['latest_run'] is not None
        assert stats['latest_run']['mode'] == "full"


class TestDataCleanup:
    """Test data cleanup functionality"""
    
    def test_clear_all_data(self, state_manager):
        """Test clearing all data from database"""
        # Add some data
        state_manager.save_vehicle_hash("vehicle_1", "hash1")
        checkpoint = Checkpoint(id="cp_1", processed_count=50)
        state_manager.save_checkpoint(checkpoint)
        result = ScrapingResult(
            id="run_1",
            start_time=datetime.now(),
            mode="full",
            total_processed=100
        )
        state_manager.save_scraping_run(result)
        
        # Clear all data
        state_manager.clear_all_data()
        
        # Verify everything is empty
        stats = state_manager.get_statistics()
        assert stats['total_vehicles'] == 0
        assert stats['total_checkpoints'] == 0
        assert stats['total_runs'] == 0
