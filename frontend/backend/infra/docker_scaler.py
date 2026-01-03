from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


def _run(cmd: List[str], *, cwd: Optional[str] = None) -> Dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        return {"ok": True, "stdout": proc.stdout, "stderr": proc.stderr}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def optimize_docker_builds(dockerfile_path: str) -> Dict[str, Any]:
    """Provide guidance and quick checks to optimize Docker builds.

    - Validates existence of Dockerfile
    - Returns recommended flags and multi-stage best practices summary
    """
    p = Path(dockerfile_path)
    exists = p.exists()
    tips = [
        "Use multi-stage builds to minimize final image size",
        "Leverage .dockerignore to reduce build context",
        "Order RUN steps from least to most likely to change to maximize layer caching",
        "Pin base images and package versions for reproducibility",
        "Use --no-cache-dir for pip/apt where appropriate",
    ]
    return {"dockerfile": str(p), "exists": exists, "recommendations": tips}


def implement_docker_layer_caching(
    context_dir: str = ".",
    *,
    tag: str = "app:latest",
    cache_from: Optional[List[str]] = None,
    use_buildx: bool = True,
    execute: bool = False,
) -> Dict[str, Any]:
    """Prepare a docker build command that uses layer caching.

    - When execute=True, runs the command and returns result
    """
    cache_args: List[str] = []
    if cache_from:
        for ref in cache_from:
            cache_args += ["--cache-from", ref]

    if use_buildx:
        cmd = [
            "docker", "buildx", "build", "--progress=plain", "--pull", "-t", tag,
        ] + cache_args + [context_dir]
    else:
        cmd = ["docker", "build", "--pull", "-t", tag] + cache_args + [context_dir]

    if execute:
        return {"cmd": cmd, **_run(cmd, cwd=context_dir)}
    return {"cmd": cmd}


def manage_multi_container_deployments(
    compose_file: str = "docker-compose.yml",
    *,
    scale: Optional[Dict[str, int]] = None,
    execute: bool = False,
) -> Dict[str, Any]:
    """Scale services using docker compose. Returns command (and optionally output)."""
    base = ["docker", "compose", "-f", compose_file]
    cmds: List[str] = []
    if scale:
        for svc, n in scale.items():
            cmds.append("--scale")
            cmds.append(f"{svc}={int(n)}")
    full_cmd = base + ["up", "-d"] + cmds
    if execute:
        return {"cmd": full_cmd, **_run(full_cmd)}
    return {"cmd": full_cmd}

