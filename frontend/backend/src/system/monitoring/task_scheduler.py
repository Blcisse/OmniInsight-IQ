from __future__ import annotations

import os
from celery import Celery
from celery.schedules import crontab
import logging


def get_celery_app() -> Celery:
    """Create and return a Celery app configured with Redis.

    Broker URL priority: CELERY_BROKER_URL > REDIS_URL > redis://localhost:6379/0
    Result backend uses the same Redis by default.
    """
    broker = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
    backend = os.getenv("CELERY_RESULT_BACKEND") or broker
    app = Celery("system_monitor", broker=broker, backend=backend)
    # Load any task modules declared via env if needed
    include = os.getenv("CELERY_INCLUDE", "").split(",") if os.getenv("CELERY_INCLUDE") else []
    if include:
        app.conf.update(include=include)
    # Reasonable defaults
    app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"]) 
    return app


# Optional: example periodic task registration (can be enabled externally)
celery_app = get_celery_app()


@celery_app.task(name="system_monitor.train_model_task")
def train_model_task(model_name: str) -> str:
    # Placeholder for real training invocation
    logging.getLogger("task_scheduler").info("Triggered training for model '%s'", model_name)
    return f"scheduled training for {model_name}"


@celery_app.task(name="system_monitor.update_forecast_task")
def update_forecast_task() -> str:
    logging.getLogger("task_scheduler").info("Triggered scheduled forecast update")
    return "scheduled forecast update"


def schedule_model_training(task_id: str, model_name: str, interval: str = "@hourly") -> None:
    """Register a periodic task to train a model at the given interval.

    interval accepts cron-like aliases (e.g., '@hourly', '@daily') or crontab strings
    in the format 'm h dom mon dow'.
    """
    # Resolve schedule
    schedule = None
    if interval.startswith("@"):  # aliases
        alias = interval.lower()
        if alias == "@hourly":
            schedule = crontab(minute=0)
        elif alias == "@daily":
            schedule = crontab(minute=0, hour=0)
        elif alias == "@weekly":
            schedule = crontab(minute=0, hour=0, day_of_week="sun")
        else:
            schedule = crontab(minute=0)
    else:
        try:
            m, h, dom, mon, dow = interval.split()
            schedule = crontab(minute=m, hour=h, day_of_month=dom, month_of_year=mon, day_of_week=dow)
        except Exception:
            schedule = crontab(minute=0)

    celery_app.conf.beat_schedule = celery_app.conf.get("beat_schedule", {})
    celery_app.conf.beat_schedule[task_id] = {
        "task": "system_monitor.train_model_task",
        "schedule": schedule,
        "args": (model_name,),
    }


def schedule_forecast_updates(interval: str = "@hourly") -> None:
    """Register periodic forecast update task (default hourly)."""
    task_id = "scheduled_forecast_updates"
    if interval.startswith("@"):  # alias handling
        alias = interval.lower()
        if alias == "@hourly":
            schedule = crontab(minute=0)
        elif alias == "@daily":
            schedule = crontab(minute=0, hour=0)
        else:
            schedule = crontab(minute=0)
    else:
        try:
            m, h, dom, mon, dow = interval.split()
            schedule = crontab(minute=m, hour=h, day_of_month=dom, month_of_year=mon, day_of_week=dow)
        except Exception:
            schedule = crontab(minute=0)

    celery_app.conf.beat_schedule = celery_app.conf.get("beat_schedule", {})
    celery_app.conf.beat_schedule[task_id] = {
        "task": "system_monitor.update_forecast_task",
        "schedule": schedule,
    }
