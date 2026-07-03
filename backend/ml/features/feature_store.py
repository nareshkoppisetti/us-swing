"""
File path: backend/ml/features/feature_store.py
Purpose: FeatureStore — persists and retrieves pre-computed feature vectors for training.
         Stores features as Parquet files at data/features/{symbol}/{date}.parquet.
         Per SPEC Section 15 (ML Architecture).

Why a feature store:
  - Training the ensemble model requires historical feature vectors + labels
  - Re-computing features from raw agent outputs is expensive
  - The feature store caches feature vectors after each prediction run
  - Weekly retraining job reads from the feature store

Structure:
  data/features/
    {SYMBOL}/
      {YYYY-MM-DD}.parquet   — one file per (symbol, date) with features + label
    index.parquet             — index of all stored (symbol, date) combos
"""
import logging
import os
logger = logging.getLogger("app")

FEATURES_DIR = "data/features"


class FeatureStore:
    """
    Read/write interface for the feature store.
    """

    def save(self, symbol: str, date: str, features: dict, label: int = None) -> str:
        """
        Save a feature vector to the store.
        
        Args:
            symbol: Ticker
            date: ISO date string (YYYY-MM-DD)
            features: Feature dict from FeatureBuilder.build()
            label: 1=Bullish, 0=Bearish, None if not yet resolved
        
        Returns: File path written
        TODO: Implement using pandas + pyarrow
        """
        raise NotImplementedError

    def load(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        """
        Load feature vectors for a symbol in a date range.
        Returns list of feature dicts with 'label' and 'date' added.
        TODO: Implement
        """
        raise NotImplementedError

    def update_labels(self, symbol: str, date: str, label: int) -> None:
        """
        Update the label for an existing feature record after prediction resolution.
        Called by PerformanceService.resolve_expired_predictions().
        TODO: Implement
        """
        raise NotImplementedError

    def get_training_data(self, min_date: str = None, only_labeled: bool = True) -> tuple:
        """
        Load all labeled feature records for model training.
        Returns (X: list[dict], y: list[int])
        TODO: Implement
        """
        raise NotImplementedError
