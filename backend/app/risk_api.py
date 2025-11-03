"""
Real-time ACL injury risk assessment endpoints using evidence-based formula.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, ActivityData
from app.risk_calculator import compute_risk_score, generate_recommendations
from app.encryption import decrypt_token
from app.fitbit_auth import is_token_expired, refresh_access_token
from app.fitbit_data import FitbitDataService

router = APIRouter()


@router.get("/api/risk/realtime/{user_id}")
async def get_realtime_risk_assessment(
    user_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get real-time ACL injury risk assessment using evidence-based formula.
    
    Uses 7-day Fitbit data + user profile for clinical risk calculation.
    """
    # Get user from database
    user = db.query(User).filter(User.fitbit_user_id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found or disconnected")
    
    # Get recent activity data (last 7 days for risk calculation)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    activity_data = db.query(ActivityData).filter(
        ActivityData.user_id == user.id,
        ActivityData.date >= seven_days_ago.date()
    ).order_by(ActivityData.date.desc()).all()
    
    if not activity_data or len(activity_data) < 3:
        # Insufficient data - return default
        return {
            "status": "insufficient_data",
            "message": "Not enough activity data yet. Need at least 3 days of Fitbit data.",
            "risk_score": None,
            "risk_level": "Unknown",
            "risk_color": "gray",
            "confidence": "low",
            "recommendations": [
                "Connect your Fitbit and sync for at least 3 days to get accurate risk assessment.",
                "Ensure your Fitbit app is syncing with the same email you used to log in."
            ]
        }
    
    # ============================================
    # COMPUTE WEEKLY AGGREGATES FROM FITBIT DATA
    # ============================================
    
    total_steps = sum(d.steps for d in activity_data if d.steps)
    avg_steps_day = total_steps / len(activity_data) if activity_data else 0
    
    # Peak/very active minutes
    peak_minutes = [d.very_active_minutes or 0 for d in activity_data]
    avg_peak_minutes_day = sum(peak_minutes) / len(peak_minutes) if peak_minutes else 0
    
    # Resting heart rate
    resting_hrs = [d.resting_heart_rate for d in activity_data if d.resting_heart_rate]
    avg_resting_hr = sum(resting_hrs) / len(resting_hrs) if resting_hrs else 0
    
    # Sleep data
    sleep_minutes = [d.sleep_duration_minutes for d in activity_data if d.sleep_duration_minutes]
    avg_minutes_asleep = sum(sleep_minutes) / len(sleep_minutes) if sleep_minutes else 0
    
    # Weight (use latest or user profile)
    latest_weight = None
    for d in activity_data:
        if hasattr(d, 'weight_kg') and d.weight_kg:
            latest_weight = d.weight_kg
            break
    weight_kg = latest_weight or user.weight_kg or 70  # Default 70kg
    
    # High intensity days (>30 min very active)
    high_intensity_days = sum(1 for m in peak_minutes if m > 30)
    
    # ============================================
    # PREPARE FEATURE DICT
    # ============================================
    
    features = {
        'avg_steps_day': avg_steps_day,
        'avg_peak_minutes_day': avg_peak_minutes_day,
        'avg_resting_hr': avg_resting_hr,
        'avg_minutes_asleep': avg_minutes_asleep,
        'weight_kg': weight_kg,
        'high_intensity_days': high_intensity_days
    }
    
    # ============================================
    # PREPARE USER PROFILE DICT
    # ============================================
    
    user_profile = {
        'height_cm': user.height_cm or 170,  # Default 170cm
        'sex': user.sex or 'M',
        'age': user.age or 25,
        'sport': user.sport or 'none',
        'acl_history_flag': user.acl_history_flag or False,
        'baseline_resting_hr': user.baseline_resting_hr,
        'knee_pain_score': user.knee_pain_score or 0,
        'rehab_status': user.rehab_status,
        'weight_kg': weight_kg
    }
    
    # ============================================
    # COMPUTE EVIDENCE-BASED RISK SCORE
    # ============================================
    
    risk_result = compute_risk_score(features, user_profile)
    
    # ============================================
    # GENERATE ACTIONABLE RECOMMENDATIONS
    # ============================================
    
    recommendations = generate_recommendations(risk_result, features, user_profile)
    
    # ============================================
    # LATEST METRICS FROM MOST RECENT DAY
    # ============================================
    
    latest = activity_data[0]
    
    return {
        "status": "success",
        "user_id": user_id,
        "assessment_date": datetime.utcnow().isoformat(),
        "data_days": len(activity_data),
        
        # Risk Score (0-100 scale)
        "risk_score": risk_result['risk_score'],
        "risk_level": risk_result['risk_level'],
        "risk_color": risk_result['risk_color'],
        "confidence": risk_result['confidence'],
        "missing_data": risk_result['missing_data'],
        
        # Component Breakdown (with weights and contributions)
        "risk_components": {
            "load": round(risk_result['components']['load']['contribution'] * 100, 1),
            "fatigue": round(risk_result['components']['fatigue']['contribution'] * 100, 1),
            "intensity": round(risk_result['components']['intensity']['contribution'] * 100, 1),
            "bmi": round(risk_result['components']['bmi']['contribution'] * 100, 1),
            "history": round(risk_result['components']['history']['contribution'] * 100, 1),
            "pain": round(risk_result['components']['pain']['contribution'] * 100, 1)
        },
        
        # Detailed component info
        "component_details": risk_result['components'],
        
        # Latest Metrics
        "current_metrics": {
            "steps_today": latest.steps or 0,
            "heart_rate_avg": latest.resting_heart_rate or 0,
            "sleep_hours": round((latest.sleep_duration_minutes or 0) / 60, 1),
            "distance_km": round((latest.distance or 0), 2),
        },
        
        # Personalized Recommendations (evidence-based)
        "recommendations": recommendations,
        
        # Metadata for transparency
        "metadata": risk_result['metadata'],
        
        # Feature Aggregates (for debugging/transparency)
        "weekly_aggregates": {
            "avg_steps_day": round(avg_steps_day, 0),
            "avg_peak_minutes_day": round(avg_peak_minutes_day, 1),
            "avg_resting_hr": round(avg_resting_hr, 1),
            "avg_sleep_hours": round(avg_minutes_asleep / 60, 1),
            "high_intensity_days": high_intensity_days
        }
    }


@router.post("/api/risk/sync-and-assess/{user_id}")
async def sync_and_assess(
    user_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Sync latest Fitbit data and immediately run risk assessment.
    
    This provides the most up-to-date risk score.
    """
    # Get user
    user = db.query(User).filter(User.fitbit_user_id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if token needs refresh
    access_token = decrypt_token(user.access_token_encrypted)
    
    if is_token_expired(user.token_expires_at):
        # Refresh token
        refresh_token = decrypt_token(user.refresh_token_encrypted)
        from app.encryption import encrypt_token
        from app.fitbit_auth import calculate_token_expiry
        
        tokens = await refresh_access_token(refresh_token)
        
        user.access_token_encrypted = encrypt_token(tokens['access_token'])
        user.refresh_token_encrypted = encrypt_token(tokens['refresh_token'])
        user.token_expires_at = calculate_token_expiry(tokens['expires_in'])
        user.last_sync_at = datetime.utcnow()
        db.commit()
        
        access_token = tokens['access_token']
    
    # Sync latest data
    fitbit_service = FitbitDataService(access_token)
    
    # Fetch last 3 days to get latest data
    today = datetime.now().date()
    for i in range(3):
        date = today - timedelta(days=i)
        
        try:
            # Get activity
            activity = await fitbit_service.get_activity_summary(date)
            heart = await fitbit_service.get_heart_rate(date)
            sleep = await fitbit_service.get_sleep(date)
            
            # Update or create activity record
            existing = db.query(ActivityData).filter(
                ActivityData.user_id == user.id,
                ActivityData.date == date
            ).first()
            
            if existing:
                existing.steps = activity.get('summary', {}).get('steps', 0)
                existing.distance = activity.get('summary', {}).get('distances', [{}])[0].get('distance', 0)
                existing.calories = activity.get('summary', {}).get('caloriesOut', 0)
                existing.heart_rate = heart.get('activities-heart', [{}])[0].get('value', {}).get('restingHeartRate', 70)
                existing.sleep_minutes = sleep.get('summary', {}).get('totalMinutesAsleep', 0)
            else:
                new_activity = ActivityData(
                    user_id=user.id,
                    date=date,
                    steps=activity.get('summary', {}).get('steps', 0),
                    distance=activity.get('summary', {}).get('distances', [{}])[0].get('distance', 0),
                    calories=activity.get('summary', {}).get('caloriesOut', 0),
                    heart_rate=heart.get('activities-heart', [{}])[0].get('value', {}).get('restingHeartRate', 70),
                    sleep_minutes=sleep.get('summary', {}).get('totalMinutesAsleep', 0),
                )
                db.add(new_activity)
        
        except Exception as e:
            print(f"Error syncing data for {date}: {e}")
            continue
    
    db.commit()
    
    # Now run risk assessment with updated data
    return await get_realtime_risk_assessment(user_id, db)
