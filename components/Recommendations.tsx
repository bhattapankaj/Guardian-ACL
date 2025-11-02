'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Dumbbell, Heart, Activity, Clock, AlertCircle, CheckCircle2 } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RecommendationsProps {
  userId: string;
}

interface MLRiskData {
  recommendations: string[];
  risk_level: string;
  risk_components: {
    asymmetry: number;
    cadence: number;
    load: number;
    fatigue: number;
    consistency: number;
  };
}

export default function Recommendations({ userId }: RecommendationsProps) {
  const [loading, setLoading] = useState(true);
  const [mlRecommendations, setMlRecommendations] = useState<string[]>([]);
  const [riskLevel, setRiskLevel] = useState<string>('');
  const [riskComponents, setRiskComponents] = useState<any>(null);

  useEffect(() => {
    fetchRecommendations();
  }, [userId]);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      // Get ML recommendations from real-time endpoint
      const response = await axios.get<MLRiskData>(`${API_BASE_URL}/api/risk/realtime/${userId}`);
      setMlRecommendations(response.data.recommendations || []);
      setRiskLevel(response.data.risk_level);
      setRiskComponents(response.data.risk_components);
    } catch (error) {
      console.error('Error fetching ML recommendations:', error);
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

  const getRecommendationPriority = (rec: string): 'high' | 'medium' | 'low' => {
    const lower = rec.toLowerCase();
    if (lower.includes('high') || lower.includes('sudden') || lower.includes('immediately')) {
      return 'high';
    } else if (lower.includes('consider') || lower.includes('improve')) {
      return 'medium';
    }
    return 'low';
  };

  const getRiskColorClass = () => {
    switch (riskLevel.toLowerCase()) {
      case 'low': return 'from-green-500 to-teal-500';
      case 'moderate': return 'from-yellow-500 to-orange-500';
      case 'high': return 'from-red-500 to-pink-500';
      default: return 'from-blue-500 to-purple-500';
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className={`bg-gradient-to-r ${getRiskColorClass()} p-6 sm:p-8 lg:p-10 rounded-2xl text-white shadow-xl`}>
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-2">
          ML-Powered Prevention Plan
        </h1>
        <p className="text-white/90 text-sm sm:text-base lg:text-lg">
          Personalized recommendations based on your real Fitbit activity patterns
        </p>
        <div className="mt-4 sm:mt-6 flex flex-wrap items-center gap-3 sm:gap-4 text-xs sm:text-sm">
          <div className="flex items-center bg-white/20 px-3 py-2 rounded-lg backdrop-blur-sm">
            <CheckCircle2 className="w-4 h-4 mr-1.5" />
            <span>{mlRecommendations.length} Recommendations</span>
          </div>
          <div className="flex items-center bg-white/20 px-3 py-2 rounded-lg backdrop-blur-sm">
            <AlertCircle className="w-4 h-4 mr-1.5" />
            <span className="uppercase">{riskLevel} Risk Level</span>
          </div>
        </div>
      </div>

      {/* ML Recommendations */}
      {mlRecommendations.length > 0 ? (
        <div>
                  <h2 className="text-2xl sm:text-3xl font-bold mb-4 sm:mb-6 text-gray-900">
          Recommended Prevention Programs
        </h2>
          <div className="space-y-3 sm:space-y-4">
            {mlRecommendations.map((rec, index) => {
              const priority = getRecommendationPriority(rec);
              const isHigh = priority === 'high';
              
              return (
                <div
                  key={index}
                  className={`bg-white border-l-4 ${
                    isHigh ? 'border-[#EF4444]' : 'border-[#0066CC]'
                  } p-4 sm:p-6 rounded-r-2xl shadow-md hover:shadow-lg transition-all duration-300`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-2.5 rounded-lg ${
                      isHigh ? 'bg-red-100 text-[#EF4444]' : 'bg-blue-100 text-[#0066CC]'
                    } flex-shrink-0`}>
                      {isHigh ? (
                        <AlertCircle className="w-5 h-5 sm:w-6 sm:h-6" />
                      ) : (
                        <Activity className="w-5 h-5 sm:w-6 sm:h-6" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-semibold text-gray-500">
                          RECOMMENDATION #{index + 1}
                        </span>
                        {isHigh && (
                          <span className="flex items-center px-2 py-1 bg-red-100 text-[#EF4444] text-xs font-semibold rounded-full">
                            <AlertCircle className="w-3 h-3 mr-1" />
                            High Priority
                          </span>
                        )}
                      </div>
                      <p className="text-sm sm:text-base text-gray-800 leading-relaxed font-medium">
                        {rec}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-2xl">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                Great job! No critical issues detected.
              </h3>
              <p className="text-sm text-gray-700">
                Your movement patterns and training load look good. Continue with your current routine.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Resources Section */}
      <div className="bg-gradient-to-r from-green-50 via-teal-50 to-blue-50 p-4 sm:p-6 lg:p-8 rounded-2xl border-2 border-green-200 shadow-md">
        <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-3 sm:mb-4">
          Recommended Prevention Programs
        </h3>
        <div className="space-y-3 sm:space-y-4">
          <div className="bg-white p-4 sm:p-5 rounded-xl shadow-sm border border-green-100">
            <h4 className="font-semibold text-gray-900 text-sm sm:text-base">FIFA 11+ Warmup Program</h4>
            <p className="text-xs sm:text-sm text-gray-600 mt-1 sm:mt-2 leading-relaxed">
              Evidence-based neuromuscular training program shown to reduce ACL injuries by up to 50% 
              in soccer players. Includes running exercises, strength, plyometrics, and balance training.
            </p>
          </div>
          <div className="bg-white p-4 sm:p-5 rounded-xl shadow-sm border border-green-100">
            <h4 className="font-semibold text-gray-900 text-sm sm:text-base">PEP (Prevent Injury, Enhance Performance)</h4>
            <p className="text-xs sm:text-sm text-gray-600 mt-1 sm:mt-2 leading-relaxed">
              20-minute warmup program developed by Santa Monica Sports Medicine Foundation, 
              proven to decrease ACL injuries in female athletes by 88%.
            </p>
          </div>
          <div className="bg-white p-4 sm:p-5 rounded-xl shadow-sm border border-green-100">
            <h4 className="font-semibold text-gray-900 text-sm sm:text-base">Nordic Hamstring Curls</h4>
            <p className="text-xs sm:text-sm text-gray-600 mt-1 sm:mt-2 leading-relaxed">
              Strengthens hamstrings to improve hamstring-to-quadriceps ratio (H:Q), 
              a key protective factor against ACL injuries.
            </p>
          </div>
        </div>
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <button
          onClick={fetchRecommendations}
          className="px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-[#0066CC] to-[#0052A3] text-white text-sm sm:text-base font-semibold rounded-xl hover:from-[#0052A3] hover:to-[#003D7A] transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
        >
          Refresh Recommendations
        </button>
      </div>
    </div>
  );
}
