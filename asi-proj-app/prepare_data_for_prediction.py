import numpy as np
import pandas as pd

def calculate_team_goals_features(home_team: str, away_team: str,
                                 n_matches=5, h2h_matches=10) -> dict:

    data = pd.read_csv('data/database/matches_results_separated.csv')

    def calculate_team_attacking_stats(df, team, n_matches=5):
        """Statystyki ofensywne i defensywne drużyny"""

        # Filtrowanie ostatnich meczów drużyny
        team_matches = df[
            (df['home_team'] == team) | (df['away_team'] == team)
            ].tail(n_matches)

        if len(team_matches) == 0:
            return {
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
            }

        goals_scored = goals_conceded = clean_sheets = failed_to_score = high_scoring = 0

        for _, match in team_matches.iterrows():
            is_home = match['home_team'] == team
            total_goals_in_match = match['full_time_score_home'] + match['full_time_score_away']

            if is_home:
                team_goals = match['full_time_score_home']
                opponent_goals = match['full_time_score_away']
            else:
                team_goals = match['full_time_score_away']
                opponent_goals = match['full_time_score_home']

            goals_scored += team_goals
            goals_conceded += opponent_goals

            if opponent_goals == 0:
                clean_sheets += 1
            if team_goals == 0:
                failed_to_score += 1
            if total_goals_in_match >= 3:
                high_scoring += 1

        matches_played = len(team_matches)
        return {
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
        }

    def calculate_h2h_goals_stats(df, home_team, away_team, n_matches=10):
        """Statystyki goli w meczach head-to-head"""

        # Pobieranie ostatnich meczów head-to-head
        h2h_matches = df[
            ((df['home_team'] == home_team) & (df['away_team'] == away_team)) |
            ((df['home_team'] == away_team) & (df['away_team'] == home_team))
            ].tail(n_matches)

        if len(h2h_matches) == 0:
            return {
                'h2h_avg_total_goals': 2.5,  # Liga average
                'h2h_over_2_5_rate': 0.5,
                'h2h_btts_rate': 0.5,
                'h2h_matches': 0
            }

        total_goals_list = []
        over_2_5_count = 0
        btts_count = 0

        for _, match in h2h_matches.iterrows():
            total_goals = match['full_time_score_home'] + match['full_time_score_away']
            total_goals_list.append(total_goals)

            if total_goals > 2.5:
                over_2_5_count += 1

            if match['full_time_score_home'] > 0 and match['full_time_score_away'] > 0:
                btts_count += 1

        matches_count = len(h2h_matches)
        return {
            'h2h_avg_total_goals': np.mean(total_goals_list),
            'h2h_over_2_5_rate': over_2_5_count / matches_count,
            'h2h_btts_rate': btts_count / matches_count,
            'h2h_matches': matches_count
        }

    # Obliczanie statystyk dla obu drużyn
    home_stats = calculate_team_attacking_stats(data, home_team, n_matches)
    away_stats = calculate_team_attacking_stats(data, away_team, n_matches)
    h2h_stats = calculate_h2h_goals_stats(data, home_team, away_team, h2h_matches)

    # Obliczanie średniej ligowej
    if 'league' in data.columns:
        # Znajdź ligę dla tych drużyn (zakładając że grają w tej samej lidze)
        home_league_matches = data[data['home_team'] == home_team]
        if len(home_league_matches) > 0 and 'league' in home_league_matches.columns:
            league = home_league_matches.iloc[0]['league']
            league_avg_goals = data[data['league'] == league][
                'total_goals'].mean() if 'total_goals' in data.columns else 2.5
        else:
            league_avg_goals = data['total_goals'].mean() if 'total_goals' in data.columns else 2.5
    else:
        league_avg_goals = data['total_goals'].mean() if 'total_goals' in data.columns else 2.5

    # Kombinowane cechy ofensywno-defensywne
    expected_goals_home = home_stats['avg_goals_scored']
    expected_goals_away = away_stats['avg_goals_scored']
    expected_total_goals = expected_goals_home + expected_goals_away

    defensive_strength_home = 1 / (home_stats['avg_goals_conceded'] + 0.1)
    defensive_strength_away = 1 / (away_stats['avg_goals_conceded'] + 0.1)

    attacking_advantage = home_stats['avg_goals_scored'] - away_stats['avg_goals_scored']
    high_scoring_tendency = (home_stats['high_scoring_rate'] + away_stats['high_scoring_rate']) / 2
    defensive_solidity = home_stats['clean_sheet_rate'] + away_stats['clean_sheet_rate']
    btts_likelihood = 1 - (home_stats['fail_to_score_rate'] + away_stats['fail_to_score_rate'])
    goals_vs_league_avg = expected_total_goals - league_avg_goals

    # Budowanie słownika wynikowego
    result = {
        'home_team': home_team,
        'away_team': away_team,

        # Statystyki drużyny domowej
        **{f'home_{key}_last{n_matches}': value for key, value in home_stats.items()},

        # Statystyki drużyny gości
        **{f'away_{key}_last{n_matches}': value for key, value in away_stats.items()},

        # Statystyki head-to-head
        **h2h_stats,

        # Kombinowane cechy
        'expected_goals_home': expected_goals_home,
        'expected_goals_away': expected_goals_away,
        'expected_total_goals': expected_total_goals,
        'defensive_strength_home': defensive_strength_home,
        'defensive_strength_away': defensive_strength_away,
        'attacking_advantage': attacking_advantage,
        'high_scoring_tendency': high_scoring_tendency,
        'defensive_solidity': defensive_solidity,
        'btts_likelihood': btts_likelihood,
        'league_avg_goals': league_avg_goals,
        'goals_vs_league_avg': goals_vs_league_avg
    }

    return result