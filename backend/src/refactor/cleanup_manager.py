from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
import re
import shutil
import gzip



def remove_empty_files(paths: Iterable[str]) -> List[str]:
    """Delete empty files and return a list of removed file paths."""
    removed: List[str] = []
    for p in map(Path, paths):
        if p.exists() and p.is_file() and p.stat().st_size == 0:
            p.unlink()
            removed.append(str(p))
    return removed


def normalize_line_endings(path: str) -> bool:
    """Convert CRLF to LF in the given file. Returns True if changed."""
    p = Path(path)
    if not p.exists() or not p.is_file():
        return False
    data = p.read_bytes()
    new = data.replace(b"\r\n", b"\n")
    if new != data:
        p.write_bytes(new)
        return True
    return False


def strip_trailing_whitespace(path: str) -> bool:
    """Strip trailing spaces from each line in the file. Returns True if changed."""
    p = Path(path)
    if not p.exists() or not p.is_file():
        return False
    text = p.read_text(encoding="utf-8", errors="ignore")
    new = "\n".join(line.rstrip() for line in text.splitlines()) + ("\n" if text.endswith("\n") else "")
    if new != text:
        p.write_text(new, encoding="utf-8")
        return True
    return False


def remove_unused_imports(path: str) -> bool:
    """Naively remove unused 'import ... as _' or commented imports.

    Note: For reliable import pruning, use tools like autoflake/pyflakes.
    This is a cautious heuristic to only remove clearly unused/commented imports.
    """
    p = Path(path)
    if not p.exists() or not p.is_file():
        return False
    text = p.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    changed = False
    new_lines: List[str] = []
    for ln in lines:
        # Drop fully commented import lines
        if re.match(r"^\s*#\s*(from\s+\S+\s+import\s+|import\s+\S+)", ln):
            changed = True
            continue
        # Drop imports aliased to '_' which are commonly unused placeholders
        if re.match(r"^\s*(from\s+\S+\s+import\s+\S+\s+as\s+_|import\s+\S+\s+as\s+_)\b", ln):
            changed = True
            continue
        new_lines.append(ln)
    if changed:
        p.write_text("\n".join(new_lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
    return changed


def delete_temp_files(root: str, patterns: Iterable[str] = ("*.tmp", "*.temp", "*.log.old")) -> List[str]:
    """Delete files matching patterns under root; returns list of removed paths."""
    removed: List[str] = []
    base = Path(root)
    for pat in patterns:
        for f in base.rglob(pat):
            try:
                if f.is_file():
                    f.unlink()
                    removed.append(str(f))
            except Exception:
                continue
    return removed


def compress_logs(root: str, pattern: str = "*.log", *, keep_original: bool = False) -> List[str]:
    """Gzip-compress .log files recursively under root. Returns list of created .gz files."""
    created: List[str] = []
    for f in Path(root).rglob(pattern):
        if not f.is_file() or f.suffix == ".gz":
            continue
        gz_path = f.with_suffix(f.suffix + ".gz")
        try:
            with f.open("rb") as src, gzip.open(gz_path, "wb") as dst:
                shutil.copyfileobj(src, dst)
            created.append(str(gz_path))
            if not keep_original:
                f.unlink()
        except Exception:
            # ignore failures and continue
            continue
    return created
