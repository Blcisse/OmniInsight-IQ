from __future__ import annotations

from typing import Iterable, List, Tuple, Optional

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .dataset_loader import train_test_split_df


def infer_feature_types(df: pd.DataFrame, target: str) -> Tuple[List[str], List[str]]:
    """Infer numeric and categorical feature lists from a DataFrame.

    Excludes the target column. Numeric = number dtypes; Categorical = object/category.
    """
    features = [c for c in df.columns if c != target]
    num = [c for c in features if pd.api.types.is_numeric_dtype(df[c])]
    cat = [c for c in features if c not in num]
    return num, cat


def build_preprocess_pipeline(
    numeric_features: Iterable[str],
    categorical_features: Iterable[str],
) -> ColumnTransformer:
    """Create a ColumnTransformer that imputes and scales numeric features
    and imputes + one-hot-encodes categorical features.
    """
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, list(numeric_features)),
            ("cat", categorical_pipeline, list(categorical_features)),
        ]
    )
    return preprocessor


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply basic cleaning to a DataFrame.

    - Strips whitespace in object columns
    - Converts empty strings to NaN
    - Drops duplicate rows
    Returns a cleaned copy.
    """
    out = df.copy()
    obj_cols = [c for c in out.columns if pd.api.types.is_object_dtype(out[c])]
    for c in obj_cols:
        out[c] = out[c].astype(str).str.strip()
        out[c] = out[c].replace({"": pd.NA})
    out = out.drop_duplicates()
    return out


def encode_features(
    df: pd.DataFrame,
    target: Optional[str] = None,
    preprocessor: Optional[ColumnTransformer] = None,
):
    """Encode numeric/categorical features into a model-ready matrix.

    If `target` is provided, it is removed from the features and returned separately.
    If `preprocessor` is None, a new ColumnTransformer is created and fitted.
    Returns (X, y, preprocessor, feature_names)
    """
    work = df.copy()
    y = None
    if target is not None and target in work.columns:
        y = work[target]
        work = work.drop(columns=[target])

    # Infer features and (build &) fit preprocessor if needed
    num, cat = infer_feature_types(pd.concat([work, y], axis=1) if y is not None else work, target or "__none__")
    if preprocessor is None:
        preprocessor = build_preprocess_pipeline(num, cat)
        X = preprocessor.fit_transform(work)
    else:
        X = preprocessor.transform(work)

    # Try to extract feature names (best-effort)
    feature_names: List[str] = []
    try:
        feature_names = preprocessor.get_feature_names_out().tolist()  # type: ignore[attr-defined]
    except Exception:
        feature_names = [f"f{i}" for i in range(getattr(X, "shape", [0, 0])[1])]

    return X, y, preprocessor, feature_names


def split_data(
    df: pd.DataFrame,
    target: str,
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = False,
):
    """Convenience wrapper for train/test split on a DataFrame."""
    return train_test_split_df(df, target, test_size=test_size, random_state=random_state, stratify=stratify)
