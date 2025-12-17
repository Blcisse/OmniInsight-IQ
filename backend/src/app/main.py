import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def monitoring_startup(app: FastAPI) -> None:
    """Initialize background model performance tracking hooks at app startup.

    Currently ensures logging is configured and can be extended to warm Redis
    connections or schedule periodic monitoring tasks.
    """
    import logging
    from src.system.monitoring.performance_tracker import record_metric

    logger = logging.getLogger("uvicorn")

    @app.on_event("startup")
    async def _on_startup():
        try:
            # Write a tiny marker to indicate service start for monitoring dashboards
            record_metric("service", "startup", 1)
            logger.info("Monitoring initialized: performance tracker ready")
        except Exception as e:
            logger.warning("Monitoring initialization failed: %s", e)


def telemetry_startup(app: FastAPI) -> None:
    """Initialize telemetry collectors and (optionally) Prometheus exporter."""
    import logging
    from src.system.telemetry.metrics_collector import collect_system_metrics, export_metrics_to_prometheus

    logger = logging.getLogger("telemetry")

    @app.on_event("startup")
    async def _telemetry_start():
        try:
            # Capture initial system metrics
            metrics = collect_system_metrics()
            logger.info("Telemetry initialized: cpu=%s mem=%s", metrics.get("cpu_percent"), metrics.get("mem_percent"))
            # Start Prometheus exporter if env is set
            if os.getenv("ENABLE_PROMETHEUS_EXPORTER", "false").lower() in {"1", "true", "yes"}:
                out = export_metrics_to_prometheus(start_http=True, port=int(os.getenv("PROMETHEUS_PORT", "9464")))
                logger.info("Prometheus exporter: %s", out)
        except Exception as e:
            logger.warning("Telemetry startup failed: %s", e)


def create_app() -> FastAPI:
    app = FastAPI(title="OmniInsightIQ API")

    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and include routers. These imports are local to avoid issues
    # if modules are optional or loaded later.
    try:
        from .routers import sales  # type: ignore
        app.include_router(sales.router)
    except Exception:
        pass

    try:
        from .routers import analytics  # type: ignore
        app.include_router(analytics.router)
    except Exception:
        pass

    try:
        from .routers import marketing  # type: ignore
        app.include_router(marketing.router)
    except Exception:
        pass

    try:
        from .routers import insights  # type: ignore
        app.include_router(insights.router)
    except Exception:
        pass

    try:
        from .routers import insightops_router  # type: ignore
        app.include_router(insightops_router.router)
    except Exception:
        pass

    # Include AI & Predictive Engine routes
    try:
        from src.api.model_inference.model_inference_router import router as model_inference_router  # type: ignore
        app.include_router(model_inference_router, tags=["AI & Predictive Engine"])
    except Exception:
        pass

    # Include Health Intelligence endpoints (JSON & CSV)
    try:
        from src.api.health_intel.health_intel_router import router as health_intel_router  # type: ignore
        app.include_router(health_intel_router)
    except Exception:
        pass

    # Include Sales Intelligence endpoints (JSON & CSV)
    try:
        from src.api.sales_metrics.sales_metrics_router import router as sales_metrics_router  # type: ignore
        app.include_router(sales_metrics_router)
    except Exception:
        pass

    # Include Analytics Dashboard visualization routes
    try:
        from src.api.analytics_dashboard.analytics_dashboard_router import router as analytics_dashboard_router  # type: ignore
        app.include_router(analytics_dashboard_router, tags=["Analytics Dashboard"])
    except Exception:
        pass

    # Include Processed Data routes
    try:
        from .routers import processed_data  # type: ignore
        app.include_router(processed_data.router)
    except Exception:
        pass

    # CSV-backed reports (e.g., FOOD-DATA-GROUP1.csv)
    try:
        from src.api.reports_csv.reports_csv_router import router as reports_csv_router  # type: ignore
        app.include_router(reports_csv_router)
    except Exception:
        pass

    # Include authentication routes
    try:
        from .routers import auth  # type: ignore
        app.include_router(auth.router)
    except Exception:
        pass

    # Include user management routes
    try:
        from .routers import users  # type: ignore
        app.include_router(users.router)
    except Exception:
        pass

    # Include admin panel routes
    try:
        from .routers import admin  # type: ignore
        app.include_router(admin.router)
    except Exception:
        pass

    # Include data ingestion routes
    try:
        from .routers import data_ingest  # type: ignore
        app.include_router(data_ingest.router)
    except Exception:
        pass

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # Seed development users on startup (only if enabled)
    @app.on_event("startup")
    async def seed_users():
        try:
            from .core.seed import seed_development_users
            await seed_development_users()
        except Exception as e:
            import logging
            logger = logging.getLogger("uvicorn")
            logger.warning("Seed failed: %s", e)

    monitoring_startup(app)
    telemetry_startup(app)

    return app


# ASGI entrypoint
app = create_app()
