'use client';

import { useState } from 'react';
import axios from 'axios';
import { Save, CheckCircle2, Calendar, Activity, Heart, Moon, Flame, TrendingUp } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ManualDataEntryProps {
  userId: string;
  onSaveSuccess?: () => void; // Callback to switch to dashboard tab
}

interface ManualData {
  date: string;
  steps: number | null;
  distance_km: number | null;
  calories: number | null;
  active_minutes: number | null;
  peak_minutes: number | null;
  resting_heart_rate: number | null;
  sleep_hours: number | null;
  sleep_efficiency: number | null;
}

export default function ManualDataEntry({ userId, onSaveSuccess }: ManualDataEntryProps) {
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [data, setData] = useState<ManualData>({
    date: new Date().toISOString().split('T')[0], // Today's date
    steps: null,
    distance_km: null,
    calories: null,
    active_minutes: null,
    peak_minutes: null,
    resting_heart_rate: null,
    sleep_hours: null,
    sleep_efficiency: null
  });

  const handleChange = (field: keyof ManualData, value: any) => {
    setData(prev => ({ ...prev, [field]: value }));
  };

  const saveData = async () => {
    setSaving(true);
    setSaved(false);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/manual-data/${userId}`, data);
      console.log('✅ Manual data saved:', response.data);
      setSaved(true);
      
      // Show success message briefly, then redirect to dashboard
      setTimeout(() => {
        setSaved(false);
        if (onSaveSuccess) {
          onSaveSuccess(); // Switch to dashboard tab
        }
      }, 1500); // Reduced from 2000ms to 1500ms
      
      // Reset form for next entry (but user will be on dashboard)
      setTimeout(() => {
        setData({
          date: new Date().toISOString().split('T')[0],
          steps: null,
          distance_km: null,
          calories: null,
          active_minutes: null,
          peak_minutes: null,
          resting_heart_rate: null,
          sleep_hours: null,
          sleep_efficiency: null
        });
      }, 2000);
    } catch (error: any) {
      console.error('❌ Error saving manual data:', error);
      console.error('Error details:', error.response?.data);
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
      alert(`Failed to save data: ${errorMsg}\n\nPlease check the console for details.`);
    } finally {
      setSaving(false);
    }
  };

  const isFormValid = () => {
    // At minimum, require date and steps
    return data.date && data.steps !== null && data.steps > 0;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-6 sm:p-8 rounded-2xl text-white shadow-xl">
        <div className="flex items-center mb-3">
          <Activity className="w-7 h-7 mr-3" />
          <h1 className="text-2xl sm:text-3xl font-bold">Manual Activity Data Entry</h1>
        </div>
        <p className="text-purple-100 text-sm sm:text-base">
          Enter your daily activity data from your wearable device (Whoop, Polar, etc.). 
          This data will be used for your personalized ACL risk assessment.
        </p>
      </div>

      {/* Info Notice */}
      <div className="bg-blue-50 border-2 border-blue-200 p-4 rounded-xl">
        <div className="flex items-start">
          <Activity className="w-5 h-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-1">How to Find Your Data</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>Whoop:</strong> Open app → Performance → Today's stats</li>
              <li>• <strong>Polar:</strong> Flow app → Activity → Daily data</li>
              <li>• <strong>Garmin:</strong> Connect app → My Day → Daily stats</li>
              <li>• <strong>Other devices:</strong> Check your device's companion app</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Date Selection */}
      <div className="bg-white p-6 rounded-2xl shadow-md border border-gray-100">
        <div className="flex items-center mb-4">
          <Calendar className="w-5 h-5 text-purple-600 mr-2" />
          <h2 className="text-xl font-bold text-gray-900">Date</h2>
        </div>
        <input
          type="date"
          value={data.date}
          max={new Date().toISOString().split('T')[0]} // Can't enter future dates
          onChange={(e) => handleChange('date', e.target.value)}
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-lg text-gray-900"
        />
        <p className="text-xs text-gray-500 mt-2">Select the date for this activity data</p>
      </div>

      {/* Activity Metrics */}
      <div className="bg-white p-6 rounded-2xl shadow-md border border-gray-100">
        <div className="flex items-center mb-4">
          <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
          <h2 className="text-xl font-bold text-gray-900">Activity Metrics</h2>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Steps (Required) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Steps <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="0"
              value={data.steps || ''}
              onChange={(e) => handleChange('steps', parseInt(e.target.value) || null)}
              placeholder="e.g., 10000"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-900"
            />
            <p className="text-xs text-gray-500 mt-1">Total steps for the day (required)</p>
          </div>

          {/* Distance */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Distance (km)
            </label>
            <input
              type="number"
              min="0"
              step="0.1"
              value={data.distance_km || ''}
              onChange={(e) => handleChange('distance_km', parseFloat(e.target.value) || null)}
              placeholder="e.g., 7.5"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-900"
            />
            <p className="text-xs text-gray-500 mt-1">Total distance traveled</p>
          </div>

          {/* Calories */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Calories Burned
            </label>
            <div className="flex items-center">
              <Flame className="w-4 h-4 text-orange-500 mr-2" />
              <input
                type="number"
                min="0"
                value={data.calories || ''}
                onChange={(e) => handleChange('calories', parseInt(e.target.value) || null)}
                placeholder="e.g., 2500"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-900"
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">Total calories burned</p>
          </div>

          {/* Active Minutes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Active Minutes
            </label>
            <input
              type="number"
              min="0"
              value={data.active_minutes || ''}
              onChange={(e) => handleChange('active_minutes', parseInt(e.target.value) || null)}
              placeholder="e.g., 60"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-900"
            />
            <p className="text-xs text-gray-500 mt-1">Total active/exercise minutes</p>
          </div>

          {/* Peak/Intense Minutes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Peak Intensity Minutes
            </label>
            <input
              type="number"
              min="0"
              value={data.peak_minutes || ''}
              onChange={(e) => handleChange('peak_minutes', parseInt(e.target.value) || null)}
              placeholder="e.g., 25"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-900"
            />
            <p className="text-xs text-gray-500 mt-1">High-intensity / cardio zone minutes</p>
          </div>
        </div>
      </div>

      {/* Heart & Recovery Metrics */}
      <div className="bg-white p-6 rounded-2xl shadow-md border border-gray-100">
        <div className="flex items-center mb-4">
          <Heart className="w-5 h-5 text-red-600 mr-2" />
          <h2 className="text-xl font-bold text-gray-900">Heart & Recovery</h2>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Resting Heart Rate */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Resting Heart Rate (bpm)
            </label>
            <input
              type="number"
              min="30"
              max="120"
              value={data.resting_heart_rate || ''}
              onChange={(e) => handleChange('resting_heart_rate', parseInt(e.target.value) || null)}
              placeholder="e.g., 65"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-900"
            />
            <p className="text-xs text-gray-500 mt-1">Avg resting HR (important for fatigue)</p>
          </div>

          {/* Sleep Hours */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sleep Duration (hours)
            </label>
            <div className="flex items-center">
              <Moon className="w-4 h-4 text-indigo-500 mr-2" />
              <input
                type="number"
                min="0"
                max="16"
                step="0.5"
                value={data.sleep_hours || ''}
                onChange={(e) => handleChange('sleep_hours', parseFloat(e.target.value) || null)}
                placeholder="e.g., 7.5"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-900"
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">Total hours slept last night</p>
          </div>

          {/* Sleep Efficiency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sleep Efficiency (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={data.sleep_efficiency || ''}
              onChange={(e) => handleChange('sleep_efficiency', parseInt(e.target.value) || null)}
              placeholder="e.g., 85"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-900"
            />
            <p className="text-xs text-gray-500 mt-1">Sleep quality percentage (if available)</p>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="sticky bottom-4 bg-white p-4 rounded-2xl shadow-lg border-2 border-purple-200">
        <button
          onClick={saveData}
          disabled={saving || !isFormValid()}
          className={`w-full py-4 rounded-xl font-semibold text-lg transition-all flex items-center justify-center space-x-2 ${
            saved 
              ? 'bg-green-600 text-white'
              : saving
              ? 'bg-gray-400 text-white cursor-not-allowed'
              : !isFormValid()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-md'
          }`}
        >
          {saved ? (
            <>
              <CheckCircle2 className="w-6 h-6" />
              <span>Data Saved Successfully!</span>
            </>
          ) : saving ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Saving...</span>
            </>
          ) : (
            <>
              <Save className="w-6 h-6" />
              <span>Save Activity Data</span>
            </>
          )}
        </button>
        {!isFormValid() && (
          <p className="text-center text-sm text-gray-500 mt-2">
            Please enter at least the date and steps count (marked with *)
          </p>
        )}
      </div>

      {/* Tips */}
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-l-4 border-yellow-500 p-4 rounded-r-xl">
        <h3 className="font-semibold text-yellow-900 mb-2">Tips for Best Results</h3>
        <ul className="text-sm text-yellow-800 space-y-1">
          <li>✓ Enter data daily for most accurate risk assessment</li>
          <li>✓ More metrics = better confidence score in your risk analysis</li>
          <li>✓ Resting HR and sleep are critical for fatigue detection</li>
          <li>✓ Peak minutes help track high-intensity training load</li>
        </ul>
      </div>
    </div>
  );
}
