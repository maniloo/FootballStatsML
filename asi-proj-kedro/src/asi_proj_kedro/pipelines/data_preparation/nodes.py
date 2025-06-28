"""
This is a boilerplate pipeline 'data_preparation'
generated using Kedro 0.19.12
"""

import pandas as pd
import re
from typing import Dict, Any

from sqlalchemy import false


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    def to_snake_case(name):
        # Replace spaces and special characters with underscore
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        # Replace multiple spaces/special chars with single underscore
        s3 = re.sub(r'[^a-zA-Z0-9]', '_', s2)
        # Convert to lowercase and remove leading/trailing underscores
        return re.sub(r'_+', '_', s3).lower().strip('_')

    df_copy.columns = [to_snake_case(col) for col in df_copy.columns]

    return df_copy

def standardize_time_column(df: pd.DataFrame) -> pd.DataFrame:
    def round_time_to_nearest_15_minutes(time_str: str) -> str:
        if pd.isna(time_str):
            return ""
        try:
            time = pd.to_datetime(time_str, format='%H:%M')
            rounded_time = time.round('15min')
            return rounded_time.strftime('%H:%M')
        except ValueError:
            return ""

    if 'time' in df.columns:
        df['time'] = df['time'].apply(round_time_to_nearest_15_minutes)

    return df

def merge_datasets(df_initial: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
    df_merged = df_initial.merge(
        df_new,
        on='match_id',
        validate='1:1'
    )
    return df_merged


def split_match_statistics(df: pd.DataFrame) -> pd.DataFrame:
    stats_columns = [
        'attacks', 'attempts_on_goal', 'corners', 'dangerous_attacks',
        'fauls', 'free_kicks', 'goal_kicks', 'offsides', 'penalties',
        'possesion', 'red_cards', 'saves', 'shots_blocked',
        'shots_off_target', 'shots_on_target', 'substitutions',
        'throw_ins', 'treatments', 'yellow_cards'
    ]

    result_df = df.copy()

    for col in stats_columns:
        if col in df.columns:
            home_col = f"{col}_home"
            away_col = f"{col}_away"

            result_df[home_col] = df[col].apply(
                lambda x: split_stat_value(x)[0] if pd.notna(x) else None
            )
            result_df[away_col] = df[col].apply(
                lambda x: split_stat_value(x)[1] if pd.notna(x) else None
            )

            result_df = result_df.drop(columns=[col])

    return result_df


def split_stat_value(value: Any) -> tuple:
    if pd.isna(value):
        return (None, None)

    value_str = str(value)

    if ':' in value_str:
        parts = value_str.split(':')
    else:
        return (None, None)

    try:
        home = float(parts[0])
        if home.is_integer():
            home = int(home)
    except (ValueError, IndexError):
        home = parts[0] if len(parts) > 0 else None

    try:
        away = float(parts[1])
        if away.is_integer():
            away = int(away)
    except (ValueError, IndexError):
        away = parts[1] if len(parts) > 1 else None

    return (home, away)


def split_match_scores(df: pd.DataFrame) -> pd.DataFrame:
    score_columns = ['half_time_score', 'full_time_score']

    result_df = df.copy()

    for col in score_columns:
        if col in df.columns:
            home_col = f"{col}_home"
            away_col = f"{col}_away"

            result_df[home_col] = df[col].apply(
                lambda x: split_score(x)[0] if pd.notna(x) else None
            )
            result_df[away_col] = df[col].apply(
                lambda x: split_score(x)[1] if pd.notna(x) else None
            )

            result_df = result_df.drop(columns=[col])

    return result_df


def split_score(value: Any) -> tuple:
    if pd.isna(value):
        return (None, None)

    value_str = str(value)

    match = re.match(r'(\d+)\s*-\s*(\d+)', value_str)

    if match:
        home_score = int(match.group(1))
        away_score = int(match.group(2))
        return (home_score, away_score)
    else:
        return (None, None)
