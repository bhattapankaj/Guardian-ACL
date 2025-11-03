"""
Evidence-based ACL risk calculator using Fitbit data + manual user inputs.
Based on clinical research and biomechanical principles.

Weights and normalization caps are informed by ACL injury literature.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value between lo and hi."""
    return max(lo, min(hi, x))


def compute_risk_score(features: Dict, user: Dict) -> Dict:
    """
    Compute evidence-based ACL injury risk score from Fitbit data + user profile.
    
    Args:
        features: Weekly aggregates from Fitbit
            - avg_steps_day: Average daily steps over 7 days
            - avg_peak_minutes_day: Average daily minutes in peak/very active zone
            - avg_resting_hr: Average resting heart rate
            - avg_minutes_asleep: Average minutes asleep per night
            - weight_kg: Current weight in kg
            - high_intensity_days: Number of high-intensity days in week
            
        user: User profile dict
            - height_cm: Height in centimeters
            - sex: 'M', 'F', or 'Other'
            - age: Age in years
            - sport: 'football', 'soccer', 'basketball', 'none'
            - acl_history_flag: Boolean - previous ACL injury
            - baseline_resting_hr: Baseline resting HR (computed or default)
            - knee_pain_score: Self-reported pain 0-10
            - rehab_status: 'active_rehab', 'recovered', 'none'
    
    Returns:
        Dict with:
            - risk_score: Float 0-1
            - risk_level: 'Low', 'Moderate', 'High'
            - risk_color: 'green', 'yellow', 'red'
            - components: Dict of normalized component indices
            - confidence: 'high', 'medium', 'low'
            - missing_data: List of missing critical fields
    """
    
    # Extract features with safe defaults
    avg_steps = features.get('avg_steps_day', 0)
    avg_peak_minutes = features.get('avg_peak_minutes_day', 0)
    avg_resting_hr = features.get('avg_resting_hr', 0)
    avg_minutes_asleep = features.get('avg_minutes_asleep', 0)
    weight_kg = features.get('weight_kg', user.get('weight_kg', 70))  # Default 70kg
    
    # User profile
    height_cm = user.get('height_cm', 170)  # Default 170cm
    height_m = height_cm / 100.0
    sex = user.get('sex', 'M')
    age = user.get('age', 25)
    
    # Calculate BMI
    bmi = weight_kg / (height_m ** 2) if height_m > 0 else 22
    
    # Baseline resting HR (population defaults if not set)
    baseline_hr = user.get('baseline_resting_hr')
    if not baseline_hr:
        # Age and sex-based defaults
        if sex == 'F':
            baseline_hr = 68 if age < 30 else 70
        else:
            baseline_hr = 63 if age < 30 else 65
    
    # Track missing data for confidence scoring
    missing_data = []
    
    # ============================================
    # NORMALIZATION: Map each feature to 0-1
    # ============================================
    
    # 1. LOAD INDEX (30% weight)
    # Based on average daily steps
    # Research: 5k = low, 20k+ = very high load
    load_index = clamp((avg_steps - 5000) / (20000 - 5000))
    
    # 2. INTENSITY INDEX (15% weight)
    # Based on peak/very active minutes per day
    # Research: 60+ minutes peak intensity = high
    intensity_index = clamp(avg_peak_minutes / 60.0)
    
    # 3. FATIGUE INDEX (25% weight)
    # Combines HR elevation + sleep deficit
    if avg_resting_hr > 0:
        hr_component = clamp((avg_resting_hr - baseline_hr) / 8.0)  # 8 bpm above = max
    else:
        hr_component = 0.5  # Unknown = moderate risk
        missing_data.append('resting_heart_rate')
    
    if avg_minutes_asleep > 0:
        sleep_component = clamp((420 - avg_minutes_asleep) / 240.0)  # 420min = 7h baseline
    else:
        sleep_component = 0.5  # Unknown = moderate risk
        missing_data.append('sleep_data')
    
    fatigue_index = max(hr_component, sleep_component)
    
    # 4. BMI INDEX (10% weight)
    # Research: BMI 22 = ideal, 35+ = high risk
    bmi_index = clamp((bmi - 22) / (35 - 22))
    
    # 5. HISTORY INDEX (10% weight)
    # Previous ACL injury = major risk factor
    acl_history_flag = user.get('acl_history_flag', False)
    history_index = 1.0 if acl_history_flag else 0.0
    
    # 6. PAIN INDEX (5% weight)
    # Self-reported knee pain 0-10
    knee_pain = user.get('knee_pain_score', 0)
    pain_index = clamp(knee_pain / 10.0)
    
    # 7. SPORT RISK FACTOR (multiplier)
    # Different sports have different ACL injury rates
    sport_factors = {
        'football': 0.25,    # Highest contact risk
        'soccer': 0.20,      # High cutting/pivoting
        'basketball': 0.18,  # High jumping/landing
        'running': 0.08,
        'cycling': 0.03,
        'none': 0.05
    }
    sport = user.get('sport', 'none').lower()
    sport_risk = sport_factors.get(sport, 0.05)
    sport_index = sport_risk / 0.25  # Normalize to 0-1
    
    # ============================================
    # WEIGHTED RISK SCORE
    # ============================================
    
    risk_raw = (
        0.30 * load_index +
        0.25 * fatigue_index +
        0.15 * intensity_index +
        0.10 * bmi_index +
        0.10 * history_index +
        0.05 * pain_index
    )
    
    # Apply sport multiplier
    risk_adjusted = clamp(risk_raw * (1 + 0.15 * sport_index))
    
    # Female athletes have ~3-8x higher ACL risk (literature)
    if sex == 'F':
        risk_adjusted = clamp(risk_adjusted * 1.15)  # 15% increase
    
    # ============================================
    # RISK LEVEL MAPPING
    # ============================================
    
    if risk_adjusted < 0.30:
        risk_level = 'Low'
        risk_color = 'green'
    elif risk_adjusted < 0.60:
        risk_level = 'Moderate'
        risk_color = 'yellow'
    else:
        risk_level = 'High'
        risk_color = 'red'
    
    # ============================================
    # CONFIDENCE SCORING
    # ============================================
    
    confidence = 'high'
    if len(missing_data) >= 2:
        confidence = 'low'
    elif len(missing_data) == 1:
        confidence = 'medium'
    
    # Low data volume reduces confidence
    if avg_steps < 1000:  # Very low activity
        confidence = 'low'
        missing_data.append('insufficient_activity_data')
    
    # ============================================
    # RETURN COMPREHENSIVE RESULT
    # ============================================
    
    return {
        'risk_score': round(risk_adjusted * 100, 1),  # Convert to 0-100 scale
        'risk_level': risk_level,
        'risk_color': risk_color,
        'confidence': confidence,
        'missing_data': missing_data,
        'components': {
            'load': {
                'index': round(load_index, 3),
                'weight': 0.30,
                'contribution': round(load_index * 0.30, 3),
                'description': f'Avg {int(avg_steps)} steps/day'
            },
            'fatigue': {
                'index': round(fatigue_index, 3),
                'weight': 0.25,
                'contribution': round(fatigue_index * 0.25, 3),
                'description': f'HR: {int(avg_resting_hr)} bpm, Sleep: {avg_minutes_asleep/60:.1f}h'
            },
            'intensity': {
                'index': round(intensity_index, 3),
                'weight': 0.15,
                'contribution': round(intensity_index * 0.15, 3),
                'description': f'{int(avg_peak_minutes)} peak min/day'
            },
            'bmi': {
                'index': round(bmi_index, 3),
                'weight': 0.10,
                'contribution': round(bmi_index * 0.10, 3),
                'description': f'BMI: {bmi:.1f}'
            },
            'history': {
                'index': round(history_index, 3),
                'weight': 0.10,
                'contribution': round(history_index * 0.10, 3),
                'description': 'Previous ACL injury' if acl_history_flag else 'No ACL history'
            },
            'pain': {
                'index': round(pain_index, 3),
                'weight': 0.05,
                'contribution': round(pain_index * 0.05, 3),
                'description': f'Knee pain: {knee_pain}/10'
            },
            'sport': {
                'index': round(sport_index, 3),
                'multiplier': 0.15,
                'description': f'Sport: {sport.title()}'
            }
        },
        'metadata': {
            'bmi': round(bmi, 1),
            'baseline_resting_hr': baseline_hr,
            'sex': sex,
            'age': age
        }
    }


def generate_recommendations(risk_result: Dict, features: Dict, user: Dict) -> List[str]:
    """
    Generate actionable, evidence-based recommendations based on risk components.
    
    Args:
        risk_result: Output from compute_risk_score
        features: Weekly Fitbit aggregates
        user: User profile
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    components = risk_result['components']
    
    # HIGH LOAD recommendations
    if components['load']['index'] > 0.7:
        recommendations.append(
            "⚠️ Training volume is very high. Reduce step count by 15-20% for the next 48 hours to allow recovery."
        )
    elif components['load']['index'] > 0.5:
        recommendations.append(
            "📊 Training load is elevated. Monitor for signs of fatigue and ensure adequate rest days."
        )
    
    # FATIGUE recommendations
    if components['fatigue']['index'] > 0.6:
        avg_sleep_hours = features.get('avg_minutes_asleep', 0) / 60
        if avg_sleep_hours < 7:
            recommendations.append(
                f"😴 Sleep quality is poor ({avg_sleep_hours:.1f}h avg). Target 7-9 hours per night for optimal recovery."
            )
        recommendations.append(
            "🔄 Schedule a complete rest day within the next 48 hours. High fatigue increases injury risk."
        )
    
    # INTENSITY recommendations
    if components['intensity']['index'] > 0.7:
        recommendations.append(
            "🏃 High-intensity training is frequent. Incorporate more low-intensity active recovery sessions."
        )
    
    # BMI recommendations
    bmi = risk_result['metadata']['bmi']
    if bmi > 30:
        recommendations.append(
            f"⚖️ BMI is elevated ({bmi:.1f}). Consider consulting a sports nutritionist for weight management."
        )
    elif bmi < 18.5:
        recommendations.append(
            f"⚖️ BMI is low ({bmi:.1f}). Ensure adequate nutrition to support training demands."
        )
    
    # PAIN recommendations
    knee_pain = user.get('knee_pain_score', 0)
    if knee_pain >= 5:
        recommendations.append(
            f"🏥 URGENT: Knee pain is significant ({knee_pain}/10). Consult a sports medicine physician or physical therapist immediately."
        )
    elif knee_pain >= 3:
        recommendations.append(
            f"⚕️ Moderate knee pain detected ({knee_pain}/10). Monitor closely and reduce high-impact activities."
        )
    
    # ACL HISTORY recommendations
    if user.get('acl_history_flag'):
        recommendations.append(
            "🔍 Previous ACL injury detected. Maintain neuromuscular training and avoid sudden direction changes without proper warm-up."
        )
        if user.get('rehab_status') != 'recovered':
            recommendations.append(
                "💪 Continue prescribed rehabilitation exercises. Compliance is critical for preventing re-injury."
            )
    
    # SPORT-SPECIFIC recommendations
    sport = user.get('sport', 'none').lower()
    if sport in ['football', 'soccer', 'basketball']:
        recommendations.append(
            f"⚽ For {sport.title()}: Focus on landing mechanics, deceleration training, and core stability exercises."
        )
    
    # GENERAL recommendations
    if risk_result['risk_level'] == 'High':
        recommendations.append(
            "🛡️ Overall risk is HIGH. Consider a formal ACL injury prevention program (e.g., FIFA 11+, PEP program)."
        )
    
    if risk_result['confidence'] == 'low':
        recommendations.append(
            "📱 Data quality is limited. Ensure your Fitbit is synced daily for more accurate risk assessment."
        )
    
    # Limit to top 5 most important
    return recommendations[:5]
