"""
This is a boilerplate pipeline 'data_preparation'
generated using Kedro 0.19.12
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import merge_datasets, standardize_column_names, split_match_statistics, split_match_scores, standardize_time_column


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
          func=standardize_column_names,
          inputs="matches_data",
          outputs="matches_data_standardized",
          name="standardize_matches_data_node"
        ),
        node(
            func=standardize_column_names,
            inputs="matches_statistics",
            outputs="matches_statistics_standardized",
            name="standardize_matches_statistics_node"
        ),
        node(
            func=standardize_time_column,
            inputs="matches_data_standardized",
            outputs="matches_data_time_standardized",
            name="standardize_matches_data_time_node"
        ),
        node(
            func=merge_datasets,
            inputs=["matches_data_time_standardized", "matches_statistics_standardized"],
            outputs="matches_data_merged",
            name="merge_datasets_node"
        ),
        node(
            func=split_match_statistics,
            inputs="matches_data_merged",
            outputs="matches_statistics_separated",
            name="split_match_statistics_node"
        ),
        node(
            func=split_match_scores,
            inputs="matches_statistics_separated",
            outputs="matches_results_separated",
            name="split_match_scores_node"
        )
    ])
