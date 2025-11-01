'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

interface RiskAssessmentProps {
  userId: string;
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

export default function RiskAssessment({ userId }: RiskAssessmentProps) {
  const [loading, setLoading] = useState(true);
  const [riskData, setRiskData] = useState<RiskData | null>(null);

  useEffect(() => {
    fetchRiskData();
  }, [userId]);

  const fetchRiskData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/user/${userId}/risk-assessment`);
      setRiskData(response.data);
    } catch (error) {
      console.error('Error fetching risk data:', error);
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

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-[#10B981] bg-green-50 border-green-200';
      case 'moderate': return 'text-[#F59E0B] bg-yellow-50 border-yellow-200';
      case 'high': return 'text-[#EF4444] bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'low': return <CheckCircle className="w-12 h-12 sm:w-16 sm:h-16" />;
      case 'moderate': return <Info className="w-12 h-12 sm:w-16 sm:h-16" />;
      case 'high': return <AlertTriangle className="w-12 h-12 sm:w-16 sm:h-16" />;
      default: return <Info className="w-12 h-12 sm:w-16 sm:h-16" />;
    }
  };

  const getRiskMessage = (level: string) => {
    switch (level) {
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
      name: 'Gait Asymmetry',
      description: 'Measures left-right movement imbalance during walking and running',
      insight: 'Research shows that gait asymmetry greater than 10% significantly increases ACL injury risk due to uneven joint loading.'
    },
    load_management: {
      name: 'Training Load Management',
      description: 'Tracks sudden spikes in training volume or intensity',
      insight: 'Rapid increases in training load (>20% per week) are associated with higher injury rates due to inadequate tissue adaptation.'
    },
    impact: {
      name: 'Peak Impact Forces',
      description: 'Measures ground reaction forces during high-intensity movements',
      insight: 'Excessive impact forces (>4G) during landing and cutting maneuvers increase ACL strain and tear risk.'
    },
    cadence: {
      name: 'Step Cadence',
      description: 'Your step rate during running and dynamic activities',
      insight: 'Lower cadences (<170 steps/min) are linked to increased ground reaction forces and higher ACL stress.'
    },
    consistency: {
      name: 'Movement Consistency',
      description: 'Variability in your movement patterns day-to-day',
      insight: 'High variability suggests poor neuromuscular control, which is a key risk factor for non-contact ACL injuries.'
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Overall Risk Card */}
      <div className={`p-6 sm:p-8 lg:p-10 rounded-2xl border-2 shadow-lg ${getRiskColor(riskData.risk_level)}`}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6">
          <div className="flex-shrink-0">{getRiskIcon(riskData.risk_level)}</div>
          <div className="flex-1">
            <div className="text-xs sm:text-sm font-medium uppercase tracking-wide mb-1 sm:mb-2">
              ACL Injury Risk Level
            </div>
            <div className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-2 uppercase">
              {riskData.risk_level}
            </div>
            <p className="text-sm sm:text-base lg:text-lg opacity-90 leading-relaxed">
              {getRiskMessage(riskData.risk_level)}
            </p>
          </div>
          <div className="text-right self-end sm:self-auto">
            <div className="text-4xl sm:text-5xl lg:text-6xl font-bold">{riskData.overall_score.toFixed(1)}</div>
            <div className="text-xs sm:text-sm font-medium mt-1">Risk Score</div>
          </div>
        </div>
      </div>

      {/* Risk Factors Detailed Breakdown */}
      <div className="bg-white rounded-2xl shadow-md border border-gray-100 overflow-hidden">
        <div className="p-4 sm:p-6 lg:p-8 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-teal-50">
          <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">Detailed Risk Factor Analysis</h2>
          <p className="text-sm sm:text-base text-gray-600 mt-1 sm:mt-2">
            Based on biomechanical data from NCBI sports medicine research
          </p>
        </div>

        <div className="divide-y divide-gray-200">
          {Object.entries(riskData.factors).map(([key, value]) => {
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

                {/* Research Insight */}
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

      {/* NCBI Research Reference */}
      <div className="bg-gradient-to-r from-purple-50 via-blue-50 to-cyan-50 p-4 sm:p-6 lg:p-8 rounded-2xl border-2 border-purple-200 shadow-md">
        <h3 className="text-lg sm:text-xl font-bold text-purple-900 mb-2 sm:mb-3">
          🧬 Powered by NCBI Research
        </h3>
        <p className="text-sm sm:text-base text-purple-800 mb-3 sm:mb-4 leading-relaxed">
          This risk assessment model is trained on peer-reviewed research from the National Center 
          for Biotechnology Information (NCBI), including studies on ACL injury epidemiology, 
          biomechanics, and prevention strategies in football and other high-risk sports.
        </p>
        <div className="flex flex-wrap gap-2">
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            NCAA Football Data
          </span>
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            Biomechanical Analysis
          </span>
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            Gait Asymmetry Studies
          </span>
          <span className="px-3 py-1.5 bg-white rounded-full text-xs font-medium text-purple-900 shadow-sm">
            Neuromuscular Control
          </span>
        </div>
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <button
          onClick={fetchRiskData}
          className="px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-[#0066CC] to-[#0052A3] text-white text-sm sm:text-base font-semibold rounded-xl hover:from-[#0052A3] hover:to-[#003D7A] transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
        >
          Refresh Assessment
        </button>
        <p className="text-xs sm:text-sm text-gray-500 mt-2 sm:mt-3">
          Last updated: {new Date(riskData.timestamp).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
