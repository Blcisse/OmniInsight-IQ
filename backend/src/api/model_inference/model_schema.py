from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    model_name: str = Field(..., description="Registered model name")
    version: Optional[str] = Field(None, description="Optional model version (latest if omitted)")
    models_dir: Optional[str] = Field("models", description="Base directory where models are stored")
    framework: Optional[Literal["sklearn", "tensorflow"]] = Field(
        None, description="Force framework if autodetection is not desired"
    )
    records: List[Dict[str, Any]] = Field(..., description="List of feature dicts for prediction")
    feature_order: Optional[List[str]] = Field(
        None, description="Explicit feature order for array-based models (e.g., TensorFlow)"
    )
    return_proba: Optional[bool] = Field(
        False, description="For sklearn classifiers, return predict_proba when available"
    )


class InferenceResponse(BaseModel):
    model_name: str
    version: Optional[str]
    framework: str
    count: int
    predictions: List[Any]
    probabilities: Optional[List[Any]] = None
    meta: Dict[str, Any] = {}


# New canonical schemas for input/output validation

class PredictionInput(BaseModel):
    model_name: str
    version: Optional[str] = None
    models_dir: Optional[str] = "models"
    framework: Optional[Literal["sklearn", "tensorflow"]] = None
    records: List[Dict[str, Any]]
    feature_order: Optional[List[str]] = None
    return_proba: bool = False


class PredictionOutput(BaseModel):
    model_name: str
    version: Optional[str]
    framework: str
    count: int
    predictions: List[Any]
    probabilities: Optional[List[Any]] = None
    meta: Dict[str, Any] = {}


class ForecastInput(BaseModel):
    model_name: str
    timeframe: int = 7
    models_dir: Optional[str] = "models"
    history: List[Dict[str, Any]]
    date_col: str = "date"
    target_col: str = "target"
    exog_cols: Optional[List[str]] = None


class ForecastOutput(BaseModel):
    model_name: str
    timeframe: int
    count: int
    forecast: List[Dict[str, Any]]


class RecommendationInput(BaseModel):
    algorithm: Literal["popularity", "item_knn"] = "popularity"
    records: List[Dict[str, Any]]
    user_col: Optional[str] = None
    item_col: str
    rating_col: str
    top_k: int = 10
    seen_items: Optional[List[Any]] = None
    user_ratings: Optional[Dict[str, float]] = None


class RecommendationItem(BaseModel):
    item: Any
    score: float


class RecommendationOutput(BaseModel):
    count: int
    recommendations: List[RecommendationItem]
