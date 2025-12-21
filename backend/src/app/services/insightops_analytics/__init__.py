"""InsightOps analytics layer (CD3).

Provides shared constants, time helpers, types, and DB accessors for KPI and
engagement series queries. Built to stay deterministic and reusable across
dashboards and services.
"""

from .constants import (  # noqa: F401
    ALLOWED_KPI_KEYS,
    ALLOWED_SIGNAL_KEYS,
    DEFAULT_LOOKBACK_DAYS,
    DEFAULT_ORG_ID,
)
from .db import fetch_kpi_series, fetch_signal_series  # noqa: F401
from .kpis import compute_kpi_delta, compute_rolling_average, get_kpi_series  # noqa: F401
from .time import default_window, parse_date  # noqa: F401
from .types import DateWindow, MetricSeriesPoint, SeriesResponse  # noqa: F401
