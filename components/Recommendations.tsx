'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Dumbbell, Heart, Activity, Clock, AlertCircle, CheckCircle2 } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

interface RecommendationsProps {
  userId: string;
}

interface Recommendation {
  category: string;
  title: string;
  description: string;
  priority: string;
}

export default function Recommendations({ userId }: RecommendationsProps) {
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  useEffect(() => {
    fetchRecommendations();
  }, [userId]);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/user/${userId}/recommendations`);
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
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

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'strength':
      case 'biomechanics':
        return <Dumbbell className="w-5 h-5 sm:w-6 sm:h-6" />;
      case 'warmup':
      case 'technique':
        return <Activity className="w-5 h-5 sm:w-6 sm:h-6" />;
      case 'recovery':
      case 'training load':
        return <Clock className="w-5 h-5 sm:w-6 sm:h-6" />;
      case 'running form':
        return <Heart className="w-5 h-5 sm:w-6 sm:h-6" />;
      default:
        return <CheckCircle2 className="w-5 h-5 sm:w-6 sm:h-6" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'strength':
      case 'biomechanics':
        return 'bg-purple-100 text-purple-700 border-purple-200';
      case 'warmup':
      case 'technique':
        return 'bg-blue-100 text-[#0066CC] border-blue-200';
      case 'recovery':
      case 'training load':
        return 'bg-green-100 text-[#00CC88] border-green-200';
      case 'running form':
        return 'bg-orange-100 text-[#FF6B35] border-orange-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'high':
        return (
          <span className="flex items-center px-3 py-1.5 bg-red-100 text-[#EF4444] text-xs font-semibold rounded-full border border-red-200">
            <AlertCircle className="w-3 h-3 mr-1" />
            High Priority
          </span>
        );
      case 'medium':
        return (
          <span className="px-3 py-1.5 bg-yellow-100 text-[#F59E0B] text-xs font-semibold rounded-full border border-yellow-200">
            Medium Priority
          </span>
        );
      case 'low':
        return (
          <span className="px-3 py-1.5 bg-green-100 text-[#10B981] text-xs font-semibold rounded-full border border-green-200">
            Low Priority
          </span>
        );
      default:
        return null;
    }
  };

  const highPriority = recommendations.filter(r => r.priority === 'high');
  const mediumPriority = recommendations.filter(r => r.priority === 'medium');
  const lowPriority = recommendations.filter(r => r.priority === 'low');

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0066CC] via-[#0052A3] to-purple-600 p-6 sm:p-8 lg:p-10 rounded-2xl text-white shadow-xl">
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-2">Your Personalized Prevention Plan</h1>
        <p className="text-blue-100 text-sm sm:text-base lg:text-lg">
          Evidence-based recommendations to reduce your ACL injury risk
        </p>
        <div className="mt-4 sm:mt-6 flex flex-wrap items-center gap-3 sm:gap-4 text-xs sm:text-sm">
          <div className="flex items-center bg-white/10 px-3 py-2 rounded-lg backdrop-blur-sm">
            <CheckCircle2 className="w-4 h-4 mr-1.5" />
            <span>{recommendations.length} Recommendations</span>
          </div>
          <div className="flex items-center bg-white/10 px-3 py-2 rounded-lg backdrop-blur-sm">
            <AlertCircle className="w-4 h-4 mr-1.5" />
            <span>{highPriority.length} High Priority</span>
          </div>
        </div>
      </div>

      {/* High Priority Recommendations */}
      {highPriority.length > 0 && (
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3 sm:mb-4 flex items-center">
            <AlertCircle className="w-5 h-5 sm:w-6 sm:h-6 text-[#EF4444] mr-2" />
            High Priority Actions
          </h2>
          <div className="space-y-3 sm:space-y-4">
            {highPriority.map((rec, index) => (
              <div
                key={index}
                className="bg-white border-l-4 border-[#EF4444] p-4 sm:p-6 rounded-r-2xl shadow-md hover:shadow-lg transition-all duration-300"
              >
                <div className="flex flex-col sm:flex-row items-start justify-between gap-3 sm:gap-4 mb-3">
                  <div className="flex items-start gap-3 flex-1 w-full">
                    <div className={`p-2 sm:p-2.5 rounded-lg border ${getCategoryColor(rec.category)} flex-shrink-0`}>
                      {getCategoryIcon(rec.category)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 sm:mb-2">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-lg border ${getCategoryColor(rec.category)}`}>
                          {rec.category}
                        </span>
                      </div>
                      <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">{rec.title}</h3>
                      <p className="text-sm sm:text-base text-gray-700 leading-relaxed">{rec.description}</p>
                    </div>
                  </div>
                  <div className="flex-shrink-0 self-start">
                    {getPriorityBadge(rec.priority)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Medium Priority Recommendations */}
      {mediumPriority.length > 0 && (
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3 sm:mb-4">Recommended Actions</h2>
          <div className="grid sm:grid-cols-2 gap-3 sm:gap-4">
            {mediumPriority.map((rec, index) => (
              <div
                key={index}
                className="bg-white border border-gray-200 p-4 sm:p-6 rounded-2xl shadow-md hover:shadow-lg transition-all duration-300"
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className={`p-2 rounded-lg border ${getCategoryColor(rec.category)} flex-shrink-0`}>
                    {getCategoryIcon(rec.category)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-lg border ${getCategoryColor(rec.category)} mb-2`}>
                      {rec.category}
                    </span>
                    <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">{rec.title}</h3>
                    <p className="text-xs sm:text-sm text-gray-700 leading-relaxed">{rec.description}</p>
                  </div>
                  <div className="flex-shrink-0">
                    {getPriorityBadge(rec.priority)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Low Priority Recommendations */}
      {lowPriority.length > 0 && (
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3 sm:mb-4">Additional Suggestions</h2>
          <div className="grid sm:grid-cols-2 gap-3 sm:gap-4">
            {lowPriority.map((rec, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-gray-50 to-blue-50 border border-gray-200 p-4 sm:p-6 rounded-2xl shadow-sm hover:shadow-md transition-all duration-300"
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className={`p-2 rounded-lg border ${getCategoryColor(rec.category)} flex-shrink-0`}>
                    {getCategoryIcon(rec.category)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-lg border ${getCategoryColor(rec.category)} mb-2`}>
                      {rec.category}
                    </span>
                    <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">{rec.title}</h3>
                    <p className="text-xs sm:text-sm text-gray-700 leading-relaxed">{rec.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Resources Section */}
      <div className="bg-gradient-to-r from-green-50 via-teal-50 to-blue-50 p-4 sm:p-6 lg:p-8 rounded-2xl border-2 border-green-200 shadow-md">
        <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-3 sm:mb-4">
          🏃‍♂️ Recommended Prevention Programs
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
