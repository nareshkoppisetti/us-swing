"""
File path: backend/ml/models/registry.py
Purpose: ModelRegistry — tracks model versions, training dates, and performance.
         Manages loading the best available model for inference.
         Per SPEC Section 15.

Registry file: data/models/registry.json
Structure:
  {
    "models": [
      {
        "version": "v1.2.3",
        "trained_at": "2025-01-15T02:00:00",
        "accuracy_pct": 67.3,
        "calibration_error": 4.2,
        "training_samples": 8420,
        "feature_names": [...],
        "is_active": true
      }
    ]
  }
"""
import json
import logging
import os
logger = logging.getLogger("app")

REGISTRY_FILE = "data/models/registry.json"


class ModelRegistry:
    """Manages model versioning and selection."""

    def get_active_version(self) -> str | None:
        """Return the version string of the currently active model. TODO."""
        raise NotImplementedError

    def register(self, version: str, metrics: dict, feature_names: list) -> None:
        """
        Register a newly trained model version.
        Marks previous active model as inactive.
        TODO: Implement
        """
        raise NotImplementedError

    def list_versions(self) -> list:
        """List all registered model versions with metadata. TODO."""
        raise NotImplementedError

    def rollback(self, version: str) -> None:
        """Rollback to a specific model version. TODO."""
        raise NotImplementedError
