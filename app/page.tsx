'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Image from 'next/image';
import { Activity, Heart, TrendingUp, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react';
import Dashboard from '@/components/Dashboard';
import RiskAssessment from '@/components/RiskAssessment';
import Recommendations from '@/components/Recommendations';
import ActivityChart from '@/components/ActivityChart';

const API_BASE_URL = 'http://localhost:8000';

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    // Check if user is already connected
    const savedUserId = localStorage.getItem('acl_guardian_user_id');
    if (savedUserId) {
      setUserId(savedUserId);
      setIsConnected(true);
    }
  }, []);

  const handleDemoConnection = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/demo/generate-sample-data`);
      const demoUserId = response.data.user_id;
      setUserId(demoUserId);
      setIsConnected(true);
      localStorage.setItem('acl_guardian_user_id', demoUserId);
    } catch (error) {
      console.error('Error connecting demo:', error);
      alert('Failed to connect. Make sure the backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setUserId(null);
    localStorage.removeItem('acl_guardian_user_id');
  };

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">
          {/* Hero Section */}
          <div className="text-center mb-12 sm:mb-16 lg:mb-20">
            <div className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-[#0066CC] to-[#0052A3] rounded-2xl mb-6 shadow-lg p-3 sm:p-4">
              <Image 
                src="/logo.png" 
                alt="ACL Guardian Logo" 
                width={80} 
                height={80}
                className="w-full h-full object-contain"
                priority
              />
            </div>
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-4 sm:mb-6 tracking-tight">
              ACL Guardian
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-gray-600 mb-6 sm:mb-8 font-medium">
              Turn your smartwatch into an injury prevention system
            </p>
            <p className="text-base sm:text-lg text-gray-500 max-w-2xl mx-auto leading-relaxed px-4">
              Connect to your Fitbit, Apple Watch, or Garmin to analyze movement patterns, 
              load management, and asymmetry to predict ACL injury risk.
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 mb-12 sm:mb-16 lg:mb-20 max-w-6xl mx-auto">
            <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-md hover:shadow-xl border border-gray-100 transition-all duration-300 hover:-translate-y-1">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-[#0066CC] to-[#4D9FEC] rounded-xl flex items-center justify-center mb-4 sm:mb-5">
                <Heart className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
              </div>
              <h3 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3 text-gray-900">Real-time Monitoring</h3>
              <p className="text-sm sm:text-base text-gray-600 leading-relaxed">
                Track step cadence, acceleration, asymmetry, and exertion patterns from your existing wearables.
              </p>
            </div>

            <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-md hover:shadow-xl border border-gray-100 transition-all duration-300 hover:-translate-y-1">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-[#00CC88] to-[#00A870] rounded-xl flex items-center justify-center mb-4 sm:mb-5">
                <TrendingUp className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
              </div>
              <h3 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3 text-gray-900">AI Risk Assessment</h3>
              <p className="text-sm sm:text-base text-gray-600 leading-relaxed">
                Machine learning model trained on NCBI sports medicine research predicts your ACL injury risk.
              </p>
            </div>

            <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-md hover:shadow-xl border border-gray-100 transition-all duration-300 hover:-translate-y-1 sm:col-span-2 lg:col-span-1">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-[#FF6B35] to-[#E54D1C] rounded-xl flex items-center justify-center mb-4 sm:mb-5">
                <CheckCircle className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
              </div>
              <h3 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3 text-gray-900">Prevention Tips</h3>
              <p className="text-sm sm:text-base text-gray-600 leading-relaxed">
                Get personalized warmups, load management plans, and rest schedules to stay injury-free.
              </p>
            </div>
          </div>

          {/* Stats Section */}
          <div className="bg-gradient-to-r from-[#0066CC] to-[#0052A3] rounded-2xl sm:rounded-3xl p-8 sm:p-10 lg:p-12 mb-12 sm:mb-16 lg:mb-20 text-white max-w-5xl mx-auto shadow-xl">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-6 sm:mb-8 text-center">Why ACL Prevention Matters</h2>
            <div className="grid sm:grid-cols-3 gap-6 sm:gap-8 text-center">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 sm:p-6">
                <div className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-2">14.4-18.0</div>
                <div className="text-sm sm:text-base text-blue-100">ACL injuries per 100,000 NCAA athlete exposures</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 sm:p-6">
                <div className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-2">2-8x</div>
                <div className="text-sm sm:text-base text-blue-100">Higher risk for female athletes</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 sm:p-6">
                <div className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-2">7-9 mo</div>
                <div className="text-sm sm:text-base text-blue-100">Average recovery time</div>
              </div>
            </div>
          </div>

          {/* CTA Section */}
          <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-4 sm:mb-6 text-gray-900">Ready to protect your knees?</h2>
            <p className="text-base sm:text-lg text-gray-600 mb-6 sm:mb-8 px-4">
              No new hardware needed. Just connect your existing smartwatch and get started.
            </p>
            <button
              onClick={handleDemoConnection}
              disabled={loading}
              className="inline-flex items-center px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-[#0066CC] to-[#0052A3] text-white text-base sm:text-lg font-semibold rounded-xl hover:from-[#0052A3] hover:to-[#003D7A] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                  Connecting...
                </>
              ) : (
                <>
                  Try Demo Now
                  <ArrowRight className="ml-2 w-5 h-5" />
                </>
              )}
            </button>
            <p className="text-xs sm:text-sm text-gray-500 mt-4">
              Demo mode uses sample data for demonstration
            </p>
          </div>

          {/* Louisiana Focus */}
          <div className="mt-12 sm:mt-16 max-w-4xl mx-auto bg-gradient-to-r from-yellow-50 to-orange-50 border-l-4 border-[#FF6B35] p-6 sm:p-8 rounded-r-2xl shadow-md">
            <div className="flex items-start">
              <AlertTriangle className="w-6 h-6 text-[#FF6B35] mr-3 sm:mr-4 mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2 sm:mb-3">
                  Built for Louisiana Athletes
                </h3>
                <p className="text-sm sm:text-base text-gray-700 leading-relaxed">
                  Louisiana's strong sports culture, especially in football and soccer, comes with high rates 
                  of ACL injuries among young athletes. ACL Guardian makes injury prevention accessible and 
                  affordable for all athletes, even in rural areas with limited access to sports medicine.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFBFC]">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50 backdrop-blur-sm bg-white/95">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-[#0066CC] to-[#0052A3] rounded-xl flex items-center justify-center shadow-md p-2">
                <Image 
                  src="/logo.png" 
                  alt="ACL Guardian Logo" 
                  width={48} 
                  height={48}
                  className="w-full h-full object-contain"
                />
              </div>
              <div>
                <h1 className="text-lg sm:text-xl font-bold text-gray-900">ACL Guardian</h1>
                <p className="text-xs sm:text-sm text-gray-500 hidden sm:block">Injury Prevention Dashboard</p>
              </div>
            </div>
            <button
              onClick={handleDisconnect}
              className="px-3 py-2 sm:px-4 sm:py-2 text-xs sm:text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors font-medium"
            >
              Disconnect
            </button>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-[60px] sm:top-[68px] z-40 backdrop-blur-sm bg-white/95">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 overflow-x-auto scrollbar-hide">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: Activity },
              { id: 'risk', label: 'Risk Assessment', icon: AlertTriangle },
              { id: 'recommendations', label: 'Prevention', icon: CheckCircle },
              { id: 'activity', label: 'Trends', icon: TrendingUp }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 sm:px-6 py-3 font-medium text-xs sm:text-sm transition-all border-b-2 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-[#0066CC] text-[#0066CC] bg-blue-50/50'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span className="hidden sm:inline">{tab.label}</span>
                <span className="sm:hidden">{tab.label.split(' ')[0]}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {activeTab === 'dashboard' && userId && <Dashboard userId={userId} />}
        {activeTab === 'risk' && userId && <RiskAssessment userId={userId} />}
        {activeTab === 'recommendations' && userId && <Recommendations userId={userId} />}
        {activeTab === 'activity' && userId && <ActivityChart userId={userId} />}
      </div>
    </div>
  );
}
