"""
File path: backend/scripts/train_initial_models.py
Purpose: Bootstrap script to train the initial ML ensemble model
         once enough labeled prediction data has accumulated (≥500 records).

Usage:
    cd backend
    python scripts/train_initial_models.py [--min-samples 500]

This script is typically run:
  - After 30+ days of live prediction generation
  - Or with artificially constructed training data for testing

Steps:
  1. Check FeatureStore for labeled sample count
  2. If sufficient: run ModelTrainer.train()
  3. Run ModelValidator.validate() on trained model
  4. If passes: register via ModelRegistry and save artifacts
  5. Print summary of model metrics
"""
import argparse
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Train initial ML ensemble model")
    parser.add_argument("--min-samples", type=int, default=500)
    parser.add_argument("--force", action="store_true", help="Train even if below min samples")
    args = parser.parse_args()

    logger.info("Checking feature store for training data...")
    # TODO: from ml.features.feature_store import FeatureStore
    # store = FeatureStore()
    # X, y = store.get_training_data(only_labeled=True)
    # logger.info(f"Found {len(y)} labeled samples")
    # if len(y) < args.min_samples and not args.force:
    #     logger.error(f"Insufficient samples ({len(y)} < {args.min_samples}). Use --force to override.")
    #     sys.exit(1)

    logger.info("Starting model training...")
    # TODO: from ml.training.trainer import ModelTrainer
    # trainer = ModelTrainer()
    # metrics = trainer.train()
    # logger.info(f"Training complete: {metrics}")

    logger.info("Script stub — implement after FeatureStore and ModelTrainer are complete.")


if __name__ == "__main__":
    main()
