import pandas as pd
from autogluon.tabular import TabularPredictor

from fetch_data_from_s3 import fetch_everything
from prepare_data_for_prediction import calculate_team_goals_features

def main():
    """Main function to fetch data from S3 and prepare the project."""
    destination_path = "data"
    fetch_everything(destination_path)

main()