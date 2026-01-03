from __future__ import annotations

import json
import socket
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore


def setup_load_balancer(
    backends: List[Tuple[str, int]],
    *,
    upstream_name: str = "backend_upstream",
    conf_path: str = "/etc/nginx/conf.d/dynamic_upstream.conf",
) -> Dict[str, Any]:
    """Write an NGINX upstream config for provided backends and reload NGINX if possible."""
    lines = [f"upstream {upstream_name} {{", "  least_conn;"]
    for host, port in backends:
        lines.append(f"  server {host}:{port} max_fails=3 fail_timeout=30s;")
    lines.append("}")
    content = "\n".join(lines) + "\n"
    p = Path(conf_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    # Attempt reload; ignore errors in dev
    try:
        subprocess.run(["nginx", "-s", "reload"], check=False)
    except Exception:
        pass
    return {"upstream": upstream_name, "path": str(p), "servers": len(backends)}


def monitor_node_health(
    backends: List[Tuple[str, int]],
    *,
    health_endpoint: str = "/health",
    timeout: float = 2.0,
) -> List[Dict[str, Any]]:
    """Check each backend for health via HTTP GET to health endpoint (if requests available), otherwise TCP check."""
    results: List[Dict[str, Any]] = []
    for host, port in backends:
        ok = False
        status = None
        try:
            if requests is not None:
                url = f"http://{host}:{port}{health_endpoint}"
                resp = requests.get(url, timeout=timeout)
                status = resp.status_code
                ok = (status == 200)
            else:
                with socket.create_connection((host, port), timeout=timeout):
                    ok = True
        except Exception as e:
            status = str(e)
        results.append({"host": host, "port": port, "healthy": ok, "status": status})
    return results


def route_traffic_dynamically(
    health: List[Dict[str, Any]],
    *,
    upstream_name: str = "backend_upstream",
    conf_path: str = "/etc/nginx/conf.d/dynamic_upstream.conf",
) -> Dict[str, Any]:
    """Rewrite upstream with only healthy backends and reload NGINX.

    Returns { written: bool, servers: n }.
    """
    healthy = [(h["host"], h["port"]) for h in health if h.get("healthy")]
    if not healthy:
        return {"written": False, "servers": 0, "note": "no healthy backends"}
    setup = setup_load_balancer(healthy, upstream_name=upstream_name, conf_path=conf_path)
    return {"written": True, "servers": setup["servers"], "path": setup["path"]}

