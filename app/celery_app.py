# ============================================
# CELERY APPLICATION SETUP
# ============================================

from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "library_management",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.tasks"]
)


# Celery Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# ============================================
# CELERY BEAT SCHEDULE (CRON JOBS)
# ============================================

celery_app.conf.beat_schedule = {
    # Task 1: Daily reminder at 9 AM
    'send-daily-reminders': {
        'task': 'app.tasks.send_daily_reminders',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9:00 AM
    },
    
    # Task 2: Weekly statistics every Monday at 8 AM
    'weekly-statistics': {
        'task': 'app.tasks.generate_weekly_statistics',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Monday 8 AM
    },
    
    # Task 3: Monthly cleanup on 1st of month at midnight
    'monthly-cleanup': {
        'task': 'app.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),  # 1st day, midnight
    },
    
    # Task 4: Daily database backup at 2 AM
    'daily-backup': {
        'task': 'app.tasks.backup_database',
        'schedule': crontab(hour=2, minute=0),  # Every day at 2:00 AM
    },
    
    # Task 5: Every 5 minutes - check system health
    'health-check': {
        'task': 'app.tasks.system_health_check',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}

# Task routing
celery_app.conf.task_routes = {
    'app.tasks.send_*': {'queue': 'emails'},
    'app.tasks.generate_*': {'queue': 'reports'},
    'app.tasks.cleanup_*': {'queue': 'maintenance'},
}