from __future__ import annotations

from typing import Literal, Tuple, List, Optional

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline

from .dataset_loader import train_test_split_df
from .preprocess_pipeline import build_preprocess_pipeline, infer_feature_types


def train_sklearn(
    df: pd.DataFrame,
    target: str,
    task: Literal["regression", "classification"] = "regression",
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[Pipeline, dict]:
    """Train a scikit-learn pipeline (preprocess + estimator).

    Returns (pipeline, metrics) where metrics contains basic train-set scores.
    """
    num, cat = infer_feature_types(df, target)
    pre = build_preprocess_pipeline(num, cat)
    X_train, X_test, y_train, y_test = train_test_split_df(
        df, target, test_size=test_size, random_state=random_state, stratify=(task == "classification")
    )

    if task == "classification":
        est = RandomForestClassifier(random_state=random_state)
    else:
        est = RandomForestRegressor(random_state=random_state)

    pipe = Pipeline(steps=[("pre", pre), ("model", est)])
    pipe.fit(X_train, y_train)
    train_score = pipe.score(X_train, y_train)
    test_score = pipe.score(X_test, y_test)
    return pipe, {"train_score": float(train_score), "test_score": float(test_score)}


def train_tensorflow(
    df: pd.DataFrame,
    target: str,
    task: Literal["regression", "classification"] = "regression",
    test_size: float = 0.2,
    random_state: int = 42,
    epochs: int = 10,
    batch_size: int = 32,
):
    """Train a simple TensorFlow Keras model with sklearn preprocessing.

    Returns (preprocessor, model). Requires TensorFlow installed.
    """
    import numpy as np
    import tensorflow as tf

    num, cat = infer_feature_types(df, target)
    pre = build_preprocess_pipeline(num, cat)
    X_train, X_test, y_train, y_test = train_test_split_df(
        df, target, test_size=test_size, random_state=random_state, stratify=(task == "classification")
    )

    # Fit preprocessor and transform to dense arrays
    X_train_t = pre.fit_transform(X_train)
    X_test_t = pre.transform(X_test)

    if task == "classification":
        y_train_arr = np.asarray(y_train)
        y_test_arr = np.asarray(y_test)
        num_classes = int(np.unique(y_train_arr).size)
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(X_train_t.shape[1],)),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(num_classes, activation="softmax" if num_classes > 2 else "sigmoid"),
        ])
        loss = "sparse_categorical_crossentropy" if num_classes > 2 else "binary_crossentropy"
        model.compile(optimizer="adam", loss=loss, metrics=["accuracy"])
        model.fit(X_train_t, y_train_arr, validation_data=(X_test_t, y_test_arr), epochs=epochs, batch_size=batch_size, verbose=0)
    else:
        y_train_arr = y_train.to_numpy()
        y_test_arr = y_test.to_numpy()
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(X_train_t.shape[1],)),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(1),
        ])
        model.compile(optimizer="adam", loss="mse", metrics=["mae", tf.keras.metrics.RootMeanSquaredError()])
        model.fit(X_train_t, y_train_arr, validation_data=(X_test_t, y_test_arr), epochs=epochs, batch_size=batch_size, verbose=0)

    return pre, model


# Convenience wrappers for supervised learning
def train_regression_model(
    df: pd.DataFrame,
    target: str,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[Pipeline, dict]:
    """Train a regression model with preprocessing and return (pipeline, metrics)."""
    return train_sklearn(
        df=df,
        target=target,
        task="regression",
        test_size=test_size,
        random_state=random_state,
    )


def train_classification_model(
    df: pd.DataFrame,
    target: str,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[Pipeline, dict]:
    """Train a classification model with preprocessing and return (pipeline, metrics)."""
    return train_sklearn(
        df=df,
        target=target,
        task="classification",
        test_size=test_size,
        random_state=random_state,
    )


# Unsupervised helpers
def _build_unsupervised_preprocessor(df: pd.DataFrame, target: Optional[str] = None):
    """Create a preprocessing pipeline for unsupervised models and transform X.

    Returns (work_df, preprocessor, X_transformed, feature_names)
    """
    work = df.copy()
    if target and target in work.columns:
        work = work.drop(columns=[target])
    # Use a dummy label name for inference utility
    num, cat = infer_feature_types(pd.concat([work, pd.Series(name="__t__")], axis=1), "__t__")
    pre = build_preprocess_pipeline(num, cat)
    X_t = pre.fit_transform(work)
    try:
        feature_names: List[str] = pre.get_feature_names_out().tolist()  # type: ignore[attr-defined]
    except Exception:
        feature_names = [f"f{i}" for i in range(getattr(X_t, "shape", [0, 0])[1])]
    return work, pre, X_t, feature_names


def train_cluster_model(
    df: pd.DataFrame,
    n_clusters: int = 3,
    target: Optional[str] = None,
    random_state: int = 42,
):
    """Train a KMeans clustering model; return (pipeline, labels, feature_names)."""
    work, pre, X_t, feature_names = _build_unsupervised_preprocessor(df, target)
    k = min(max(1, n_clusters), max(1, len(work)))
    est = KMeans(n_clusters=k, n_init="auto", random_state=random_state)
    est.fit(X_t)
    labels = est.labels_.tolist()
    pipe = Pipeline(steps=[("pre", pre), ("model", est)])
    return pipe, labels, feature_names


def train_anomaly_model(
    df: pd.DataFrame,
    contamination: float = 0.05,
    target: Optional[str] = None,
    random_state: int = 42,
):
    """Train an IsolationForest for anomaly detection.

    Returns (pipeline, predictions, scores, feature_names).
    Predictions: 1=inlier, -1=outlier. Lower scores indicate more anomalous.
    """
    work, pre, X_t, feature_names = _build_unsupervised_preprocessor(df, target)
    est = IsolationForest(contamination=contamination, random_state=random_state)
    est.fit(X_t)
    preds = est.predict(X_t).tolist()
    scores = est.decision_function(X_t).tolist()
    pipe = Pipeline(steps=[("pre", pre), ("model", est)])
    return pipe, preds, scores, feature_names


# Intentionally no additional wrappers or unsupervised helpers here; see earlier revision
