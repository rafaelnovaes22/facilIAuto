"""Script to start Celery worker."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.celery_config import celery_app

if __name__ == "__main__":
    # Start Celery worker with configuration
    celery_app.worker_main(
        argv=[
            "worker",
            "--loglevel=info",
            "--concurrency=4",
            "--max-tasks-per-child=1000",
            "--queues=default,high_priority,low_priority",
            "--hostname=worker@%h",
        ]
    )
