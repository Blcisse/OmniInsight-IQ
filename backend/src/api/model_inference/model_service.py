from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    from src.ai.model_training.save_load_model import load_model
except Exception:  # pragma: no cover - fallback when executed as a module
    from ...ai.model_training.save_load_model import load_model  # type: ignore


def _infer_framework(model: Any, forced: Optional[str] = None) -> str:
    if forced in {"sklearn", "tensorflow"}:
        return forced
    mod = getattr(model, "__module__", "")
    if "tensorflow" in mod or "keras" in mod:
        return "tensorflow"
    # default to sklearn for typical pipelines/estimators
    return "sklearn"


def _to_dataframe(records: List[Dict[str, Any]]) -> pd.DataFrame:
    if not records:
        raise ValueError("No records provided for inference")
    return pd.DataFrame.from_records(records)


def _to_array(df: pd.DataFrame, feature_order: Optional[List[str]]) -> np.ndarray:
    if feature_order:
        missing = [c for c in feature_order if c not in df.columns]
        if missing:
            raise ValueError(f"Missing features in records: {missing}")
        X = df[feature_order].to_numpy()
    else:
        X = df.to_numpy()
    return X


def load_trained_model(models_dir: str, model_name: str, version: Optional[str]) -> Any:
    return load_model(models_dir=models_dir, name=model_name, version=version)


def predict(
    *,
    model: Any,
    records: List[Dict[str, Any]],
    framework: Optional[str] = None,
    feature_order: Optional[List[str]] = None,
    return_proba: bool = False,
) -> Tuple[List[Any], Optional[List[Any]], Dict[str, Any]]:
    """Run predictions for the provided records using a loaded model.

    Returns (predictions, probabilities_or_none, meta)
    """
    df = _to_dataframe(records)
    fmk = _infer_framework(model, forced=framework)
    meta: Dict[str, Any] = {"framework": fmk, "n_features": int(df.shape[1])}

    if fmk == "tensorflow":
        X = _to_array(df, feature_order)
        preds = model.predict(X)  # type: ignore[attr-defined]
        # Convert to python types
        preds_list = np.asarray(preds).tolist()
        return preds_list, None, meta

    # sklearn path
    # Attempt to call predict; also collect probabilities when requested
    y_pred = model.predict(df)  # type: ignore[attr-defined]
    proba_list: Optional[List[Any]] = None
    if return_proba and hasattr(model, "predict_proba"):
        try:
            proba = model.predict_proba(df)  # type: ignore[attr-defined]
            proba_list = np.asarray(proba).tolist()
        except Exception:
            proba_list = None
    preds_list = np.asarray(y_pred).tolist()
    return preds_list, proba_list, meta


def load_model_from_storage(
    model_name: str,
    *,
    version: Optional[str] = None,
    models_dir: str = "models",
) -> Any:
    """Convenience wrapper to load a trained model from storage."""
    return load_trained_model(models_dir=models_dir, model_name=model_name, version=version)


def run_inference(
    model_name: str,
    input_data: List[Dict[str, Any]],
    *,
    version: Optional[str] = None,
    models_dir: str = "models",
    framework: Optional[str] = None,
    feature_order: Optional[List[str]] = None,
    return_proba: bool = False,
) -> Tuple[List[Any], Optional[List[Any]], Dict[str, Any]]:
    """Load a model by name/version and run inference on the provided records."""
    model = load_model_from_storage(model_name, version=version, models_dir=models_dir)
    return predict(
        model=model,
        records=input_data,
        framework=framework,
        feature_order=feature_order,
        return_proba=return_proba,
    )


def batch_inference_handler(
    jobs: List[Dict[str, Any]],
    *,
    default_models_dir: str = "models",
) -> List[Dict[str, Any]]:
    """Process a batch of inference jobs.

    Each job dict may contain keys compatible with InferenceRequest, e.g.:
      {
        "model_name": str,
        "version": Optional[str],
        "models_dir": Optional[str],
        "records": List[dict],
        "framework": Optional[str],
        "feature_order": Optional[List[str]],
        "return_proba": Optional[bool]
      }

    Returns a list of result dicts with predictions or error info per job.
    """
    results: List[Dict[str, Any]] = []
    for job in jobs:
        try:
            model_name = job.get("model_name")
            if not model_name:
                raise ValueError("job missing 'model_name'")
            records = job.get("records")
            if not isinstance(records, list) or not records:
                raise ValueError("job 'records' must be a non-empty list")
            version = job.get("version")
            models_dir = job.get("models_dir") or default_models_dir
            framework = job.get("framework")
            feature_order = job.get("feature_order")
            return_proba = bool(job.get("return_proba", False))

            preds, proba, meta = run_inference(
                model_name,
                input_data=records,
                version=version,
                models_dir=models_dir,
                framework=framework,
                feature_order=feature_order,
                return_proba=return_proba,
            )
            results.append(
                {
                    "model_name": model_name,
                    "version": version,
                    "count": len(preds),
                    "predictions": preds,
                    "probabilities": proba,
                    "meta": meta,
                }
            )
        except Exception as e:
            results.append({"error": str(e), "model_name": job.get("model_name")})
    return results
