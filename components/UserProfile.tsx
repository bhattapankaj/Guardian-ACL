'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { User, Activity, AlertCircle, Save, CheckCircle2 } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UserProfileProps {
  userId: string;
}

interface ProfileData {
  height_cm: number | null;
  sex: string;
  age: number | null;
  sport: string;
  limb_dominance: string;
  acl_history_flag: boolean;
  acl_injury_date: string | null;
  knee_pain_score: number;
  rehab_status: string;
  weight_kg: number | null;
}

export default function UserProfile({ userId }: UserProfileProps) {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [profile, setProfile] = useState<ProfileData>({
    height_cm: null,
    sex: 'M',
    age: null,
    sport: 'none',
    limb_dominance: 'right',
    acl_history_flag: false,
    acl_injury_date: null,
    knee_pain_score: 0,
    rehab_status: 'none',
    weight_kg: null
  });

  const saveProfile = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await axios.post(`${API_BASE_URL}/api/user/${userId}/profile`, profile);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Failed to save profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof ProfileData, value: any) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 sm:p-8 rounded-2xl text-white shadow-xl">
        <div className="flex items-center mb-3">
          <User className="w-7 h-7 mr-3" />
          <h1 className="text-2xl sm:text-3xl font-bold">Your Health Profile</h1>
        </div>
        <p className="text-blue-100 text-sm sm:text-base">
          Complete your profile for more accurate ACL injury risk assessment. 
          All information is confidential and used only for personalized risk calculation.
        </p>
      </div>

      {/* Important Notice */}
      <div className="bg-yellow-50 border-2 border-yellow-200 p-4 rounded-xl">
        <div className="flex items-start">
          <AlertCircle className="w-5 h-5 text-yellow-600 mr-3 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-yellow-900 mb-1">Why We Need This Information</h3>
            <p className="text-sm text-yellow-800">
              Research shows that factors like sex, BMI, sport type, and ACL injury history 
              significantly affect injury risk. Fitbit alone cannot provide this critical data.
            </p>
          </div>
        </div>
      </div>

      {/* Basic Information */}
      <div className="bg-white p-6 rounded-2xl shadow-md border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <Activity className="w-5 h-5 mr-2 text-blue-600" />
          Basic Information
        </h2>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Sex */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sex <span className="text-red-500">*</span>
            </label>
            <select
              value={profile.sex}
              onChange={(e) => handleChange('sex', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="Other">Other/Prefer not to say</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">Female athletes have 3-8x higher ACL risk</p>
          </div>

          {/* Age */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Age <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={profile.age || ''}
              onChange={(e) => handleChange('age', parseInt(e.target.value) || null)}
              placeholder="25"
              min="10"
              max="100"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Height */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Height (cm) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={profile.height_cm || ''}
              onChange={(e) => handleChange('height_cm', parseFloat(e.target.value) || null)}
              placeholder="170"
              min="100"
              max="250"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Used for BMI calculation</p>
          </div>

          {/* Weight */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Weight (kg) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={profile.weight_kg || ''}
              onChange={(e) => handleChange('weight_kg', parseFloat(e.target.value) || null)}
              placeholder="70"
              min="30"
              max="200"
              step="0.1"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Can also sync from Fitbit</p>
          </div>
        </div>
      </div>

      {/* Sport & Activity */}
      <div className="bg-white p-6 rounded-2xl shadow-md border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Sport & Activity</h2>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Primary Sport */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Primary Sport/Activity <span className="text-red-500">*</span>
            </label>
            <select
              value={profile.sport}
              onChange={(e) => handleChange('sport', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="none">None / General Fitness</option>
              <option value="football">Football</option>
              <option value="soccer">Soccer</option>
              <option value="basketball">Basketball</option>
              <option value="running">Running</option>
              <option value="cycling">Cycling</option>
              <option value="tennis">Tennis</option>
              <option value="volleyball">Volleyball</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">Different sports have different ACL injury rates</p>
          </div>

          {/* Limb Dominance */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Dominant Leg
            </label>
            <select
              value={profile.limb_dominance}
              onChange={(e) => handleChange('limb_dominance', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="right">Right</option>
              <option value="left">Left</option>
            </select>
          </div>
        </div>
      </div>

      {/* Injury History */}
      <div className="bg-white p-6 rounded-2xl shadow-md border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 mb-4">ACL Injury History</h2>
        
        <div className="space-y-4">
          {/* ACL History Flag */}
          <div className="flex items-start">
            <input
              type="checkbox"
              checked={profile.acl_history_flag}
              onChange={(e) => handleChange('acl_history_flag', e.target.checked)}
              className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label className="ml-3">
              <span className="block text-sm font-medium text-gray-900">
                I have had a previous ACL injury or surgery
              </span>
              <span className="block text-xs text-gray-500 mt-1">
                Prior ACL injury is a significant risk factor for re-injury
              </span>
            </label>
          </div>

          {/* ACL Injury Date (conditional) */}
          {profile.acl_history_flag && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date of ACL Injury/Surgery
              </label>
              <input
                type="date"
                value={profile.acl_injury_date || ''}
                onChange={(e) => handleChange('acl_injury_date', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          )}

          {/* Rehab Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Rehabilitation Status
            </label>
            <select
              value={profile.rehab_status}
              onChange={(e) => handleChange('rehab_status', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="none">Not in rehab</option>
              <option value="active_rehab">Currently in active rehab</option>
              <option value="recovered">Fully recovered / Cleared to play</option>
            </select>
          </div>
        </div>
      </div>

      {/* Current Pain Level */}
      <div className="bg-white p-6 rounded-2xl shadow-md border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Current Knee Pain</h2>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Knee Pain Level (0 = No pain, 10 = Severe pain)
          </label>
          <div className="flex items-center space-x-4">
            <input
              type="range"
              min="0"
              max="10"
              value={profile.knee_pain_score}
              onChange={(e) => handleChange('knee_pain_score', parseInt(e.target.value))}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className={`text-2xl font-bold w-12 text-center ${
              profile.knee_pain_score === 0 ? 'text-green-600' :
              profile.knee_pain_score <= 3 ? 'text-yellow-600' :
              profile.knee_pain_score <= 6 ? 'text-orange-600' :
              'text-red-600'
            }`}>
              {profile.knee_pain_score}
            </div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>No pain</span>
            <span>Moderate</span>
            <span>Severe</span>
          </div>
          {profile.knee_pain_score >= 5 && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800 font-medium">
                ⚠️ Significant knee pain detected. Consider consulting a sports medicine physician.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Save Button */}
      <div className="sticky bottom-4 bg-white p-4 rounded-2xl shadow-lg border-2 border-blue-200">
        <button
          onClick={saveProfile}
          disabled={saving || !profile.height_cm || !profile.age || !profile.weight_kg}
          className={`w-full py-4 rounded-xl font-semibold text-lg transition-all flex items-center justify-center space-x-2 ${
            saved 
              ? 'bg-green-600 text-white'
              : saving
              ? 'bg-gray-400 text-white cursor-not-allowed'
              : !profile.height_cm || !profile.age || !profile.weight_kg
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 shadow-md'
          }`}
        >
          {saved ? (
            <>
              <CheckCircle2 className="w-6 h-6" />
              <span>Profile Saved Successfully!</span>
            </>
          ) : saving ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Saving...</span>
            </>
          ) : (
            <>
              <Save className="w-6 h-6" />
              <span>Save Profile</span>
            </>
          )}
        </button>
        {(!profile.height_cm || !profile.age || !profile.weight_kg) && (
          <p className="text-center text-sm text-gray-500 mt-2">
            Please fill in all required fields (marked with *)
          </p>
        )}
      </div>
    </div>
  );
}
