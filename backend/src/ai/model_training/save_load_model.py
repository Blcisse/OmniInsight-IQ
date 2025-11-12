from __future__ import annotations

from pathlib import Path
from typing import Any, Tuple, Dict, List, Optional

import joblib
import json
from datetime import datetime
import shutil


def save_sklearn(model: Any, path: str | Path) -> None:
    """Persist a scikit-learn Pipeline/estimator using joblib."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_sklearn(path: str | Path) -> Any:
    """Load a scikit-learn Pipeline/estimator persisted by joblib."""
    return joblib.load(path)


def save_tensorflow(model: Any, path: str | Path) -> None:
    """Save a TensorFlow Keras model in SavedModel format."""
    import tensorflow as tf  # type: ignore

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tf.keras.models.save_model(model, str(path))


def load_tensorflow(path: str | Path) -> Any:
    """Load a TensorFlow Keras model (SavedModel)."""
    import tensorflow as tf  # type: ignore

    return tf.keras.models.load_model(str(path))


def save_generic(obj: Any, path: str | Path, framework: str = "sklearn") -> None:
    """Save model/pipeline depending on framework ('sklearn' or 'tensorflow')."""
    if framework == "tensorflow":
        return save_tensorflow(obj, path)
    return save_sklearn(obj, path)


def load_generic(path: str | Path, framework: str = "sklearn") -> Any:
    """Load model/pipeline depending on framework ('sklearn' or 'tensorflow')."""
    if framework == "tensorflow":
        return load_tensorflow(path)
    return load_sklearn(path)


# Versioned model management helpers
def _model_root(models_dir: str | Path, name: str) -> Path:
    root = Path(models_dir) / name
    root.mkdir(parents=True, exist_ok=True)
    return root


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")


def _write_metadata(dirpath: Path, meta: Dict[str, Any]) -> None:
    with (dirpath / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def _read_metadata(dirpath: Path) -> Dict[str, Any]:
    with (dirpath / "metadata.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def _latest_version_dir(root: Path) -> Optional[Path]:
    if not root.exists():
        return None
    versions = [p for p in root.iterdir() if p.is_dir()]
    if not versions:
        return None
    # Sort by name descending (timestamps) then by mtime
    versions.sort(key=lambda p: (p.name, p.stat().st_mtime), reverse=True)
    return versions[0]


def save_model(
    obj: Any,
    models_dir: str | Path,
    name: str,
    *,
    framework: str = "sklearn",
    version: Optional[str] = None,
    extra_meta: Optional[Dict[str, Any]] = None,
) -> str:
    """Save a model artifact with simple versioning.

    - Creates `<models_dir>/<name>/<version>/`
    - Writes model under that directory and a `metadata.json`
    - Returns the version string used
    """
    root = _model_root(models_dir, name)
    ver = version or _timestamp()
    ver_dir = root / ver
    # Ensure unique dir if provided version already exists
    suffix = 1
    while ver_dir.exists():
        ver_dir = root / f"{ver}_{suffix}"
        suffix += 1
    ver_dir.mkdir(parents=True, exist_ok=True)

    if framework == "tensorflow":
        artifact = ver_dir / "model"
        save_tensorflow(obj, artifact)
    else:
        artifact = ver_dir / "model.joblib"
        save_sklearn(obj, artifact)

    meta = {
        "name": name,
        "version": ver_dir.name,
        "framework": framework,
        "artifact": artifact.name,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    if extra_meta:
        meta.update(extra_meta)
    _write_metadata(ver_dir, meta)
    return ver_dir.name


def load_model(
    models_dir: str | Path,
    name: str,
    version: Optional[str] = None,
) -> Any:
    """Load a saved model by name and optional version (latest by default)."""
    root = Path(models_dir) / name
    if not root.exists():
        raise FileNotFoundError(f"Model '{name}' not found in {models_dir}")
    ver_dir = root / version if version else _latest_version_dir(root)
    if not ver_dir or not ver_dir.exists():
        raise FileNotFoundError(f"Version '{version}' for model '{name}' not found")
    meta = _read_metadata(ver_dir)
    artifact = ver_dir / meta.get("artifact", "model.joblib")
    framework = meta.get("framework", "sklearn")
    return load_generic(artifact, framework=framework)


def list_models(models_dir: str | Path, name: Optional[str] = None) -> Dict[str, List[str]]:
    """List available models and versions under a directory.

    - When `name` is provided, returns {name: [versions...]}
    - Otherwise returns a mapping for all models present
    """
    models_path = Path(models_dir)
    result: Dict[str, List[str]] = {}
    if name:
        root = models_path / name
        versions = [p.name for p in root.iterdir() if p.is_dir()] if root.exists() else []
        versions.sort(reverse=True)
        return {name: versions}
    for model_dir in models_path.iterdir() if models_path.exists() else []:
        if not model_dir.is_dir():
            continue
        versions = [p.name for p in model_dir.iterdir() if p.is_dir()]
        versions.sort(reverse=True)
        result[model_dir.name] = versions
    return result


def delete_model(models_dir: str | Path, name: str, version: Optional[str] = None) -> None:
    """Delete a model version or the entire model directory if no version given."""
    root = Path(models_dir) / name
    if not root.exists():
        return
    if version is None:
        shutil.rmtree(root, ignore_errors=True)
    else:
        ver_dir = root / version
        if ver_dir.exists():
            shutil.rmtree(ver_dir, ignore_errors=True)
