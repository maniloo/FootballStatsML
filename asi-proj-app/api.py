from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from autogluon.tabular import TabularPredictor
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from prepare_data_for_prediction import calculate_team_goals_features

app = FastAPI(title="ML Football STATS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    date: str  # ISO format

@app.get("/predict/match_statistics")
def predict_match_statistics(
    home_team: str = Query(..., description="Home team name"),
    away_team: str = Query(..., description="Away team name"),
    date: str = Query(..., description="Match date in ISO format")
):
    features = calculate_team_goals_features(home_team, away_team)

    single_row = pd.DataFrame([features])
    single_row["date"] = pd.to_datetime(date)

    home_goals_predictor = TabularPredictor.load('data/models/home_goals_model')
    home_goals_prediction = home_goals_predictor.predict(single_row)

    away_goals_predictor = TabularPredictor.load('data/models/away_goals_model')
    away_goals_prediction = away_goals_predictor.predict(single_row)

    btts_goals_predictor = TabularPredictor.load('data/models/btts')
    btts_prediction = btts_goals_predictor.predict(single_row)

    goals_classification_predictor = TabularPredictor.load('data/models/goals_classification')
    goals_classification_prediction = goals_classification_predictor.predict(single_row)

    over_2_5_predictor = TabularPredictor.load('data/models/over_2_5')
    over_2_5_prediction = over_2_5_predictor.predict(single_row)

    total_goals_regression_predictor = TabularPredictor.load('data/models/total_goals_regression')
    total_goals_prediction = total_goals_regression_predictor.predict(single_row)

    return {
        "predicted_home_goals": float(home_goals_prediction.iloc[0]),
        "predicted_away_goals": float(away_goals_prediction.iloc[0]),
        "predicted_btts": str(btts_prediction.iloc[0]),
        "predicted_goals_classification": str(goals_classification_prediction.iloc[0]),
        "predicted_over_2_5": str(over_2_5_prediction.iloc[0]),
        "predicted_total_goals": float(total_goals_prediction.iloc[0])
    }

@app.get("/available_teams")
def available_teams():
    df = pd.read_csv("data/database/matches_results_separated.csv")
    home_teams = df["home_team"].dropna().unique().tolist()
    away_teams = df["away_team"].dropna().unique().tolist()
    all_teams = list(set(home_teams + away_teams))
    return JSONResponse(content={"teams": all_teams})

# To extend for other models, add more endpoints or parameterize model selection.

