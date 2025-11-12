from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict


def sort_python_imports(path: str) -> bool:
    """Naive import sorter that groups and alphabetizes top-level imports.

    For production use, prefer `isort`. Returns True if file changed.
    """
    p = Path(path)
    if not p.exists() or not p.is_file():
        return False
    text = p.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    import_lines: List[str] = []
    other_lines: List[str] = []
    in_header = True
    for ln in lines:
        if in_header and re.match(r"^(from\s+\S+\s+import\s+|import\s+\S+)", ln):
            import_lines.append(ln)
        else:
            in_header = False
            other_lines.append(ln)

    if not import_lines:
        return False

    # Sort imports alphabetically
    sorted_imports = sorted(import_lines)
    new_text = "\n".join(sorted_imports + other_lines) + ("\n" if text.endswith("\n") else "")
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        return True
    return False


def _group_imports(imports: List[str]) -> Dict[str, List[str]]:
    stdlib_prefixes = (
        "abc ai asyncio base64 collections concurrent contextlib copy csv dataclasses datetime decimal enum functools glob hashlib heapq hmac html http io itertools json logging math mimetypes os pathlib pickle platform pprint queue random re sched secrets shutil signal socket sqlite3 ssl statistics string struct subprocess sys tempfile textwrap threading time types typing uuid warnings weakref zlib".split()
    )
    std = []
    third = []
    local = []
    for ln in imports:
        m = re.match(r"^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))", ln)
        mod = m.group(1) or m.group(2) if m else ""
        root = (mod or "").split(".")[0]
        if root in stdlib_prefixes:
            std.append(ln)
        elif root.startswith("src") or root.startswith("backend") or root.startswith("app"):
            local.append(ln)
        else:
            third.append(ln)
    return {"stdlib": sorted(std), "third": sorted(third), "local": sorted(local)}


def sort_imports_by_standard(path: str) -> bool:
    """Sort imports by groups: stdlib, third-party, local; alphabetize within groups."""
    p = Path(path)
    if not p.exists() or not p.is_file():
        return False
    text = p.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    import_lines: List[str] = []
    other_lines: List[str] = []
    in_header = True
    for ln in lines:
        if in_header and re.match(r"^(from\s+\S+\s+import\s+|import\s+\S+)", ln):
            import_lines.append(ln)
        else:
            in_header = False
            other_lines.append(ln)
    if not import_lines:
        return False
    grouped = _group_imports(import_lines)
    new_block: List[str] = []
    for grp in ("stdlib", "third", "local"):
        if grouped[grp]:
            new_block.extend(grouped[grp])
            new_block.append("")
    if new_block and new_block[-1] == "":
        new_block.pop()
    new_text = "\n".join(new_block + other_lines) + ("\n" if text.endswith("\n") else "")
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        return True
    return False


def validate_dependencies(path: str, required: List[str]) -> List[str]:
    """Return missing top-level imports from `required` list found in file."""
    p = Path(path)
    if not p.exists() or not p.is_file():
        return required
    text = p.read_text(encoding="utf-8", errors="ignore")
    present = set()
    for m in re.finditer(r"^(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))", text, flags=re.M):
        mod = m.group(1) or m.group(2)
        present.add((mod or "").split(".")[0])
    missing = [pkg for pkg in required if pkg not in present]
    return missing


def refactor_init_files(package_dir: str) -> List[str]:
    """Ensure __init__.py exists in all subpackages under package_dir; return created paths."""
    created: List[str] = []
    root = Path(package_dir)
    if not root.exists():
        return created
    for d in root.rglob("*"):
        if d.is_dir():
            init = d / "__init__.py"
            if not init.exists():
                init.write_text("", encoding="utf-8")
                created.append(str(init))
    return created
