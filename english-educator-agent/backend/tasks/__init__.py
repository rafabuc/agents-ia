"""
Celery tasks configuration and task definitions.
"""
from celery import Celery
from celery.schedules import crontab
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "english_tutor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    "daily-practice-reminder": {
        "task": "tasks.daily_practice.send_practice_reminder",
        "schedule": crontab(hour=9, minute=0),  # 9 AM daily
        "args": (),
    },
    "weekly-progress-report": {
        "task": "tasks.progress_report.generate_weekly_report",
        "schedule": crontab(day_of_week=1, hour=8, minute=0),  # Monday 8 AM
        "args": (),
    },
    "update-user-levels": {
        "task": "tasks.progress_report.update_student_levels",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
        "args": (),
    },
    "cleanup-old-sessions": {
        "task": "tasks.maintenance.cleanup_old_sessions",
        "schedule": crontab(hour=3, minute=0),  # 3 AM daily
        "args": (),
    }
}

logger.info("Celery app configured successfully")
