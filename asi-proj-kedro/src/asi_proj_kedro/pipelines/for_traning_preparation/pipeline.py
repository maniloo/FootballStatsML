"""
This is a boilerplate pipeline 'for_traning_preparation'
generated using Kedro 0.19.12
"""

from kedro.pipeline import node, Pipeline, pipeline
from .nodes import prepare_goals_data, create_goals_features


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=prepare_goals_data,
            inputs="matches_results_separated",
            outputs="prepared_goals_data",
            name="prepare_goals_data_node"
        ),
        node(
            func=create_goals_features,
            inputs="prepared_goals_data",
            outputs="goals_features_data",
            name="create_goals_features_node"
        )
    ])
