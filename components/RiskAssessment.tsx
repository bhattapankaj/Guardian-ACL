'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RiskAssessmentProps {
  userId: string;
}

// ML Risk Assessment Response from /api/risk/realtime
interface MLRiskData {
  status: string;
  user_id: string;
  assessment_date: string;
  data_days: number;
  risk_score: number;
  risk_level: string;
  risk_color: string;
  risk_components: {
    asymmetry: number;
    cadence: number;
    load: number;
    fatigue: number;
    consistency: number;
  };
  current_metrics: {
    steps_today: number;
    heart_rate_avg: number | null;
    sleep_hours: number | null;
    distance_km: number;
  };
  recommendations: string[];
  analysis_details: {
    step_asymmetry: number;
    cadence_variance: number;
    load_spike: number;
    fatigue_score: number;
    consistency: number;
  };
}

export default function RiskAssessment({ userId }: RiskAssessmentProps) {
  const [loading, setLoading] = useState(true);
  const [riskData, setRiskData] = useState<MLRiskData | null>(null);

  useEffect(() => {
    fetchRiskData();
  }, [userId]);

  const fetchRiskData = async () => {
    setLoading(true);
    try {
      // Use NEW ML endpoint for real-time risk assessment
      const response = await axios.get(`${API_BASE_URL}/api/risk/realtime/${userId}`);
      setRiskData(response.data);
    } catch (error) {
      console.error('Error fetching ML risk data:', error);
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
    asymmetry: {
      name: 'Step Asymmetry',
      description: 'Measures gait imbalance detected from day-to-day step patterns',
      insight: `ML detected ${riskData.analysis_details.step_asymmetry.toFixed(1)}% step asymmetry. Research shows asymmetry >10% significantly increases ACL injury risk due to uneven joint loading.`
    },
    cadence: {
      name: 'Cadence Variance',
      description: 'Inconsistent pace detected from distance/steps ratio',
      insight: `ML detected ${riskData.analysis_details.cadence_variance.toFixed(1)}% cadence variance. High variance (>15%) suggests poor neuromuscular control, a key ACL risk factor.`
    },
    load: {
      name: 'Training Load Spike',
      description: 'Sudden changes in training volume week-over-week',
      insight: `ML detected ${riskData.analysis_details.load_spike.toFixed(1)}% load spike. Rapid increases (>30%) are associated with higher injury rates due to inadequate tissue adaptation.`
    },
    fatigue: {
      name: 'Fatigue Score',
      description: 'Recovery indicators from heart rate and sleep patterns',
      insight: `ML calculated ${riskData.analysis_details.fatigue_score.toFixed(1)}/100 fatigue score. Elevated fatigue reduces neuromuscular control and reaction time.`
    },
    consistency: {
      name: 'Activity Consistency',
      description: 'Training pattern regularity over the analysis period',
      insight: `ML detected ${riskData.analysis_details.consistency.toFixed(1)}% consistency. Low consistency suggests irregular training, which limits adaptation and increases injury risk.`
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Overall Risk Card */}
      <div className={`p-6 sm:p-8 lg:p-10 rounded-2xl border-2 shadow-lg ${getRiskColor(riskData.risk_color)}`}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6">
          <div className="flex-shrink-0">{getRiskIcon(riskData.risk_color)}</div>
          <div className="flex-1">
            <div className="text-xs sm:text-sm font-medium uppercase tracking-wide mb-1 sm:mb-2">
              🧠 Real-Time ML ACL Injury Risk
            </div>
            <div className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-2 uppercase">
              {riskData.risk_level}
            </div>
            <p className="text-sm sm:text-base lg:text-lg opacity-90 leading-relaxed">
              {getRiskMessage(riskData.risk_level)}
            </p>
            <p className="text-xs sm:text-sm opacity-75 mt-2">
              Analyzed {riskData.data_days} days of your Fitbit activity data
            </p>
          </div>
          <div className="text-right self-end sm:self-auto">
            <div className="text-4xl sm:text-5xl lg:text-6xl font-bold">{riskData.risk_score.toFixed(1)}</div>
            <div className="text-xs sm:text-sm font-medium mt-1">Risk Score</div>
          </div>
        </div>
      </div>

      {/* ML Recommendations */}
      {riskData.recommendations.length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border-l-4 border-[#0066CC] p-4 sm:p-6 rounded-r-2xl shadow-md">
          <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-3">
            💡 ML-Powered Recommendations
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
          <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">Detailed ML Risk Factor Analysis</h2>
          <p className="text-sm sm:text-base text-gray-600 mt-1 sm:mt-2">
            Machine learning model trained on biomechanical research
          </p>
        </div>

        <div className="divide-y divide-gray-200">
          {Object.entries(riskData.risk_components).map(([key, value]) => {
            const factor = factorDescriptions[key];
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

                {/* ML Insight */}
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

      {/* ML Model Information */}
      <div className="bg-gradient-to-r from-purple-50 via-blue-50 to-cyan-50 p-4 sm:p-6 lg:p-8 rounded-2xl border-2 border-purple-200 shadow-md">
        <h3 className="text-lg sm:text-xl font-bold text-purple-900 mb-2 sm:mb-3">
          🧬 Real Machine Learning Model
        </h3>
        <p className="text-sm sm:text-base text-purple-800 mb-3 sm:mb-4 leading-relaxed">
          This assessment uses a Gradient Boosting classifier trained on ACL injury research data. 
          The model analyzes 5 biomechanical risk factors extracted from your Fitbit activity patterns 
          to predict injury risk with sub-second response times.
        </p>
        <div className="flex flex-wrap gap-2">
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            Gradient Boosting ML
          </span>
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            Real Fitbit Data
          </span>
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            Feature Engineering
          </span>
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            {riskData.data_days} Days Analysis
          </span>
        </div>
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <button
          onClick={fetchRiskData}
          className="px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-[#0066CC] to-[#0052A3] text-white text-sm sm:text-base font-semibold rounded-xl hover:from-[#0052A3] hover:to-[#003D7A] transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
        >
          🔄 Refresh ML Assessment
        </button>
        <p className="text-xs sm:text-sm text-gray-500 mt-2 sm:mt-3">
          Last assessed: {new Date(riskData.assessment_date).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
