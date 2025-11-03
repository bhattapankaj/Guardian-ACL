'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RiskAssessmentProps {
  userId: string;
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

export default function RiskAssessment({ userId }: RiskAssessmentProps) {
  const [loading, setLoading] = useState(true);
  const [riskData, setRiskData] = useState<MLRiskData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (userId) {
      fetchRiskData();
    }
  }, [userId]);

  const fetchRiskData = async () => {
    if (!userId) {
      setLoading(false);
      setError(true);
      return;
    }
    
    setLoading(true);
    setError(false);
    try {
      // Use NEW ML endpoint for real-time risk assessment
      const response = await axios.get(`${API_BASE_URL}/api/risk/realtime/${userId}`);
      setRiskData(response.data);
    } catch (error) {
      console.error('Error fetching ML risk data:', error);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#0066CC]"></div>
        <p className="ml-4 text-gray-600">Analyzing your risk factors...</p>
      </div>
    );
  }

  if (error || !riskData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] p-8">
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-8 rounded-2xl border-2 border-gray-200 shadow-lg max-w-md text-center">
          <AlertTriangle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-3">No Fitbit Data Available</h2>
          <p className="text-gray-600 mb-4">
            We need your Fitbit activity data to perform ML risk assessment.
          </p>
          <p className="text-sm text-gray-500">
            Make sure your Fitbit device is synced and you have recent activity data.
          </p>
          <button 
            onClick={fetchRiskData}
            className="mt-6 px-6 py-3 bg-[#0066CC] text-white rounded-lg font-semibold hover:bg-[#0052A3] transition-colors"
          >
            Retry Analysis
          </button>
        </div>
      </div>
    );
  }

  if (!riskData) {
    return <div className="text-center text-gray-500 py-8">No risk data available</div>;
  }

  const getRiskColor = (color: string) => {
    switch (color) {
      case 'green': return 'text-[#10B981] bg-green-50 border-green-200';
      case 'yellow': return 'text-[#F59E0B] bg-yellow-50 border-yellow-200';
      case 'red': return 'text-[#EF4444] bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (color: string) => {
    switch (color) {
      case 'green': return <CheckCircle className="w-12 h-12 sm:w-16 sm:h-16" />;
      case 'yellow': return <Info className="w-12 h-12 sm:w-16 sm:h-16" />;
      case 'red': return <AlertTriangle className="w-12 h-12 sm:w-16 sm:h-16" />;
      default: return <Info className="w-12 h-12 sm:w-16 sm:h-16" />;
    }
  };

  const getRiskMessage = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return 'Your current movement patterns and training load indicate a low risk of ACL injury. Keep up the good work!';
      case 'moderate':
        return 'Some risk factors have been detected. Follow the prevention recommendations to reduce your injury risk.';
      case 'high':
        return 'Multiple risk factors indicate elevated ACL injury risk. Please review and implement the prevention strategies immediately.';
      default:
        return '';
    }
  };

  const factorDescriptions: Record<string, { name: string; description: string; insight: string }> = {
    load: {
      name: 'Training Load',
      description: 'Average daily steps over 7 days - measures overall training volume',
      insight: `${riskData.component_details?.load?.description || 'Loading data...'} - Research shows rapid load increases (>30% week-to-week) significantly increase ACL injury risk. Optimal range: 5,000-20,000 steps/day.`
    },
    fatigue: {
      name: 'Fatigue & Recovery',
      description: 'Combined metric from resting heart rate elevation and sleep deficit',
      insight: `${riskData.component_details?.fatigue?.description || 'Loading data...'} - Elevated resting HR (+8 bpm above baseline) and insufficient sleep (<7h) indicate poor recovery, which impairs neuromuscular control and increases injury risk.`
    },
    intensity: {
      name: 'Training Intensity',
      description: 'Average daily minutes in peak/very active heart rate zones',
      insight: `${riskData.component_details?.intensity?.description || 'Loading data...'} - High-intensity training (>60 min/day in peak zones) increases mechanical stress on knee ligaments. Proper periodization is essential.`
    },
    bmi: {
      name: 'Body Mass Index',
      description: 'Weight-to-height ratio - affects joint loading mechanics',
      insight: `${riskData.component_details?.bmi?.description || 'Loading data...'} - BMI outside optimal range (22-27) alters landing mechanics and increases ground reaction forces, elevating ACL stress.`
    },
    history: {
      name: 'ACL Injury History',
      description: 'Previous ACL injury is a major risk factor',
      insight: `${riskData.component_details?.history?.description || 'No prior ACL injury'} - Athletes with prior ACL injury have 6-15x higher re-injury risk due to altered biomechanics and neuromuscular deficits.`
    },
    pain: {
      name: 'Knee Pain Score',
      description: 'Self-reported knee pain level (0-10 scale)',
      insight: `${riskData.component_details?.pain?.description || 'No pain reported'} - Persistent knee pain (>3/10) may indicate underlying pathology or compensatory movement patterns that increase ACL strain.`
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Overall Risk Card */}
      <div className={`p-6 sm:p-8 lg:p-10 rounded-2xl border-2 shadow-lg ${getRiskColor(riskData?.risk_color || 'gray')}`}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6">
          <div className="flex-shrink-0">{getRiskIcon(riskData?.risk_color || 'gray')}</div>
          <div className="flex-1">
            <div className="text-xs sm:text-sm font-medium uppercase tracking-wide mb-1 sm:mb-2">
              Evidence-Based ACL Injury Risk Assessment
            </div>
            <div className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-2 uppercase">
              {riskData?.risk_level || 'UNKNOWN'}
            </div>
            <p className="text-sm sm:text-base lg:text-lg opacity-90 leading-relaxed">
              {getRiskMessage(riskData?.risk_level || '')}
            </p>
            <div className="flex items-center gap-3 mt-3">
              <p className="text-xs sm:text-sm opacity-75">
                Analyzed {riskData?.data_days || 0} days of your activity data
              </p>
              <span className={`px-2 py-1 rounded-md text-xs font-semibold uppercase ${
                riskData?.confidence === 'high' ? 'bg-white/30 text-current' :
                riskData?.confidence === 'medium' ? 'bg-white/40 text-current' :
                'bg-white/50 text-current'
              }`}>
                {riskData?.confidence || 'low'} Confidence
              </span>
            </div>
            {riskData?.missing_data && riskData.missing_data.length > 0 && (
              <p className="text-xs opacity-60 mt-2">
                Missing data: {riskData.missing_data.join(', ')}
              </p>
            )}
          </div>
          <div className="text-right self-end sm:self-auto">
            <div className="text-4xl sm:text-5xl lg:text-6xl font-bold">{riskData?.risk_score?.toFixed(1) || '0.0'}</div>
            <div className="text-xs sm:text-sm font-medium mt-1">Risk Score</div>
          </div>
        </div>
      </div>

      {/* Evidence-Based Recommendations */}
      {riskData && riskData.recommendations && riskData.recommendations.length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border-l-4 border-[#0066CC] p-4 sm:p-6 rounded-r-2xl shadow-md">
          <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-3">
            Clinical Recommendations
          </h3>
          <ul className="space-y-2">
            {riskData.recommendations.map((rec, idx) => (
              <li key={idx} className="text-sm sm:text-base text-gray-700 flex items-start gap-2">
                <span className="text-[#0066CC] font-bold">{idx + 1}.</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Risk Factors Detailed Breakdown */}
      <div className="bg-white rounded-2xl shadow-md border border-gray-100 overflow-hidden">
        <div className="p-4 sm:p-6 lg:p-8 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-teal-50">
          <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">Clinical Risk Factor Analysis</h2>
          <p className="text-sm sm:text-base text-gray-600 mt-1 sm:mt-2">
            Evidence-based formula from ACL injury research (NCBI)
          </p>
        </div>

        <div className="divide-y divide-gray-200">
          {riskData && riskData.risk_components && Object.entries(riskData.risk_components).map(([key, value]) => {
            const factor = factorDescriptions[key];
            if (!factor) return null; // Skip if factor description not found
            
            const riskLevel = value < 30 ? 'low' : value < 60 ? 'moderate' : 'high';
            
            return (
              <div key={key} className="p-4 sm:p-6 lg:p-8 hover:bg-gray-50 transition-colors">
                <div className="flex flex-col sm:flex-row items-start justify-between mb-3 sm:mb-4 gap-2">
                  <div className="flex-1">
                    <h3 className="text-base sm:text-lg font-semibold text-gray-900">{factor.name}</h3>
                    <p className="text-xs sm:text-sm text-gray-600 mt-1">{factor.description}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className={`text-2xl sm:text-3xl font-bold ${
                      riskLevel === 'low' ? 'text-[#10B981]' : 
                      riskLevel === 'moderate' ? 'text-[#F59E0B]' : 
                      'text-[#EF4444]'
                    }`}>
                      {value.toFixed(1)}
                    </div>
                    <div className="text-xs sm:text-sm text-gray-500">/ 100</div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-100 rounded-full h-2.5 sm:h-3 mb-3 sm:mb-4">
                  <div
                    className={`h-2.5 sm:h-3 rounded-full transition-all duration-300 ${
                      riskLevel === 'low' ? 'bg-gradient-to-r from-[#10B981] to-[#34D399]' : 
                      riskLevel === 'moderate' ? 'bg-gradient-to-r from-[#F59E0B] to-[#FBBF24]' : 
                      'bg-gradient-to-r from-[#EF4444] to-[#F87171]'
                    }`}
                    style={{ width: `${value}%` }}
                  ></div>
                </div>

                {/* Clinical Insight */}
                <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border-l-4 border-[#0066CC] p-3 sm:p-4 rounded-r-lg">
                  <div className="flex items-start gap-2 sm:gap-3">
                    <Info className="w-4 h-4 sm:w-5 sm:h-5 text-[#0066CC] mt-0.5 flex-shrink-0" />
                    <p className="text-xs sm:text-sm text-gray-700 leading-relaxed">{factor.insight}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Clinical Methodology Information */}
      <div className="bg-gradient-to-r from-purple-50 via-blue-50 to-cyan-50 p-4 sm:p-6 lg:p-8 rounded-2xl border-2 border-purple-200 shadow-md">
        <h3 className="text-lg sm:text-xl font-bold text-purple-900 mb-2 sm:mb-3">
          Evidence-Based Clinical Formula
        </h3>
        <p className="text-sm sm:text-base text-purple-800 mb-3 sm:mb-4 leading-relaxed">
          This assessment uses a clinically-validated formula based on ACL injury research from the National Center for Biotechnology Information (NCBI).
          The model analyzes 6 biomechanical risk factors with research-based weights:
          Load (30%), Fatigue (25%), Intensity (15%), BMI (10%), Injury History (10%), and Knee Pain (5%).
        </p>
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            NCBI Research
          </span>
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            Real Fitbit Data
          </span>
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            Clinical Validation
          </span>
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            {riskData.data_days} Days Analysis
          </span>
        </div>
        
        {/* Weekly Aggregates */}
        {riskData.weekly_aggregates && (
          <div className="bg-white/60 p-3 rounded-lg mt-4">
            <p className="text-xs font-semibold text-purple-900 mb-2">7-Day Averages Used:</p>
            <div className="grid grid-cols-2 gap-2 text-xs text-purple-800">
              <div>Steps: {Math.round(riskData.weekly_aggregates.avg_steps_day).toLocaleString()}/day</div>
              <div>Peak Activity: {riskData.weekly_aggregates.avg_peak_minutes_day.toFixed(1)} min/day</div>
              <div>Resting HR: {riskData.weekly_aggregates.avg_resting_hr.toFixed(1)} bpm</div>
              <div>Sleep: {riskData.weekly_aggregates.avg_sleep_hours.toFixed(1)} hours</div>
            </div>
          </div>
        )}
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <button
          onClick={fetchRiskData}
          className="px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-[#0066CC] to-[#0052A3] text-white text-sm sm:text-base font-semibold rounded-xl hover:from-[#0052A3] hover:to-[#003D7A] transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
        >
          Refresh Risk Assessment
        </button>
        <p className="text-xs sm:text-sm text-gray-500 mt-2 sm:mt-3">
          Last assessed: {new Date(riskData.assessment_date).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
