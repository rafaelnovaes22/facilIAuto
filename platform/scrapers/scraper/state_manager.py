"""
State Manager for RobustCar scraper using SQLite.

This module manages scraping state, vehicle hashes, and checkpoints
for incremental scraping and resumable execution.

Requirements: 5.1, 5.2, 5.3, 5.4, 6.5
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from contextlib import contextmanager

from .models import Checkpoint, ScrapingResult


class StateManager:
    """
    Manages scraping state using SQLite database.
    
    Handles:
    - Vehicle hash storage for change detection
    - Checkpoint management for resumable scraping
    - Scraping run history and metrics
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 6.5
    """
    
    def __init__(self, db_path: str = "state.db"):
        """
        Initialize State Manager with SQLite database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """
        Initialize database schema with tables and indexes.
        
        Creates:
        - vehicles table: stores vehicle hashes and status
        - checkpoints table: stores scraping checkpoints
        - scraping_runs table: stores execution history
        
        Requirement: 5.1, 5.2, 5.3, 6.5
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create vehicles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vehicles (
                    id TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    last_modified TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'active',
                    metadata TEXT
                )
            """)
            
            # Create indexes for vehicles table
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vehicles_hash 
                ON vehicles(content_hash)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vehicles_status 
                ON vehicles(status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vehicles_last_seen 
                ON vehicles(last_seen)
            """)
            
            # Create checkpoints table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    processed_count INTEGER NOT NULL DEFAULT 0,
                    success_count INTEGER NOT NULL DEFAULT 0,
                    error_count INTEGER NOT NULL DEFAULT 0,
                    last_vehicle_id TEXT,
                    metadata TEXT
                )
            """)
            
            # Create index for checkpoints
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_checkpoints_timestamp 
                ON checkpoints(timestamp DESC)
            """)
            
            # Create scraping_runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraping_runs (
                    id TEXT PRIMARY KEY,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    mode TEXT NOT NULL,
                    total_processed INTEGER DEFAULT 0,
                    total_success INTEGER DEFAULT 0,
                    total_errors INTEGER DEFAULT 0,
                    total_skipped INTEGER DEFAULT 0,
                    metrics TEXT
                )
            """)
            
            # Create indexes for scraping_runs
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_start_time 
                ON scraping_runs(start_time DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_mode 
                ON scraping_runs(mode)
            """)
    
    def save_vehicle_hash(
        self,
        vehicle_id: str,
        content_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Save or update vehicle hash for change detection.
        
        Args:
            vehicle_id: Unique vehicle identifier
            content_hash: MD5 hash of vehicle content
            metadata: Optional metadata dictionary
            
        Requirement: 5.1, 5.2
        """
        now = datetime.now()
        metadata_json = json.dumps(metadata) if metadata else None
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if vehicle exists
            cursor.execute(
                "SELECT content_hash FROM vehicles WHERE id = ?",
                (vehicle_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing vehicle
                cursor.execute("""
                    UPDATE vehicles 
                    SET content_hash = ?,
                        last_seen = ?,
                        last_modified = ?,
                        status = 'active',
                        metadata = ?
                    WHERE id = ?
                """, (content_hash, now, now, metadata_json, vehicle_id))
            else:
                # Insert new vehicle
                cursor.execute("""
                    INSERT INTO vehicles 
                    (id, content_hash, last_seen, last_modified, status, metadata)
                    VALUES (?, ?, ?, ?, 'active', ?)
                """, (vehicle_id, content_hash, now, now, metadata_json))
    
    def get_vehicle_hash(self, vehicle_id: str) -> Optional[str]:
        """
        Get stored hash for a vehicle.
        
        Args:
            vehicle_id: Unique vehicle identifier
            
        Returns:
            Content hash if found, None otherwise
            
        Requirement: 5.2
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT content_hash FROM vehicles WHERE id = ?",
                (vehicle_id,)
            )
            result = cursor.fetchone()
            return result['content_hash'] if result else None
    
    def has_changed(self, vehicle_id: str, content_hash: str) -> bool:
        """
        Check if vehicle content has changed.
        
        Args:
            vehicle_id: Unique vehicle identifier
            content_hash: Current content hash
            
        Returns:
            True if vehicle is new or changed, False if unchanged
            
        Requirement: 5.2, 5.3
        """
        stored_hash = self.get_vehicle_hash(vehicle_id)
        
        # New vehicle or changed content
        if stored_hash is None or stored_hash != content_hash:
            return True
        
        return False
    
    def mark_vehicle_unavailable(self, vehicle_id: str):
        """
        Mark vehicle as unavailable (no longer on site).
        
        Args:
            vehicle_id: Unique vehicle identifier
            
        Requirement: 5.4
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE vehicles 
                SET status = 'unavailable'
                WHERE id = ?
            """, (vehicle_id,))
    
    def get_active_vehicle_ids(self) -> List[str]:
        """
        Get list of all active vehicle IDs.
        
        Returns:
            List of vehicle IDs with status 'active'
            
        Requirement: 5.4
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM vehicles 
                WHERE status = 'active'
                ORDER BY last_seen DESC
            """)
            return [row['id'] for row in cursor.fetchall()]
    
    def save_checkpoint(self, checkpoint: Checkpoint):
        """
        Save scraping checkpoint for resumable execution.
        
        Args:
            checkpoint: Checkpoint object to save
            
        Requirement: 6.5
        """
        checkpoint_dict = checkpoint.to_dict()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO checkpoints
                (id, timestamp, processed_count, success_count, error_count,
                 last_vehicle_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                checkpoint_dict['id'],
                checkpoint_dict['timestamp'],
                checkpoint_dict['processed_count'],
                checkpoint_dict['success_count'],
                checkpoint_dict['error_count'],
                checkpoint_dict.get('last_vehicle_id'),
                json.dumps(checkpoint_dict.get('metadata', {}))
            ))
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Load checkpoint by ID.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Checkpoint object if found, None otherwise
            
        Requirement: 6.5
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM checkpoints WHERE id = ?
            """, (checkpoint_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return Checkpoint(
                id=row['id'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                processed_count=row['processed_count'],
                success_count=row['success_count'],
                error_count=row['error_count'],
                last_vehicle_id=row['last_vehicle_id'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
    
    def get_latest_checkpoint(self) -> Optional[Checkpoint]:
        """
        Get the most recent checkpoint.
        
        Returns:
            Latest Checkpoint object if any exist, None otherwise
            
        Requirement: 6.5
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM checkpoints 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return Checkpoint(
                id=row['id'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                processed_count=row['processed_count'],
                success_count=row['success_count'],
                error_count=row['error_count'],
                last_vehicle_id=row['last_vehicle_id'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
    
    def delete_old_checkpoints(self, keep_count: int = 10):
        """
        Delete old checkpoints, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent checkpoints to keep
            
        Requirement: 6.5
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM checkpoints 
                WHERE id NOT IN (
                    SELECT id FROM checkpoints 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                )
            """, (keep_count,))
    
    def save_scraping_run(self, result: ScrapingResult):
        """
        Save scraping run result to history.
        
        Args:
            result: ScrapingResult object
            
        Requirement: 7.4
        """
        result_dict = result.to_dict()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO scraping_runs
                (id, start_time, end_time, mode, total_processed,
                 total_success, total_errors, total_skipped, metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result_dict['id'],
                result_dict['start_time'],
                result_dict.get('end_time'),
                result_dict['mode'],
                result_dict['total_processed'],
                result_dict['total_success'],
                result_dict['total_errors'],
                result_dict['total_skipped'],
                json.dumps(result_dict.get('metrics', {}))
            ))
    
    def get_scraping_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get scraping run by ID.
        
        Args:
            run_id: Scraping run identifier
            
        Returns:
            Dictionary with run data if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scraping_runs WHERE id = ?
            """, (run_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                'id': row['id'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'mode': row['mode'],
                'total_processed': row['total_processed'],
                'total_success': row['total_success'],
                'total_errors': row['total_errors'],
                'total_skipped': row['total_skipped'],
                'metrics': json.loads(row['metrics']) if row['metrics'] else {}
            }
    
    def get_recent_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent scraping runs.
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of run dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scraping_runs 
                ORDER BY start_time DESC 
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    'id': row['id'],
                    'start_time': row['start_time'],
                    'end_time': row['end_time'],
                    'mode': row['mode'],
                    'total_processed': row['total_processed'],
                    'total_success': row['total_success'],
                    'total_errors': row['total_errors'],
                    'total_skipped': row['total_skipped'],
                    'metrics': json.loads(row['metrics']) if row['metrics'] else {}
                }
                for row in cursor.fetchall()
            ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics about stored data
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Count vehicles by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM vehicles 
                GROUP BY status
            """)
            vehicle_counts = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Count total checkpoints
            cursor.execute("SELECT COUNT(*) as count FROM checkpoints")
            checkpoint_count = cursor.fetchone()['count']
            
            # Count total runs
            cursor.execute("SELECT COUNT(*) as count FROM scraping_runs")
            run_count = cursor.fetchone()['count']
            
            # Get latest run
            cursor.execute("""
                SELECT start_time, mode 
                FROM scraping_runs 
                ORDER BY start_time DESC 
                LIMIT 1
            """)
            latest_run = cursor.fetchone()
            
            return {
                'total_vehicles': sum(vehicle_counts.values()),
                'active_vehicles': vehicle_counts.get('active', 0),
                'unavailable_vehicles': vehicle_counts.get('unavailable', 0),
                'total_checkpoints': checkpoint_count,
                'total_runs': run_count,
                'latest_run': {
                    'start_time': latest_run['start_time'],
                    'mode': latest_run['mode']
                } if latest_run else None
            }
    
    def clear_all_data(self):
        """
        Clear all data from database (for testing/reset).
        
        WARNING: This deletes all vehicles, checkpoints, and runs.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vehicles")
            cursor.execute("DELETE FROM checkpoints")
            cursor.execute("DELETE FROM scraping_runs")
