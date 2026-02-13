from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import load_app_config
from app.tasks.update_indices import create_and_run_refresh

_scheduler: BackgroundScheduler | None = None


def start_scheduler():
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    config = load_app_config()
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(
        create_and_run_refresh,
        trigger="cron",
        day_of_week=config.scheduler_day_of_week,
        hour=config.scheduler_hour,
        minute=config.scheduler_minute,
        id="weekly_refresh_job",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler
    return _scheduler


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None

