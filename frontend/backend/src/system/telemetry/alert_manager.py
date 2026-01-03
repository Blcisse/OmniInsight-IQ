from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

logger = logging.getLogger("alert_manager")

_RULES: List[Dict[str, Any]] = []


def configure_alert_rules(rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Set alert rules. Each rule: { name, metric, op, threshold, severity }"""
    global _RULES
    _RULES = list(rules)
    logger.info("Configured %d alert rules", len(_RULES))
    return {"rules": len(_RULES)}


def send_alert_notification(subject: str, message: str, *, channel: str = "log") -> Dict[str, Any]:
    """Dispatch an alert. Default channel is logging."""
    if channel == "log":
        logger.warning("ALERT: %s - %s", subject, message)
        return {"status": "logged"}
    return {"status": "ignored", "channel": channel}


def integrate_with_slack_webhook(webhook_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send a notification to a Slack webhook URL."""
    if requests is None:
        return {"ok": False, "error": "requests not installed"}
    try:
        resp = requests.post(webhook_url, json=payload, timeout=5)
        return {"ok": resp.status_code == 200, "status": resp.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)}

