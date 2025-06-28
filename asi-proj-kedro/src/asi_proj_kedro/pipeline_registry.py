"""Project pipelines."""
from __future__ import annotations

from kedro.pipeline import Pipeline

from .pipelines import data_preparation, model_training, for_traning_preparation, upload_model


def register_pipelines() -> dict[str, Pipeline]:
    return {
        "data_processing": data_preparation.create_pipeline(),
        "model_training": model_training.create_pipeline(),
        "for_traning_preparation": for_traning_preparation.create_pipeline(),
        "upload_model": upload_model.create_pipeline()
    }
