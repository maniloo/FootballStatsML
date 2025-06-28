"""
This is a boilerplate pipeline 'model_training'
generated using Kedro 0.19.12
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import train_automl_model, train_goals_models


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=train_goals_models,
            inputs="goals_features_data",
            outputs="trained_model",
            name="train_goals_models_node",
        ),
    ])
