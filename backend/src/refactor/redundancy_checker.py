from __future__ import annotations

from typing import Dict, Iterable, List, Tuple
import ast
import re


def find_duplicate_routes(paths: Iterable[str]) -> Dict[str, List[str]]:
    """Given a list of route paths, return duplicates mapped to their occurrences.

    Example input: ["/api/a", "/api/b", "/api/a"] -> {"/api/a": [0, 2]}
    """
    index: Dict[str, List[int]] = {}
    for i, p in enumerate(paths):
        index.setdefault(p, []).append(i)
    return {k: v for k, v in index.items() if len(v) > 1}


def detect_redundant_fields(records: Iterable[Dict[str, object]], *, threshold: float = 0.99) -> List[str]:
    """Return field names that are nearly constant across records (>= threshold same value)."""
    counts: Dict[str, Dict[object, int]] = {}
    total = 0
    for rec in records:
        total += 1
        for k, v in rec.items():
            d = counts.setdefault(k, {})
            d[v] = d.get(v, 0) + 1
    redundant: List[str] = []
    for k, d in counts.items():
        top = max(d.values()) if d else 0
        if total > 0 and (top / total) >= threshold:
            redundant.append(k)
    return redundant


def detect_duplicate_functions(source: str) -> List[Tuple[str, str]]:
    """Detect duplicate function bodies within a Python source string.

    Returns list of (func_name, duplicate_of) pairs for functions whose AST bodies hash equal.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    hashes: Dict[str, str] = {}
    dups: List[Tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            body_src = ast.get_source_segment(source, node) or ast.unparse(node) if hasattr(ast, "unparse") else node.name
            key = str(hash(re.sub(r"\s+", " ", body_src)))
            for fname, h in list(hashes.items()):
                if h == key:
                    dups.append((node.name, fname))
                    break
            else:
                hashes[node.name] = key
    return dups


def merge_similar_modules(mod_a: str, mod_b: str) -> str:
    """Naively merge two small Python modules, de-duplicating identical functions.

    Prefers definitions from mod_a when duplicates exist. Returns merged source text.
    """
    # Collect function names from mod_a
    try:
        tree_a = ast.parse(mod_a)
        fnames_a = {n.name for n in ast.walk(tree_a) if isinstance(n, ast.FunctionDef)}
    except SyntaxError:
        fnames_a = set()

    # Append only non-duplicate defs from mod_b
    merged = [mod_a.rstrip(), ""]
    try:
        tree_b = ast.parse(mod_b)
        for node in tree_b.body:
            if isinstance(node, ast.FunctionDef) and node.name in fnames_a:
                continue
            # Fallback to raw segment extraction when possible
            seg = ast.get_source_segment(mod_b, node)
            merged.append((seg or (ast.unparse(node) if hasattr(ast, "unparse") else "")))
    except SyntaxError:
        merged.append(mod_b)
    return "\n".join([m for m in merged if m is not None])


def unify_docstrings(source: str, *, style: str = "google") -> str:
    """Best-effort docstring normalization across functions and modules.

    - style: currently a no-op placeholder ('google' | 'numpy' supported later)
    Converts triple single quotes to triple double quotes and strips leading spaces.
    """
    # Replace ''' with """
    text = re.sub(r"'''", '"""', source)
    # Normalize indentation of docstring lines (basic)
    lines = text.splitlines()
    out: List[str] = []
    for ln in lines:
        if re.match(r"^\s*\"\"\"", ln):
            out.append(ln.lstrip())
        else:
            out.append(ln)
    return "\n".join(out)
