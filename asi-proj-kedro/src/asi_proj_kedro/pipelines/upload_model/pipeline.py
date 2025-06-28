"""
This is a boilerplate pipeline 'upload_model'
generated using Kedro 0.19.12
"""

from kedro.pipeline import node, Pipeline, pipeline
from .nodes import upload_everything


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=upload_everything,
            inputs="trained_model",
            outputs="empty_output",
            name="upload_everything_node"
        )
    ])
