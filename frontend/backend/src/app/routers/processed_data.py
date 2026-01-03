"""
Routes for serving processed food datasets.
Provides alternative data source when database is not available or for testing.
"""
from __future__ import annotations

import os
import json
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/processed-data", tags=["processed-data"])


def get_processed_data_path() -> Path:
    """Get path to processed data directory."""
    base_dir = Path(__file__).parent.parent.parent.parent.parent
    return base_dir / "data" / "processed"


def load_processed_food_data(group: Optional[str] = None) -> pd.DataFrame:
    """Load processed food data.
    
    Args:
        group: Optional group name (group1-group5) or None for combined
        
    Returns:
        DataFrame with processed food data
    """
    data_path = get_processed_data_path()
    
    if group:
        file_path = data_path / f"food_data_{group}_processed.csv"
    else:
        file_path = data_path / "food_data_combined_processed.csv"
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Processed data file not found: {file_path}"
        )
    
    return pd.read_csv(file_path)


class FoodItem(BaseModel):
    food_name: str
    calories: Optional[float] = None
    fat: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    sugars: Optional[float] = None
    dietary_fiber: Optional[float] = None
    data_group: Optional[str] = None


class FoodAnalyticsSummary(BaseModel):
    total_foods: int
    avg_calories: float
    avg_protein: float
    avg_fat: float
    avg_carbs: float
    categories: Dict[str, int]


@router.get("/food", response_model=List[FoodItem])
async def get_food_data(
    group: Optional[str] = Query(None, description="Group name (group1-group5)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> List[FoodItem]:
    """Get processed food data.
    
    Returns paginated list of food items from processed datasets.
    """
    try:
        df = load_processed_food_data(group)
        
        # Paginate
        df_paged = df.iloc[offset:offset + limit]
        
        # Convert to dict records
        records = df_paged.to_dict("records")
        
        # Filter and map to response model
        items = []
        for record in records:
            item = {
                "food_name": str(record.get("food_name", "")),
                "calories": float(record.get("calories", 0)) if pd.notna(record.get("calories")) else None,
                "fat": float(record.get("fat", 0)) if pd.notna(record.get("fat")) else None,
                "protein": float(record.get("protein", 0)) if pd.notna(record.get("protein")) else None,
                "carbohydrates": float(record.get("carbohydrates", 0)) if pd.notna(record.get("carbohydrates")) else None,
                "sugars": float(record.get("sugars", 0)) if pd.notna(record.get("sugars")) else None,
                "dietary_fiber": float(record.get("dietary_fiber", 0)) if pd.notna(record.get("dietary_fiber")) else None,
                "data_group": str(record.get("data_group", "")) if "data_group" in record else None,
            }
            items.append(FoodItem(**item))
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading food data: {str(e)}")


@router.get("/food/summary", response_model=FoodAnalyticsSummary)
async def get_food_analytics_summary() -> FoodAnalyticsSummary:
    """Get analytics summary for processed food data."""
    try:
        summary_path = get_processed_data_path() / "food_analytics_summary.json"
        
        if not summary_path.exists():
            # Generate summary on the fly
            df = load_processed_food_data()
            summary = {
                "total_foods": len(df),
                "avg_calories": float(df["calories"].mean()) if "calories" in df.columns else 0.0,
                "avg_protein": float(df["protein"].mean()) if "protein" in df.columns else 0.0,
                "avg_fat": float(df["fat"].mean()) if "fat" in df.columns else 0.0,
                "avg_carbs": float(df["carbohydrates"].mean()) if "carbohydrates" in df.columns else 0.0,
                "categories": df["data_group"].value_counts().to_dict() if "data_group" in df.columns else {},
            }
        else:
            with open(summary_path) as f:
                summary = json.load(f)
        
        return FoodAnalyticsSummary(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading summary: {str(e)}")


@router.get("/food/stats")
async def get_food_stats() -> Dict[str, Any]:
    """Get statistical summary of food data for dashboard KPIs."""
    try:
        df = load_processed_food_data()
        
        stats = {
            "total_items": len(df),
            "nutrition_stats": {
                "calories": {
                    "min": float(df["calories"].min()) if "calories" in df.columns else 0,
                    "max": float(df["calories"].max()) if "calories" in df.columns else 0,
                    "avg": float(df["calories"].mean()) if "calories" in df.columns else 0,
                },
                "protein": {
                    "min": float(df["protein"].min()) if "protein" in df.columns else 0,
                    "max": float(df["protein"].max()) if "protein" in df.columns else 0,
                    "avg": float(df["protein"].mean()) if "protein" in df.columns else 0,
                },
                "fat": {
                    "min": float(df["fat"].min()) if "fat" in df.columns else 0,
                    "max": float(df["fat"].max()) if "fat" in df.columns else 0,
                    "avg": float(df["fat"].mean()) if "fat" in df.columns else 0,
                },
            },
            "by_group": df["data_group"].value_counts().to_dict() if "data_group" in df.columns else {},
        }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing stats: {str(e)}")

