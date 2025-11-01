'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Heart, Footprints, TrendingUp, AlertCircle } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

interface DashboardProps {
  userId: string;
}

interface ActivityData {
  date: string;
  steps: number;
  distance: number;
  calories: number;
  active_minutes: number;
  heart_rate_avg: number;
  cadence: number;
  asymmetry_score: number;
  load_score: number;
  peak_impact: number;
}

interface RiskData {
  overall_score: number;
  risk_level: string;
  factors: {
    asymmetry: number;
    load_management: number;
    impact: number;
    cadence: number;
    consistency: number;
  };
  timestamp: string;
}

export default function Dashboard({ userId }: DashboardProps) {
  const [loading, setLoading] = useState(true);
  const [activityData, setActivityData] = useState<ActivityData[]>([]);
  const [riskData, setRiskData] = useState<RiskData | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, [userId]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [activityResponse, riskResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/user/${userId}/activity?days=7`),
        axios.get(`${API_BASE_URL}/user/${userId}/risk-assessment`)
      ]);
      
      setActivityData(activityResponse.data.activities);
      setRiskData(riskResponse.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#0066CC]"></div>
      </div>
    );
  }

  const todayActivity = activityData[0];
  const weekAverage = activityData.reduce((sum, day) => sum + day.steps, 0) / activityData.length;

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-[#10B981] bg-green-50 border-green-200';
      case 'moderate': return 'text-[#F59E0B] bg-yellow-50 border-yellow-200';
      case 'high': return 'text-[#EF4444] bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Risk Score Card */}
      <div className={`p-4 sm:p-6 lg:p-8 rounded-2xl border-2 shadow-md ${getRiskColor(riskData?.risk_level || 'low')}`}>
        <div className="flex flex-col sm:flex-row items-start justify-between mb-4 sm:mb-6 gap-4">
          <div className="flex-1">
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold mb-1 sm:mb-2">ACL Injury Risk Score</h2>
            <p className="text-xs sm:text-sm opacity-75">Based on your last 7 days of activity</p>
          </div>
          <AlertCircle className="w-7 h-7 sm:w-8 sm:h-8 flex-shrink-0" />
        </div>
        
        <div className="flex items-end space-x-3 sm:space-x-4 mb-4">
          <div className="text-5xl sm:text-6xl lg:text-7xl font-bold">{riskData?.overall_score.toFixed(1)}</div>
          <div className="text-xl sm:text-2xl font-semibold mb-1 sm:mb-2">/ 100</div>
        </div>
        
        <div className="mt-4">
          <div className="text-base sm:text-lg font-semibold uppercase tracking-wide">
            {riskData?.risk_level} Risk
          </div>
        </div>
      </div>

      {/* Activity Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-shadow border border-gray-100">
          <div className="flex items-center justify-between mb-2 sm:mb-3">
            <span className="text-gray-600 text-xs sm:text-sm font-medium">Steps Today</span>
            <Footprints className="w-4 h-4 sm:w-5 sm:h-5 text-[#0066CC]" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-gray-900">
            {todayActivity?.steps.toLocaleString()}
          </div>
          <div className="text-xs sm:text-sm text-gray-500 mt-1">
            Avg: {Math.round(weekAverage).toLocaleString()}
          </div>
        </div>

        <div className="bg-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-shadow border border-gray-100">
          <div className="flex items-center justify-between mb-2 sm:mb-3">
            <span className="text-gray-600 text-xs sm:text-sm font-medium">Heart Rate</span>
            <Heart className="w-4 h-4 sm:w-5 sm:h-5 text-[#EF4444]" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-gray-900">
            {todayActivity?.heart_rate_avg}
          </div>
          <div className="text-xs sm:text-sm text-gray-500 mt-1">bpm average</div>
        </div>

        <div className="bg-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-shadow border border-gray-100">
          <div className="flex items-center justify-between mb-2 sm:mb-3">
            <span className="text-gray-600 text-xs sm:text-sm font-medium">Cadence</span>
            <Activity className="w-4 h-4 sm:w-5 sm:h-5 text-[#00CC88]" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-gray-900">
            {todayActivity?.cadence}
          </div>
          <div className="text-xs sm:text-sm text-gray-500 mt-1">steps/min</div>
        </div>

        <div className="bg-white p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-md hover:shadow-lg transition-shadow border border-gray-100">
          <div className="flex items-center justify-between mb-2 sm:mb-3">
            <span className="text-gray-600 text-xs sm:text-sm font-medium">Symmetry</span>
            <TrendingUp className="w-4 h-4 sm:w-5 sm:h-5 text-[#FF6B35]" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-gray-900">
            {((todayActivity?.asymmetry_score || 0) * 100).toFixed(0)}%
          </div>
          <div className="text-xs sm:text-sm text-gray-500 mt-1">gait balance</div>
        </div>
      </div>

      {/* Risk Factors Breakdown */}
      <div className="bg-white p-4 sm:p-6 lg:p-8 rounded-xl sm:rounded-2xl shadow-md border border-gray-100">
        <h3 className="text-base sm:text-lg font-semibold mb-4 sm:mb-6 text-gray-900">Risk Factor Breakdown</h3>
        <div className="space-y-3 sm:space-y-4">
          {riskData && Object.entries(riskData.factors).map(([key, value]) => (
            <div key={key}>
              <div className="flex justify-between text-xs sm:text-sm mb-2">
                <span className="font-medium capitalize text-gray-700">
                  {key.replace('_', ' ')}
                </span>
                <span className="font-semibold text-gray-900">{value.toFixed(1)}/100</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2 sm:h-2.5">
                <div
                  className={`h-2 sm:h-2.5 rounded-full transition-all ${
                    value < 30 ? 'bg-[#10B981]' : value < 60 ? 'bg-[#F59E0B]' : 'bg-[#EF4444]'
                  }`}
                  style={{ width: `${value}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

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
