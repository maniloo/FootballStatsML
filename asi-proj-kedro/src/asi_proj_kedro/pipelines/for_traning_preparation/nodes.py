"""
This is a boilerplate pipeline 'for_traning_preparation'
generated using Kedro 0.19.12
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def prepare_goals_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Przygotowanie danych dla przewidywania liczby goli
    """
    expected_columns = ['date', 'home_team', 'away_team', 'full_time_score_home', 'full_time_score_away']
    data = raw_data.copy()
    data = data[expected_columns]

    # Sprawdź wymagane kolumny
    required_cols = ['full_time_score_home', 'full_time_score_home']
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Brakujące kolumny: {missing_cols}")

    data['home_goals'] = data['full_time_score_home']
    data['away_goals'] = data['full_time_score_away']

    # TARGET VARIABLES - różne warianty przewidywania goli

    # 1. Łączna liczba goli w meczu
    data['total_goals'] = data['home_goals'] + data['away_goals']

    # 2. Gole gospodarzy
    data['target_home_goals'] = data['home_goals']

    # 3. Gole gości
    data['target_away_goals'] = data['away_goals']

    # 4. Over/Under 2.5 gola (popularne w zakładach)
    data['over_2_5'] = (data['total_goals'] > 2.5).astype(int)

    # 5. Over/Under 1.5 gola
    data['over_1_5'] = (data['total_goals'] > 1.5).astype(int)

    # 6. Over/Under 3.5 gola
    data['over_3_5'] = (data['total_goals'] > 3.5).astype(int)

    # 7. Both Teams To Score (BTTS)
    data['btts'] = ((data['home_goals'] > 0) & (data['away_goals'] > 0)).astype(int)

    # 8. Kategorie goli (dla klasyfikacji)
    def categorize_goals(total):
        if total <= 1:
            return 'low'  # 0-1 goli
        elif total <= 3:
            return 'medium'  # 2-3 gole
        else:
            return 'high'  # 4+ goli

    data['goals_category'] = data['total_goals'].apply(categorize_goals)

    # Statystyki rozkładu goli
    logger.info(f"Średnia liczba goli: {data['total_goals'].mean():.2f}")
    logger.info(f"Rozkład kategorii: {data['goals_category'].value_counts().to_dict()}")
    logger.info(f"Over 2.5: {data['over_2_5'].mean():.2%}")
    logger.info(f"BTTS: {data['btts'].mean():.2%}")

    data.drop(columns=['full_time_score_home', 'full_time_score_away'], inplace=True)
    return data


def create_goals_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Tworzenie cech specyficznych dla przewidywania goli
    """
    df = data.copy()

    # ========== OFENSYWNE I DEFENSYWNE STATYSTYKI ==========

    def calculate_attacking_stats(df, team_col, n_matches=5):
        """Statystyki ofensywne drużyny"""
        attacking_stats = []

        for idx, row in df.iterrows():
            team = row[team_col]
            match_date = row.get('match_date', idx)

            # Ostatnie mecze tej drużyny
            if 'match_date' in df.columns:
                recent_matches = df[
                    ((df['home_team'] == team) | (df['away_team'] == team)) &
                    (df['match_date'] < match_date)
                    ].sort_values('match_date', ascending=False).head(n_matches)
            else:
                recent_matches = df[
                    ((df['home_team'] == team) | (df['away_team'] == team)) &
                    (df.index < idx)
                    ].tail(n_matches)

            if len(recent_matches) == 0:
                attacking_stats.append({
                    'goals_scored': 0,
                    'goals_conceded': 0,
                    'avg_goals_scored': 0,
                    'avg_goals_conceded': 0,
                    'matches_played': 0,
                    'clean_sheets': 0,
                    'failed_to_score': 0,
                    'high_scoring_games': 0,
                    'clean_sheet_rate': 0,
                    'fail_to_score_rate': 0,
                    'high_scoring_rate': 0
                })
                continue

            goals_scored = goals_conceded = clean_sheets = failed_to_score = high_scoring = 0

            for _, match in recent_matches.iterrows():
                is_home = match['home_team'] == team
                total_goals_in_match = match['home_goals'] + match['away_goals']

                if is_home:
                    team_goals = match['home_goals']
                    opponent_goals = match['away_goals']
                else:
                    team_goals = match['away_goals']
                    opponent_goals = match['home_goals']

                goals_scored += team_goals
                goals_conceded += opponent_goals

                if opponent_goals == 0:
                    clean_sheets += 1
                if team_goals == 0:
                    failed_to_score += 1
                if total_goals_in_match >= 3:
                    high_scoring += 1

            matches_played = len(recent_matches)
            attacking_stats.append({
                'goals_scored': goals_scored,
                'goals_conceded': goals_conceded,
                'avg_goals_scored': goals_scored / matches_played,
                'avg_goals_conceded': goals_conceded / matches_played,
                'matches_played': matches_played,
                'clean_sheets': clean_sheets,
                'failed_to_score': failed_to_score,
                'high_scoring_games': high_scoring,
                'clean_sheet_rate': clean_sheets / matches_played,
                'fail_to_score_rate': failed_to_score / matches_played,
                'high_scoring_rate': high_scoring / matches_played
            })

        return attacking_stats

    # Statystyki dla drużyny domowej
    home_stats = calculate_attacking_stats(df, 'home_team', n_matches=5)
    for key in home_stats[0].keys():
        df[f'home_{key}_last5'] = [stat[key] for stat in home_stats]

    # Statystyki dla drużyny gości
    away_stats = calculate_attacking_stats(df, 'away_team', n_matches=5)
    for key in away_stats[0].keys():
        df[f'away_{key}_last5'] = [stat[key] for stat in away_stats]

    # logs new created columns
    logger.info(f"Nowe kolumny ofensywne i defensywne: {df.columns.tolist()}")

    # ========== KOMBINOWANE CECHY OFENSYWNO-DEFENSYWNE ==========

    # Potencjał strzelecki meczu
    df['expected_goals_home'] = df['home_avg_goals_scored_last5']
    df['expected_goals_away'] = df['away_avg_goals_scored_last5']
    df['expected_total_goals'] = df['expected_goals_home'] + df['expected_goals_away']

    # Defensywna solidność
    df['defensive_strength_home'] = 1 / (df['home_avg_goals_conceded_last5'] + 0.1)
    df['defensive_strength_away'] = 1 / (df['away_avg_goals_conceded_last5'] + 0.1)

    # Różnica w sile ofensywnej
    df['attacking_advantage'] = df['home_avg_goals_scored_last5'] - df['away_avg_goals_scored_last5']

    # Prawdopodobieństwo wysokowydajnego meczu
    df['high_scoring_tendency'] = (df['home_high_scoring_rate_last5'] + df['away_high_scoring_rate_last5']) / 2

    # Solidność defensywna obu drużyn
    df['defensive_solidity'] = df['home_clean_sheet_rate_last5'] + df['away_clean_sheet_rate_last5']

    # Tendencja do bramek / brak bramek
    df['btts_likelihood'] = 1 - (df['home_fail_to_score_rate_last5'] + df['away_fail_to_score_rate_last5'])

    # ========== CECHY HISTORYCZNE HEAD-TO-HEAD ==========

    def calculate_goals_h2h(df, n_matches=10):
        """Statystyki goli w meczach head-to-head"""
        h2h_goals_stats = []

        for idx, row in df.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']
            match_date = row.get('match_date', idx)

            if 'match_date' in df.columns:
                h2h_matches = df[
                    (((df['home_team'] == home_team) & (df['away_team'] == away_team)) |
                     ((df['home_team'] == away_team) & (df['away_team'] == home_team))) &
                    (df['match_date'] < match_date)
                    ].sort_values('match_date', ascending=False).head(n_matches)
            else:
                h2h_matches = df[
                    (((df['home_team'] == home_team) & (df['away_team'] == away_team)) |
                     ((df['home_team'] == away_team) & (df['away_team'] == home_team))) &
                    (df.index < idx)
                    ].tail(n_matches)

            if len(h2h_matches) == 0:
                h2h_goals_stats.append({
                    'h2h_avg_total_goals': 2.5,  # Liga average
                    'h2h_over_2_5_rate': 0.5,
                    'h2h_btts_rate': 0.5,
                    'h2h_matches': 0
                })
                continue

            total_goals_list = []
            over_2_5_count = 0
            btts_count = 0

            for _, match in h2h_matches.iterrows():
                total_goals = match['home_goals'] + match['away_goals']
                total_goals_list.append(total_goals)

                if total_goals > 2.5:
                    over_2_5_count += 1

                if match['home_goals'] > 0 and match['away_goals'] > 0:
                    btts_count += 1

            matches_count = len(h2h_matches)
            h2h_goals_stats.append({
                'h2h_avg_total_goals': np.mean(total_goals_list),
                'h2h_over_2_5_rate': over_2_5_count / matches_count,
                'h2h_btts_rate': btts_count / matches_count,
                'h2h_matches': matches_count
            })

        return h2h_goals_stats

    h2h_data = calculate_goals_h2h(df)
    for key in h2h_data[0].keys():
        df[key] = [stat[key] for stat in h2h_data]

    # ========== CECHY LIGOWE I SEZONOWE ==========

    # Średnia ligowa (jeśli masz info o lidze)
    if 'league' in df.columns:
        league_averages = df.groupby('league')['total_goals'].mean().to_dict()
        df['league_avg_goals'] = df['league'].map(league_averages)
    else:
        df['league_avg_goals'] = df['total_goals'].mean()  # Ogólna średnia

    # Odchylenie od średniej ligowej
    df['goals_vs_league_avg'] = df['expected_total_goals'] - df['league_avg_goals']

    return df