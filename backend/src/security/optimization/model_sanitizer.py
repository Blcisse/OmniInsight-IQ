from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def verify_model_integrity(file_path: str, expected_hash: str) -> bool:
    """Compute sha256 of a model file and compare with expected hash."""
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return False
    return _sha256_file(p) == expected_hash.lower()


def hash_model_files(root: str, *, patterns: Optional[List[str]] = None) -> Dict[str, str]:
    """Return a mapping of relative file paths -> sha256 hash for given patterns."""
    patterns = patterns or ["*.joblib", "*.pkl", "saved_model.pb"]
    base = Path(root)
    results: Dict[str, str] = {}
    for pattern in patterns:
        for p in base.rglob(pattern):
            if p.is_file():
                rel = str(p.relative_to(base))
                results[rel] = _sha256_file(p)
    return results


def detect_tampering(previous_hashes: Dict[str, str], new_root: str, *, patterns: Optional[List[str]] = None) -> Dict[str, List[str]]:
    """Compare previous file hashes against current ones and report changes.

    Returns dict with keys: 'modified', 'missing', 'new'.
    """
    current = hash_model_files(new_root, patterns=patterns)
    prev_keys = set(previous_hashes.keys())
    cur_keys = set(current.keys())
    modified = [k for k in prev_keys & cur_keys if previous_hashes.get(k) != current.get(k)]
    missing = [k for k in prev_keys - cur_keys]
    new = [k for k in cur_keys - prev_keys]
    return {"modified": modified, "missing": missing, "new": new}

