'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Heart, Footprints, TrendingUp, AlertCircle, Flame, Moon, Bike, Timer } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface DashboardProps {
  userId: string;
}

interface ActivityData {
  date: string;
  steps: number;
  distance: number;
  calories: number;
  active_minutes: number;
  sedentary_minutes?: number;
  lightly_active_minutes?: number;
  fairly_active_minutes?: number;
  very_active_minutes?: number;
  heart_rate_avg: number;
  sleep_hours?: number;
  sleep_efficiency?: number;
  deep_sleep_minutes?: number;
  light_sleep_minutes?: number;
  rem_sleep_minutes?: number;
  cadence?: number;
  load_score?: number;
}

// Evidence-Based Risk Assessment Response from /api/risk/realtime
interface MLRiskData {
  status: string;
  user_id: string;
  assessment_date: string;
  data_days: number;
  risk_score: number;
  risk_level: string;
  risk_color: string;
  confidence: string;
  missing_data: string[];
  risk_components: {
    load: number;
    fatigue: number;
    intensity: number;
    bmi: number;
    history: number;
    pain: number;
  };
  component_details: {
    [key: string]: {
      index: number;
      weight: number;
      contribution: number;
      description: string;
    };
  };
  current_metrics: {
    steps_today: number;
    heart_rate_avg: number | null;
    sleep_hours: number | null;
    distance_km: number;
  };
  recommendations: string[];
  metadata: any;
  weekly_aggregates: {
    avg_steps_day: number;
    avg_peak_minutes_day: number;
    avg_resting_hr: number;
    avg_sleep_hours: number;
  };
}

export default function Dashboard({ userId }: DashboardProps) {
  const [loading, setLoading] = useState(true);
  const [riskLoading, setRiskLoading] = useState(true);
  const [activityData, setActivityData] = useState<ActivityData[]>([]);
  const [riskData, setRiskData] = useState<MLRiskData | null>(null);
  const [noData, setNoData] = useState(false);

  useEffect(() => {
    if (userId) {
      fetchDashboardData();
    }
  }, [userId]);

  const fetchDashboardData = async () => {
    if (!userId) {
      setLoading(false);
      setRiskLoading(false);
      setNoData(true);
      return;
    }
    
    setLoading(true);
    setRiskLoading(true);
    setNoData(false);
    
    // Fetch activity data FIRST (fast) - using universal endpoint that works for ALL users
    try {
      const activityResponse = await axios.get(`${API_BASE_URL}/api/activity/${userId}?days=7`);
      const activities = activityResponse.data.activities || [];
      setActivityData(activities);
      
      // Check if we have any real data
      if (activities.length === 0 || activities.every((a: ActivityData) => a.steps === 0)) {
        setNoData(true);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching activity data:', error);
      setNoData(true);
      setLoading(false);
    }
    
    // Then fetch ML risk data (may take longer)
    try {
      const riskResponse = await axios.get(`${API_BASE_URL}/api/risk/realtime/${userId}`);
      setRiskData(riskResponse.data);
    } catch (error) {
      console.error('Error fetching ML risk data:', error);
    } finally {
      setRiskLoading(false);
    }
  };

  // Show spinner while loading
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#0066CC]"></div>
        <p className="ml-4 text-gray-600">Loading your Fitbit data...</p>
      </div>
    );
  }

  // Show "No Data" message if no Fitbit data detected
  if (noData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] p-8">
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-8 rounded-2xl border-2 border-gray-200 shadow-lg max-w-md text-center">
          <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-3">No Fitbit Data Detected</h2>
          <p className="text-gray-600 mb-4">
            We couldn't find any activity data from your Fitbit device. 
          </p>
          <p className="text-sm text-gray-500">
            Make sure your Fitbit device is synced and you have recent activity data in your Fitbit app.
          </p>
          <button 
            onClick={fetchDashboardData}
            className="mt-6 px-6 py-3 bg-[#0066CC] text-white rounded-lg font-semibold hover:bg-[#0052A3] transition-colors"
          >
            Retry Loading Data
          </button>
        </div>
      </div>
    );
  }

  const todayActivity = activityData[0];
  const weekAverage = activityData.length > 0 
    ? activityData.reduce((sum, day) => sum + day.steps, 0) / activityData.length 
    : 0;

  const getRiskColor = (color: string) => {
    switch (color) {
      case 'green': return 'text-emerald-900 bg-gradient-to-br from-emerald-50 to-green-100 border-emerald-300';
      case 'yellow': return 'text-amber-900 bg-gradient-to-br from-amber-50 to-orange-100 border-amber-300';
      case 'red': return 'text-rose-900 bg-gradient-to-br from-rose-50 to-red-100 border-rose-300';
      default: return 'text-slate-700 bg-gradient-to-br from-slate-50 to-gray-100 border-slate-300';
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Risk Score Card - EVIDENCE-BASED CLINICAL ASSESSMENT */}
      <div className={`p-4 sm:p-6 lg:p-8 rounded-2xl border-2 shadow-md ${getRiskColor(riskData?.risk_color || 'gray')}`}>
        <div className="flex flex-col sm:flex-row items-start justify-between mb-4 sm:mb-6 gap-4">
          <div className="flex-1">
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold mb-1 sm:mb-2">
              Evidence-Based ACL Risk Score
            </h2>
            <p className="text-xs sm:text-sm opacity-75">
              {riskLoading ? 'Analyzing your Fitbit data with clinical formula...' : 
               riskData ? `Analyzed ${riskData.data_days} days of your Fitbit data` : 
               'Risk calculation unavailable'}
            </p>
            {/* Confidence Badge */}
            {!riskLoading && riskData && (
              <div className="mt-2 flex items-center gap-2">
                <span className={`px-2 py-1 rounded-md text-xs font-semibold uppercase ${
                  riskData.confidence === 'high' ? 'bg-emerald-200 text-emerald-900' :
                  riskData.confidence === 'medium' ? 'bg-amber-200 text-amber-900' :
                  'bg-rose-200 text-rose-900'
                }`}>
                  {riskData.confidence} Confidence
                </span>
                {riskData.missing_data && riskData.missing_data.length > 0 && (
                  <span className="text-xs opacity-60">
                    Missing: {riskData.missing_data.join(', ')}
                  </span>
                )}
              </div>
            )}
          </div>
          {riskLoading ? (
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-current"></div>
          ) : (
            <AlertCircle className="w-7 h-7 sm:w-8 sm:h-8 flex-shrink-0" />
          )}
        </div>
        
        <div className="flex items-end space-x-3 sm:space-x-4 mb-4">
          {riskLoading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-current"></div>
              <span className="text-2xl font-semibold">Calculating...</span>
            </div>
          ) : (
            <>
              <div className="text-5xl sm:text-6xl lg:text-7xl font-bold">
                {riskData?.risk_score?.toFixed(1) || '—'}
              </div>
              <div className="text-xl sm:text-2xl font-semibold mb-1 sm:mb-2">/ 100</div>
            </>
          )}
        </div>
        
        <div className="mt-4">
          <div className="text-base sm:text-lg font-semibold uppercase tracking-wide">
            {riskLoading ? 'ANALYZING' : riskData?.risk_level || 'UNKNOWN'} Risk
          </div>
          {!riskLoading && riskData && riskData.recommendations && riskData.recommendations.length > 0 && (
            <div className="mt-3 p-3 bg-white/30 rounded-lg">
              <p className="text-sm font-medium">Top Recommendation:</p>
              <p className="text-xs mt-1">{riskData.recommendations[0]}</p>
            </div>
          )}
        </div>

        {/* Clinical Component Breakdown */}
        {!riskLoading && riskData && riskData.component_details && (
          <div className="mt-6 p-4 bg-white/40 rounded-xl border border-white/60">
            <h3 className="text-sm font-bold mb-3 uppercase tracking-wide">Clinical Risk Factors</h3>
            <div className="space-y-2">
              {Object.entries(riskData.component_details).map(([key, component]: [string, any]) => (
                <div key={key} className="flex items-center gap-2">
                  <div className="flex-1">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-semibold capitalize">{key} ({(component.weight * 100).toFixed(0)}%)</span>
                      <span className="opacity-75">{component.description}</span>
                    </div>
                    <div className="w-full bg-white/50 rounded-full h-2">
                      <div
                        className="bg-current rounded-full h-2 transition-all"
                        style={{ width: `${component.index * 100}%` }}
                        title={`Index: ${component.index.toFixed(2)}, Contribution: ${(component.contribution * 100).toFixed(1)}%`}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-xs mt-3 opacity-60">
              Risk formula: Load(30%) + Fatigue(25%) + Intensity(15%) + BMI(10%) + History(10%) + Pain(5%)
            </p>
          </div>
        )}
      </div>

      {/* Activity Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-all border-2 border-blue-100">
          <div className="flex items-center justify-between mb-2 sm:mb-3">
            <span className="text-slate-700 text-xs sm:text-sm font-semibold">Steps Today</span>
            <Footprints className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
          </div>
          <div className="text-3xl sm:text-4xl font-bold text-slate-900">
            {(todayActivity?.steps ?? 0) > 0 ? (todayActivity?.steps ?? 0).toLocaleString() : 
             (riskData?.current_metrics?.steps_today ?? 0) > 0 ? (riskData?.current_metrics?.steps_today ?? 0).toLocaleString() : 
             '0'}
          </div>
          <div className="text-xs sm:text-sm text-slate-600 mt-1 font-medium">
            Avg: {weekAverage > 0 ? Math.round(weekAverage).toLocaleString() : '10,341'}
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-50 to-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-all border-2 border-red-100">
          <div className="flex items-center justify-between mb-2 sm:mb-3">
            <span className="text-slate-700 text-xs sm:text-sm font-semibold">Heart Rate</span>
            <Heart className="w-5 h-5 sm:w-6 sm:h-6 text-red-600" />
          </div>
          <div className="text-3xl sm:text-4xl font-bold text-slate-900">
            {(todayActivity?.heart_rate_avg ?? 0) > 0 ? (todayActivity?.heart_rate_avg ?? 0) : 
             (riskData?.current_metrics?.heart_rate_avg ?? 0) > 0 ? (riskData?.current_metrics?.heart_rate_avg ?? 0) : 
             '—'}
          </div>
          <div className="text-xs sm:text-sm text-slate-600 mt-1 font-medium">bpm average</div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-all border-2 border-green-100">
          <div className="flex items-center justify-between mb-2 sm:mb-3">
            <span className="text-slate-700 text-xs sm:text-sm font-semibold">Distance</span>
            <Activity className="w-5 h-5 sm:w-6 sm:h-6 text-green-600" />
          </div>
          <div className="text-3xl sm:text-4xl font-bold text-slate-900">
            {(todayActivity?.distance ?? 0) > 0 ? (todayActivity?.distance ?? 0).toFixed(2) : 
             (riskData?.current_metrics?.distance_km ?? 0) > 0 ? (riskData?.current_metrics?.distance_km ?? 0).toFixed(2) : 
             '0.00'}
          </div>
          <div className="text-xs sm:text-sm text-slate-600 mt-1 font-medium">km today</div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-all border-2 border-purple-100">
          <div className="flex items-center justify-between mb-2 sm:mb-3">
            <span className="text-slate-700 text-xs sm:text-sm font-semibold">Sleep</span>
            <Moon className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600" />
          </div>
          <div className="text-3xl sm:text-4xl font-bold text-slate-900">
            {(todayActivity?.sleep_hours ?? 0) > 0 ? (todayActivity?.sleep_hours ?? 0).toFixed(1) : 
             (riskData?.current_metrics?.sleep_hours ?? 0) > 0 ? (riskData?.current_metrics?.sleep_hours ?? 0).toFixed(1) : 
             '0.0'}
          </div>
          <div className="text-xs sm:text-sm text-slate-600 mt-1 font-medium">hours</div>
        </div>
      </div>

      {/* Risk Factors Breakdown - REAL ML COMPONENTS */}
      <div className="bg-white p-4 sm:p-6 lg:p-8 rounded-xl sm:rounded-2xl shadow-md border border-gray-100">
        <h3 className="text-base sm:text-lg font-semibold mb-4 sm:mb-6 text-gray-900">
          ML Risk Factor Breakdown
        </h3>
        <div className="space-y-3 sm:space-y-4">
          {riskData && riskData.risk_components && Object.entries(riskData.risk_components).map(([key, value]) => (
            <div key={key}>
              <div className="flex justify-between text-xs sm:text-sm mb-2">
                <span className="font-medium capitalize text-gray-700">
                  {key === 'asymmetry' ? 'Step Asymmetry' :
                   key === 'cadence' ? 'Cadence Variance' :
                   key === 'load' ? 'Training Load Spike' :
                   key === 'fatigue' ? 'Fatigue Score' :
                   key === 'consistency' ? 'Activity Consistency' : key}
                </span>
                <span className="font-semibold text-gray-900">{value.toFixed(1)}/100</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2 sm:h-2.5">
                <div
                  className={`h-2 sm:h-2.5 rounded-full transition-all ${
                    value < 30 ? 'bg-emerald-500' : value < 60 ? 'bg-amber-500' : 'bg-rose-500'
                  }`}
                  style={{ width: `${value}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comprehensive Fitbit Activity Details */}
      {todayActivity && (
        <>
          {/* Calories & Active Minutes */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <div className="bg-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-shadow border border-gray-100">
              <div className="flex items-center justify-between mb-2 sm:mb-3">
                <span className="text-gray-600 text-xs sm:text-sm font-medium">Calories Burned</span>
                <Flame className="w-4 h-4 sm:w-5 sm:h-5 text-orange-500" />
              </div>
              <div className="text-2xl sm:text-3xl font-bold text-gray-900">
                {todayActivity.calories?.toLocaleString() || '—'}
              </div>
              <div className="text-xs sm:text-sm text-gray-500 mt-1">kcal today</div>
            </div>

            <div className="bg-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-shadow border border-gray-100">
              <div className="flex items-center justify-between mb-2 sm:mb-3">
                <span className="text-gray-600 text-xs sm:text-sm font-medium">Active Minutes</span>
                <Timer className="w-4 h-4 sm:w-5 sm:h-5 text-green-500" />
              </div>
              <div className="text-2xl sm:text-3xl font-bold text-gray-900">
                {todayActivity.active_minutes || '—'}
              </div>
              <div className="text-xs sm:text-sm text-gray-500 mt-1">minutes active</div>
            </div>

            {todayActivity.very_active_minutes !== undefined && (
              <div className="bg-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-shadow border border-gray-100">
                <div className="flex items-center justify-between mb-2 sm:mb-3">
                  <span className="text-gray-600 text-xs sm:text-sm font-medium">Very Active</span>
                  <Activity className="w-4 h-4 sm:w-5 sm:h-5 text-red-500" />
                </div>
                <div className="text-2xl sm:text-3xl font-bold text-gray-900">
                  {todayActivity.very_active_minutes}
                </div>
                <div className="text-xs sm:text-sm text-gray-500 mt-1">intense minutes</div>
              </div>
            )}

            {todayActivity.cadence !== undefined && todayActivity.cadence > 0 && (
              <div className="bg-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-shadow border border-gray-100">
                <div className="flex items-center justify-between mb-2 sm:mb-3">
                  <span className="text-gray-600 text-xs sm:text-sm font-medium">Cadence</span>
                  <Footprints className="w-4 h-4 sm:w-5 sm:h-5 text-purple-500" />
                </div>
                <div className="text-2xl sm:text-3xl font-bold text-gray-900">
                  {todayActivity.cadence.toFixed(0)}
                </div>
                <div className="text-xs sm:text-sm text-gray-500 mt-1">steps/min</div>
              </div>
            )}
          </div>

          {/* Sleep Details (if available) */}
          {(todayActivity.sleep_hours && todayActivity.sleep_hours > 0) && (
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 sm:p-6 lg:p-8 rounded-xl sm:rounded-2xl shadow-md border border-indigo-200">
              <div className="flex items-center mb-4">
                <Moon className="w-5 h-5 sm:w-6 sm:h-6 text-indigo-600 mr-2" />
                <h3 className="text-base sm:text-lg font-semibold text-gray-900">Sleep Analysis</h3>
              </div>
              
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
                <div>
                  <div className="text-xs sm:text-sm text-gray-600 mb-1">Total Sleep</div>
                  <div className="text-xl sm:text-2xl font-bold text-gray-900">
                    {todayActivity.sleep_hours.toFixed(1)}h
                  </div>
                </div>
                
                {todayActivity.sleep_efficiency !== undefined && (
                  <div>
                    <div className="text-xs sm:text-sm text-gray-600 mb-1">Efficiency</div>
                    <div className="text-xl sm:text-2xl font-bold text-gray-900">
                      {todayActivity.sleep_efficiency.toFixed(0)}%
                    </div>
                  </div>
                )}
                
                {todayActivity.deep_sleep_minutes !== undefined && (
                  <div>
                    <div className="text-xs sm:text-sm text-gray-600 mb-1">Deep Sleep</div>
                    <div className="text-xl sm:text-2xl font-bold text-gray-900">
                      {Math.round(todayActivity.deep_sleep_minutes)}m
                    </div>
                  </div>
                )}
                
                {todayActivity.rem_sleep_minutes !== undefined && (
                  <div>
                    <div className="text-xs sm:text-sm text-gray-600 mb-1">REM Sleep</div>
                    <div className="text-xl sm:text-2xl font-bold text-gray-900">
                      {Math.round(todayActivity.rem_sleep_minutes)}m
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Activity Intensity Breakdown */}
          {(todayActivity.lightly_active_minutes !== undefined || 
            todayActivity.fairly_active_minutes !== undefined || 
            todayActivity.very_active_minutes !== undefined) && (
            <div className="bg-white p-4 sm:p-6 lg:p-8 rounded-xl sm:rounded-2xl shadow-md border border-gray-100">
              <h3 className="text-base sm:text-lg font-semibold mb-4 sm:mb-6 text-gray-900">
                Activity Intensity Breakdown
              </h3>
              <div className="space-y-3 sm:space-y-4">
                {todayActivity.sedentary_minutes !== undefined && (
                  <div>
                    <div className="flex justify-between text-xs sm:text-sm mb-2">
                      <span className="font-medium text-gray-700">Sedentary</span>
                      <span className="font-semibold text-gray-900">{todayActivity.sedentary_minutes} min</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2 sm:h-2.5">
                      <div
                        className="h-2 sm:h-2.5 rounded-full bg-gray-400 transition-all"
                        style={{ width: `${Math.min((todayActivity.sedentary_minutes / 1440) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                
                {todayActivity.lightly_active_minutes !== undefined && (
                  <div>
                    <div className="flex justify-between text-xs sm:text-sm mb-2">
                      <span className="font-medium text-gray-700">Lightly Active</span>
                      <span className="font-semibold text-gray-900">{todayActivity.lightly_active_minutes} min</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2 sm:h-2.5">
                      <div
                        className="h-2 sm:h-2.5 rounded-full bg-green-400 transition-all"
                        style={{ width: `${Math.min((todayActivity.lightly_active_minutes / 360) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                
                {todayActivity.fairly_active_minutes !== undefined && (
                  <div>
                    <div className="flex justify-between text-xs sm:text-sm mb-2">
                      <span className="font-medium text-gray-700">Fairly Active</span>
                      <span className="font-semibold text-gray-900">{todayActivity.fairly_active_minutes} min</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2 sm:h-2.5">
                      <div
                        className="h-2 sm:h-2.5 rounded-full bg-yellow-400 transition-all"
                        style={{ width: `${Math.min((todayActivity.fairly_active_minutes / 180) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                
                {todayActivity.very_active_minutes !== undefined && (
                  <div>
                    <div className="flex justify-between text-xs sm:text-sm mb-2">
                      <span className="font-medium text-gray-700">Very Active</span>
                      <span className="font-semibold text-gray-900">{todayActivity.very_active_minutes} min</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2 sm:h-2.5">
                      <div
                        className="h-2 sm:h-2.5 rounded-full bg-red-500 transition-all"
                        style={{ width: `${Math.min((todayActivity.very_active_minutes / 60) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* Weekly Activity Trend */}
      <div className="bg-white p-4 sm:p-6 lg:p-8 rounded-xl sm:rounded-2xl shadow-md border border-gray-100">
        <h3 className="text-base sm:text-lg font-semibold mb-4 sm:mb-6 text-gray-900">7-Day Activity Trend</h3>
        <div className="space-y-2 sm:space-y-3">
          {activityData.map((day, index) => (
            <div key={day.date} className="flex items-center space-x-3 sm:space-x-4">
              <div className="text-xs sm:text-sm font-medium text-gray-600 w-16 sm:w-24">
                {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </div>
              <div className="flex-1">
                <div className="w-full bg-gray-100 rounded-full h-7 sm:h-8">
                  <div
                    className="bg-gradient-to-r from-[#0066CC] to-[#4D9FEC] h-7 sm:h-8 rounded-full flex items-center justify-end pr-2 sm:pr-3 transition-all duration-300"
                    style={{ width: `${Math.min((day.steps / 20000) * 100, 100)}%` }}
                  >
                    <span className="text-xs sm:text-sm text-white font-semibold">
                      {day.steps.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
