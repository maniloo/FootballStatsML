"""
This is a boilerplate pipeline 'model_training'
generated using Kedro 0.19.12
"""
from typing import Dict, Any

import pandas as pd
from autogluon.tabular import TabularPredictor
import logging
logger = logging.getLogger(__name__)


def train_automl_model(data: pd.DataFrame) -> TabularPredictor:
    predictor = TabularPredictor(
        label="btts",
        path="data/08_reporting/automl_models",
        problem_type="binary",
        eval_metric="roc_auc",
    )

    predictor.fit(
        data,
        time_limit=3600,
        presets="best_quality",
        hyperparameters={
            'GBM': {},
            'CAT': {},
            'XGB': {},
            'RF': {},
            'XT': {}
        }
    )

    logger.info(f"Model trained. Leaderboard:")
    logger.info(predictor.leaderboard())

    return predictor

def train_goals_models(train_data: pd.DataFrame) -> Dict[str, TabularPredictor]:
    """
    Trenowanie różnych modeli dla przewidywania goli
    """
    models = {}
    time_per_model = 600

    # Przygotuj cechy (bez targetów)
    feature_columns = [col for col in train_data.columns
                       if not col.startswith(('target_', 'total_goals', 'over_', 'btts', 'goals_category'))
                       and col not in ['home_goals', 'away_goals', 'result']]

    logger.info(f"Używam {len(feature_columns)} cech do trenowania")

    # 1. MODEL REGRESYJNY - łączna liczba goli
    logger.info("Trenowanie modelu regresyjnego dla łącznej liczby goli...")
    # log columns used for training

    total_goals_regression_model_columns = feature_columns + ['total_goals']
    logger.info(f"Columns used for training total_goals_regression_model: {total_goals_regression_model_columns}")

    total_goals_regression_model = TabularPredictor(
        label='total_goals',
        path="data/08_reporting/total_goals_regression",
        problem_type='regression',
        eval_metric='root_mean_squared_error'
    ).fit(
        train_data[total_goals_regression_model_columns],
        time_limit=time_per_model,
        presets='high_quality',
        verbosity=2,
        hyperparameters={
            'GBM': {'num_boost_round': 300, 'learning_rate': 0.05, 'max_depth': 6},
            'XGB': {'n_estimators': 300, 'learning_rate': 0.05, 'max_depth': 6, 'subsample': 0.8},
            'RF': {'n_estimators': 200, 'max_depth': 10, 'min_samples_split': 5},
            'NN_TORCH': {'num_epochs': 100, 'learning_rate': 0.01, 'weight_decay': 0.01}
        },
        save_bag_folds=True
    )

    models['total_goals_regression'] = total_goals_regression_model
    logger.info(f"Model regresyjny dla łącznej liczby goli wytrenowany. Leaderboard:")
    logger.info(total_goals_regression_model.leaderboard())

    logger.info("Trenowanie modelu klasyfikacyjnego dla kategorii goli...")

    goals_classification_model = TabularPredictor(
        label='goals_category',
        path="data/08_reporting/goals_classification",
        problem_type='multiclass',
        eval_metric='accuracy'
    ).fit(
        train_data[feature_columns + ['goals_category']],
        time_limit=time_per_model,
        presets='high_quality',
        verbosity=2,
        hyperparameters={
            'GBM': {'num_boost_round': 350, 'learning_rate': 0.045, 'max_depth': 7},
            'CAT': {'iterations': 600, 'learning_rate': 0.03, 'depth': 8},
            'XGB': {'n_estimators': 350, 'learning_rate': 0.045, 'max_depth': 7},
        },
        save_bag_folds = True

    )

    models['goals_classification'] = goals_classification_model
    logger.info(f"Model klasyfikacyjny dla kategorii goli wytrenowany. Leaderboard:")
    logger.info(goals_classification_model.leaderboard())

    logger.info("Trenowanie modelu Over/Under 2.5...")
    over_2_5_model = TabularPredictor(
        label='over_2_5',
        path="data/08_reporting/over_2_5",
        problem_type='binary',
        eval_metric='roc_auc'
    ).fit(
        train_data[feature_columns + ['over_2_5']],
        time_limit=time_per_model,
        presets='high_quality',
        verbosity=2,
        hyperparameters={
            'GBM': {'num_boost_round': 400, 'learning_rate': 0.04, 'max_depth': 7},
            'CAT': {'iterations': 500, 'learning_rate': 0.04, 'depth': 8},
            'XGB': {'n_estimators': 400, 'learning_rate': 0.04, 'max_depth': 7, 'subsample': 0.85},
            'RF': {'n_estimators': 300, 'max_depth': 12, 'min_samples_split': 4},
            'NN_TORCH': {'num_epochs': 150, 'learning_rate': 0.008, 'weight_decay': 0.005}
        },
        save_bag_folds=True
    )

    models['over_2_5'] = over_2_5_model
    logger.info(f"Model Over/Under 2.5 wytrenowany. Leaderboard:")
    logger.info(over_2_5_model.leaderboard())

    logger.info("Trenowanie modelu BTTS...")
    btts_model = TabularPredictor(
        label='btts',
        path="data/08_reporting/btts",
        problem_type='binary',
        eval_metric='roc_auc'
    ).fit(
        train_data[feature_columns + ['btts']],
        time_limit=time_per_model,
        presets='high_quality',
        verbosity=2,
        hyperparameters={
            'GBM': {'num_boost_round': 400, 'learning_rate': 0.04, 'max_depth': 7},
            'CAT': {'iterations': 500, 'learning_rate': 0.04, 'depth': 8},
            'XGB': {'n_estimators': 400, 'learning_rate': 0.04, 'max_depth': 7, 'subsample': 0.85},
            'RF': {'n_estimators': 300, 'max_depth': 12, 'min_samples_split': 4},
            'NN_TORCH': {'num_epochs': 150, 'learning_rate': 0.008, 'weight_decay': 0.005}
        },
        save_bag_folds=True
    )

    models['btts'] = btts_model
    logger.info(f"Model BTTS wytrenowany. Leaderboard:")
    logger.info(btts_model.leaderboard())

    # 5. MODELE DLA GOLI OSOBNO
    logger.info("Trenowanie modeli dla goli osobno...")

    home_goals_model = TabularPredictor(
        label='home_goals',
        path="data/08_reporting/home_goals_model",
        problem_type='regression',
        eval_metric='root_mean_squared_error'
    ).fit(
        train_data[feature_columns + ['home_goals']],
        time_limit=time_per_model,
        presets='high_quality',
        verbosity=2,
        hyperparameters={
            'GBM': {'num_boost_round': 300, 'learning_rate': 0.05, 'max_depth': 6},
            'XGB': {'n_estimators': 300, 'learning_rate': 0.05, 'max_depth': 6, 'subsample': 0.8},
            'RF': {'n_estimators': 200, 'max_depth': 10, 'min_samples_split': 5},
            'NN_TORCH': {'num_epochs': 100, 'learning_rate': 0.01, 'weight_decay': 0.01}
        },
        save_bag_folds=True
    )
    models['home_goals'] = home_goals_model
    logger.info(f"Model dla home_goals wytrenowany. Leaderboard:")
    logger.info(home_goals_model.leaderboard())

    # Model for away_goals
    away_goals_model = TabularPredictor(
        label='away_goals',
        path="data/08_reporting/away_goals_model",
        problem_type='regression',
        eval_metric='root_mean_squared_error'
    ).fit(
        train_data[feature_columns + ['away_goals']],
        time_limit=time_per_model,
        presets='high_quality',
        verbosity=2,
        hyperparameters={
            'GBM': {'num_boost_round': 300, 'learning_rate': 0.05, 'max_depth': 6},
            'XGB': {'n_estimators': 300, 'learning_rate': 0.05, 'max_depth': 6, 'subsample': 0.8},
            'RF': {'n_estimators': 200, 'max_depth': 10, 'min_samples_split': 5},
            'NN_TORCH': {'num_epochs': 100, 'learning_rate': 0.01, 'weight_decay': 0.01}
        },
        save_bag_folds=True
    )
    models['away_goals'] = away_goals_model

    logger.info(f"Model Over/Under 2.5 wytrenowany. Leaderboard:")
    logger.info(over_2_5_model.leaderboard())
    logger.info(f"Model BTTS wytrenowany. Leaderboard:")
    logger.info(btts_model.leaderboard())
    logger.info(f"Model dla home_goals wytrenowany. Leaderboard:")
    logger.info(home_goals_model.leaderboard())
    logger.info(f"Model dla away_goals wytrenowany. Leaderboard:")
    logger.info(away_goals_model.leaderboard())
    logger.info(f"Model klasyfikacyjny dla kategorii goli wytrenowany. Leaderboard:")
    logger.info(goals_classification_model.leaderboard())
    logger.info(f"Model regresyjny dla łącznej liczby goli wytrenowany. Leaderboard:")
    logger.info(total_goals_regression_model.leaderboard())

    return models