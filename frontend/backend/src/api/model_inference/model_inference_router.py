from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from .model_schema import (
    InferenceRequest,
    InferenceResponse,
    ForecastInput,
    ForecastOutput,
    RecommendationInput,
    RecommendationOutput,
    RecommendationItem,
)
from .model_service import load_trained_model, predict

try:
    from src.ai.forecasting.forecast_inference import run_forecast
except Exception:  # pragma: no cover
    from ...ai.forecasting.forecast_inference import run_forecast  # type: ignore

try:
    from src.ai.recommendation_engine.rec_core import generate_recommendations
except Exception:  # pragma: no cover
    from ...ai.recommendation_engine.rec_core import generate_recommendations  # type: ignore


router = APIRouter(prefix="/api/model-inference", tags=["model-inference"])


@router.post("/predict", response_model=InferenceResponse)
def model_predict(req: InferenceRequest) -> InferenceResponse:
    try:
        model = load_trained_model(req.models_dir or "models", req.model_name, req.version)
        preds, proba, meta = predict(
            model=model,
            records=req.records,
            framework=req.framework,
            feature_order=req.feature_order,
            return_proba=bool(req.return_proba),
        )
        return InferenceResponse(
            model_name=req.model_name,
            version=req.version,
            framework=meta.get("framework", req.framework or "unknown"),
            count=len(preds),
            predictions=preds,
            probabilities=proba,
            meta=meta,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/forecast", response_model=ForecastOutput)
def model_forecast(req: ForecastInput) -> ForecastOutput:
    try:
        import pandas as pd

        history_df = pd.DataFrame.from_records(req.history)
        fc = run_forecast(
            model_name=req.model_name,
            timeframe=req.timeframe,
            models_dir=req.models_dir or "models",
            history=history_df,
            date_col=req.date_col,
            target_col=req.target_col,
            exog_cols=req.exog_cols,
        )
        return ForecastOutput(
            model_name=req.model_name,
            timeframe=req.timeframe,
            count=len(fc),
            forecast=fc,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/recommend", response_model=RecommendationOutput)
def model_recommend(req: RecommendationInput) -> RecommendationOutput:
    try:
        import pandas as pd

        df = pd.DataFrame.from_records(req.records)
        context: Dict[str, Any] = {
            "algorithm": req.algorithm,
            "df": df,
            "user_col": req.user_col,
            "item_col": req.item_col,
            "rating_col": req.rating_col,
            "top_k": req.top_k,
            "seen_items": req.seen_items,
            "user_ratings": req.user_ratings,
        }
        recs = generate_recommendations(context)
        items = [RecommendationItem(item=i, score=float(s)) for i, s in recs]
        return RecommendationOutput(count=len(items), recommendations=items)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
