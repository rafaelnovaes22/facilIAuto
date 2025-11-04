"""
Simple validation script for State Manager.
Tests core functionality without pytest.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add scraper to path
sys.path.insert(0, str(Path(__file__).parent))

from scraper.state_manager import StateManager
from scraper.models import Checkpoint, ScrapingResult


def test_basic_functionality():
    """Test basic State Manager functionality"""
    print("Testing State Manager...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Initialize State Manager
        manager = StateManager(db_path=db_path)
        print("✓ State Manager initialized")
        
        # Test 1: Save and retrieve vehicle hash
        vehicle_id = "test_vehicle_1"
        content_hash = "abc123def456"
        manager.save_vehicle_hash(vehicle_id, content_hash)
        retrieved_hash = manager.get_vehicle_hash(vehicle_id)
        assert retrieved_hash == content_hash, "Hash mismatch"
        print("✓ Vehicle hash save/load works")
        
        # Test 2: Change detection - new vehicle
        assert manager.has_changed("new_vehicle", "hash123") is True
        print("✓ Change detection for new vehicle works")
        
        # Test 3: Change detection - unchanged vehicle
        assert manager.has_changed(vehicle_id, content_hash) is False
        print("✓ Change detection for unchanged vehicle works")
        
        # Test 4: Change detection - modified vehicle
        assert manager.has_changed(vehicle_id, "new_hash") is True
        print("✓ Change detection for modified vehicle works")
        
        # Test 5: Mark vehicle unavailable
        manager.mark_vehicle_unavailable(vehicle_id)
        print("✓ Mark vehicle unavailable works")
        
        # Test 6: Get active vehicles
        manager.save_vehicle_hash("vehicle_2", "hash2")
        manager.save_vehicle_hash("vehicle_3", "hash3")
        active_ids = manager.get_active_vehicle_ids()
        assert len(active_ids) == 2
        assert "vehicle_2" in active_ids
        assert "vehicle_3" in active_ids
        print("✓ Get active vehicles works")
        
        # Test 7: Save and load checkpoint
        checkpoint = Checkpoint(
            id="checkpoint_1",
            timestamp=datetime.now(),
            processed_count=50,
            success_count=48,
            error_count=2,
            last_vehicle_id="vehicle_50"
        )
        manager.save_checkpoint(checkpoint)
        loaded_checkpoint = manager.load_checkpoint("checkpoint_1")
        assert loaded_checkpoint is not None
        assert loaded_checkpoint.processed_count == 50
        print("✓ Checkpoint save/load works")
        
        # Test 8: Get latest checkpoint
        checkpoint2 = Checkpoint(
            id="checkpoint_2",
            timestamp=datetime.now(),
            processed_count=100
        )
        manager.save_checkpoint(checkpoint2)
        latest = manager.get_latest_checkpoint()
        assert latest.id == "checkpoint_2"
        print("✓ Get latest checkpoint works")
        
        # Test 9: Save scraping run
        result = ScrapingResult(
            id="run_1",
            start_time=datetime.now(),
            mode="full",
            total_processed=100,
            total_success=95,
            total_errors=5
        )
        manager.save_scraping_run(result)
        loaded_run = manager.get_scraping_run("run_1")
        assert loaded_run is not None
        assert loaded_run['total_processed'] == 100
        print("✓ Scraping run save/load works")
        
        # Test 10: Get statistics
        stats = manager.get_statistics()
        assert stats['total_vehicles'] > 0
        assert stats['active_vehicles'] == 2
        assert stats['unavailable_vehicles'] == 1
        assert stats['total_checkpoints'] == 2
        assert stats['total_runs'] == 1
        print("✓ Statistics works")
        
        # Test 11: Clear all data
        manager.clear_all_data()
        stats_after = manager.get_statistics()
        assert stats_after['total_vehicles'] == 0
        print("✓ Clear all data works")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        Path(db_path).unlink(missing_ok=True)


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
