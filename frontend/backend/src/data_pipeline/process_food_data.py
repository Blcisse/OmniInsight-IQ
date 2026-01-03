"""
Process raw food datasets and prepare them for analytics.
Converts raw CSV files to processed format suitable for dashboard consumption.
"""
from __future__ import annotations

import os
import pandas as pd
from pathlib import Path
from typing import Optional

from .data_cleaner import clean_raw_data


def process_food_dataset(
    input_path: str,
    output_path: Optional[str] = None,
    group_name: Optional[str] = None,
) -> pd.DataFrame:
    """Process a single food dataset CSV file.
    
    Args:
        input_path: Path to raw CSV file
        output_path: Optional path to save processed CSV
        group_name: Optional group identifier
        
    Returns:
        Cleaned and processed DataFrame
    """
    # Read raw data
    df = pd.read_csv(input_path)
    
    # Clean the data
    df_clean = clean_raw_data(df)
    
    # Add metadata
    if group_name:
        df_clean["data_group"] = group_name
    
    # Standardize food name column
    if "food" in df_clean.columns:
        df_clean["food_name"] = df_clean["food"].astype(str).str.strip()
        df_clean = df_clean.drop(columns=["food"], errors="ignore")
    
    # Rename caloric value to calories for consistency
    if "caloric_value" in df_clean.columns:
        df_clean["calories"] = pd.to_numeric(df_clean["caloric_value"], errors="coerce")
        df_clean = df_clean.drop(columns=["caloric_value"], errors="ignore")
    
    # Ensure numeric columns are properly typed
    numeric_cols = [
        "calories", "fat", "saturated_fats", "carbohydrates", "sugars",
        "protein", "dietary_fiber", "cholesterol", "sodium", "water"
    ]
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
    
    # Save processed data if output path provided
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_clean.to_csv(output_path, index=False)
        print(f"Processed {len(df_clean)} rows -> {output_path}")
    
    return df_clean


def process_all_food_datasets(
    raw_dir: str = "data/raw",
    processed_dir: str = "data/processed",
) -> pd.DataFrame:
    """Process all food dataset files and combine into single DataFrame.
    
    Args:
        raw_dir: Directory containing raw CSV files
        processed_dir: Directory to save processed files
        
    Returns:
        Combined DataFrame with all processed food data
    """
    raw_path = Path(raw_dir)
    processed_path = Path(processed_dir)
    processed_path.mkdir(parents=True, exist_ok=True)
    
    all_data = []
    
    # Process each group file
    for i in range(1, 6):
        input_file = raw_path / f"FOOD-DATA-GROUP{i}.csv"
        if input_file.exists():
            output_file = processed_path / f"food_data_group{i}_processed.csv"
            df = process_food_dataset(
                str(input_file),
                str(output_file),
                group_name=f"group{i}"
            )
            all_data.append(df)
            print(f"✓ Processed GROUP{i}: {len(df)} rows")
        else:
            print(f"⚠ File not found: {input_file}")
    
    # Combine all datasets
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined_output = processed_path / "food_data_combined_processed.csv"
        combined.to_csv(combined_output, index=False)
        print(f"\n✓ Combined dataset: {len(combined)} total rows -> {combined_output}")
        return combined
    else:
        print("⚠ No data files found to process")
        return pd.DataFrame()


def create_analytics_summary(df: pd.DataFrame, output_path: str) -> None:
    """Create summary statistics for analytics dashboard.
    
    Args:
        df: Processed food DataFrame
        output_path: Path to save summary JSON
    """
    import json
    
    summary = {
        "total_foods": len(df),
        "avg_calories": float(df["calories"].mean()) if "calories" in df.columns else 0,
        "avg_protein": float(df["protein"].mean()) if "protein" in df.columns else 0,
        "avg_fat": float(df["fat"].mean()) if "fat" in df.columns else 0,
        "avg_carbs": float(df["carbohydrates"].mean()) if "carbohydrates" in df.columns else 0,
        "categories": df["data_group"].value_counts().to_dict() if "data_group" in df.columns else {},
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"✓ Analytics summary saved -> {output_path}")


if __name__ == "__main__":
    # Process all food datasets
    base_dir = Path(__file__).parent.parent.parent.parent
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    
    combined_df = process_all_food_datasets(
        str(raw_dir),
        str(processed_dir)
    )
    
    if not combined_df.empty:
        # Create analytics summary
        summary_path = processed_dir / "food_analytics_summary.json"
        create_analytics_summary(combined_df, str(summary_path))
        print("\n✅ Food data processing complete!")

