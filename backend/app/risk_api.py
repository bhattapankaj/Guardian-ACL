"""
Real-time ACL injury risk assessment endpoints using ML model.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, ActivityData
from app.ml_model import get_model
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
    Get real-time ACL injury risk assessment using ML model.
    
    Fetches latest 14 days of activity data and runs through trained model.
    """
    # Get user from database
    user = db.query(User).filter(User.fitbit_user_id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found or disconnected")
    
    # Get recent activity data (last 14 days)
    two_weeks_ago = datetime.utcnow() - timedelta(days=14)
    activity_data = db.query(ActivityData).filter(
        ActivityData.user_id == user.id,
        ActivityData.date >= two_weeks_ago.date()
    ).order_by(ActivityData.date.desc()).all()
    
    if not activity_data:
        # No data yet - return default assessment
        return {
            "status": "insufficient_data",
            "message": "Not enough activity data yet. Connect your Fitbit and sync data.",
            "risk_score": None,
            "recommendations": ["Connect your Fitbit and allow a few days of data collection."]
        }
    
    # Load ML model
    model = get_model()
    
    # Extract features from activity data
    features = model.extract_features(activity_data)
    
    # Get risk prediction
    prediction = model.predict_risk(features)
    
    # Add latest metrics from most recent day
    latest = activity_data[0]
    
    return {
        "status": "success",
        "user_id": user_id,
        "assessment_date": datetime.utcnow().isoformat(),
        "data_days": len(activity_data),
        
        # ML Model Prediction
        "risk_score": prediction['risk_score'],
        "risk_level": prediction['risk_level'],
        "risk_color": prediction['risk_color'],
        
        # Component Breakdown
        "risk_components": prediction['components'],
        
        # Latest Metrics
        "current_metrics": {
            "steps_today": latest.steps or 0,
            "heart_rate_avg": latest.heart_rate or 0,
            "sleep_hours": round((latest.sleep_minutes or 0) / 60, 1),
            "calories": latest.calories or 0,
            "distance_km": round((latest.distance or 0), 2),
        },
        
        # Personalized Recommendations
        "recommendations": prediction['recommendations'],
        
        # Feature Details (for transparency)
        "analysis_details": {
            "step_asymmetry_pct": round(features['step_asymmetry'], 1),
            "cadence_variance_pct": round(features['cadence_variance'], 1),
            "load_spike_pct": round(features['load_spike'], 1),
            "fatigue_score": round(features['fatigue_score'], 1),
            "consistency_pct": round(features['consistency'], 1),
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
