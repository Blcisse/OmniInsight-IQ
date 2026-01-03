from __future__ import annotations

import logging
import socket
from typing import Any, Dict, List, Tuple


logger = logging.getLogger("failover")


def check_endpoint(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def select_active_backend(candidates: List[Tuple[str, int]], *, timeout: float = 1.5) -> Dict[str, Any]:
    """Return the first healthy backend from candidates or a failover notice."""
    for host, port in candidates:
        if check_endpoint(host, port, timeout=timeout):
            return {"host": host, "port": port, "healthy": True}
    return {"healthy": False, "reason": "no healthy backends"}


def detect_service_failure(current_host: str, current_port: int, *, timeout: float = 1.5) -> bool:
    """Return True if the current service endpoint is unreachable."""
    ok = check_endpoint(current_host, current_port, timeout=timeout)
    return not ok


def log_failover_event(old_host: str, old_port: int, new_host: str, new_port: int, *, reason: str = "unhealthy") -> None:
    """Log a failover event for audit and observability."""
    logger.warning(
        "Failover: %s:%s -> %s:%s (reason=%s)", old_host, old_port, new_host, new_port, reason
    )


def initiate_failover_sequence(
    candidates: List[Tuple[str, int]],
    *,
    current: Tuple[str, int],
    timeout: float = 1.5,
) -> Dict[str, Any]:
    """If current is down, select a healthy backend and log the failover.

    Returns { 'failed': bool, 'new': {host,port,healthy}? }.
    """
    cur_host, cur_port = current
    if not detect_service_failure(cur_host, cur_port, timeout=timeout):
        return {"failed": False}
    sel = select_active_backend(candidates, timeout=timeout)
    if sel.get("healthy"):
        log_failover_event(cur_host, cur_port, sel["host"], sel["port"], reason="unhealthy")
        return {"failed": True, "new": sel}
    logger.error("Failover requested but no healthy backends available")
    return {"failed": True, "new": None}
