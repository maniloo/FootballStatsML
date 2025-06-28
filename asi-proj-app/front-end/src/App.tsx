import React, { useState, useEffect } from 'react';
import { Calendar, Users, TrendingUp, Target, BarChart3, Activity } from 'lucide-react';

interface PredictionResult {
  predicted_home_goals: number;
  predicted_away_goals: number;
  predicted_btts: string;
  predicted_goals_classification: string;
  predicted_over_2_5: string;
  predicted_total_goals: number;
}

interface ApiResponse {
  teams?: string[];
}

function App() {
  const [teams, setTeams] = useState<string[]>([]);
  const [homeTeam, setHomeTeam] = useState<string>('');
  const [awayTeam, setAwayTeam] = useState<string>('');
  const [date, setDate] = useState<string>('');
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [teamsLoading, setTeamsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetchTeams();
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    setDate(today);
  }, []);

  const fetchTeams = async () => {
    try {
      setTeamsLoading(true);
      const response = await fetch('http://localhost:8080/available_teams');
      const data: ApiResponse = await response.json();
      
      if (data.teams) {
        setTeams(data.teams);
      }
    } catch (err) {
      console.error('Failed to fetch teams:', err);
      setError('Failed to load teams. Please check if the API server is running.');
    } finally {
      setTeamsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!homeTeam || !awayTeam || !date) {
      setError('Please fill in all fields');
      return;
    }

    if (homeTeam === awayTeam) {
      setError('Home team and away team must be different');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const params = new URLSearchParams({
        home_team: homeTeam,
        away_team: awayTeam,
        date: date
      });
      
      const response = await fetch(`http://localhost:8080/predict/match_statistics?${params}`);
      
      if (!response.ok) {
        throw new Error('Prediction failed');
      }
      
      const data: PredictionResult = await response.json();
      setPrediction(data);
    } catch (err) {
      console.error('Prediction error:', err);
      setError('Failed to get prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <BarChart3 className="w-12 h-12 text-cyan-400 mr-3" />
            <h1 className="text-4xl font-bold text-white">
              ML Football Predictor
            </h1>
          </div>
          <p className="text-slate-300 text-lg">
            Advanced machine learning predictions for football match statistics
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          {/* Prediction Form */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8 mb-8 shadow-2xl">
            <h2 className="text-2xl font-semibold text-white mb-6 flex items-center">
              <Target className="w-6 h-6 text-emerald-400 mr-2" />
              Match Prediction Setup
            </h2>
            
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-6">
                <p className="text-red-400">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                {/* Home Team */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    <Users className="w-4 h-4 inline mr-1" />
                    Home Team
                  </label>
                  <select
                    value={homeTeam}
                    onChange={(e) => setHomeTeam(e.target.value)}
                    disabled={teamsLoading}
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all duration-200 disabled:opacity-50"
                  >
                    <option value="">
                      {teamsLoading ? 'Loading teams...' : 'Select home team'}
                    </option>
                    {teams.map((team) => (
                      <option key={team} value={team} className="bg-slate-700">
                        {team}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Away Team */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    <Users className="w-4 h-4 inline mr-1" />
                    Away Team
                  </label>
                  <select
                    value={awayTeam}
                    onChange={(e) => setAwayTeam(e.target.value)}
                    disabled={teamsLoading}
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all duration-200 disabled:opacity-50"
                  >
                    <option value="">
                      {teamsLoading ? 'Loading teams...' : 'Select away team'}
                    </option>
                    {teams.map((team) => (
                      <option key={team} value={team} className="bg-slate-700">
                        {team}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Date */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Match Date
                </label>
                <input
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all duration-200"
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || teamsLoading}
                className="w-full bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-600 hover:to-emerald-600 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-4 px-6 rounded-lg transition-all duration-200 transform hover:scale-[1.02] disabled:hover:scale-100 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <Activity className="animate-spin w-5 h-5 mr-2" />
                    Generating Prediction...
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-5 h-5 mr-2" />
                    Predict Match Statistics
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Prediction Results */}
          {prediction && (
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8 shadow-2xl">
              <h2 className="text-2xl font-semibold text-white mb-6 flex items-center">
                <BarChart3 className="w-6 h-6 text-emerald-400 mr-2" />
                Prediction Results
              </h2>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Goals Prediction */}
                <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-blue-300 mb-4">Expected Goals</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">Home:</span>
                      <span className="text-xl font-bold text-blue-400">
                        {prediction.predicted_home_goals.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">Away:</span>
                      <span className="text-xl font-bold text-cyan-400">
                        {prediction.predicted_away_goals.toFixed(1)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Total Goals */}
                <div className="bg-gradient-to-br from-emerald-500/10 to-green-500/10 border border-emerald-500/20 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-emerald-300 mb-4">Total Goals</h3>
                  <div className="space-y-3">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-emerald-400 mb-2">
                        {prediction.predicted_total_goals.toFixed(1)}
                      </div>
                      <div className="text-sm text-slate-300">
                        {prediction.predicted_goals_classification}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Market Predictions */}
                <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-purple-300 mb-4">Market Predictions</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">Over 2.5:</span>
                      <span className={`font-bold ${
                        prediction.predicted_over_2_5 === 'Yes' 
                          ? 'text-green-400' 
                          : 'text-red-400'
                      }`}>
                        {prediction.predicted_over_2_5}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">BTTS:</span>
                      <span className={`font-bold ${
                        prediction.predicted_btts === 'Yes' 
                          ? 'text-green-400' 
                          : 'text-red-400'
                      }`}>
                        {prediction.predicted_btts}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-slate-700/30 rounded-lg border border-slate-600/50">
                <p className="text-sm text-slate-400 text-center">
                  <Activity className="w-4 h-4 inline mr-1" />
                  Predictions generated using advanced machine learning algorithms
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;