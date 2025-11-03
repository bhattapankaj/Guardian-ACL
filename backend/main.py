from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
import random
import os
from dotenv import load_dotenv

# Import our Fitbit integration modules
from app.database import get_db, init_db
from app.models import User, ActivityData
from app.encryption import encrypt_token, decrypt_token
from app.fitbit_auth import generate_authorization_url, exchange_code_for_tokens, refresh_access_token, calculate_token_expiry, is_token_expired
from app.fitbit_data import FitbitDataService, calculate_cadence, calculate_load_score, calculate_impact_score, calculate_consistency_score

# Import ML risk assessment endpoints
from app.risk_api import router as risk_router

load_dotenv()

app = FastAPI(title="ACL Guardian API", version="2.0.0 - Real Fitbit Integration")

# Configure CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "https://*.netlify.app"],  # Allow Netlify deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("🚀 ACL Guardian API started with Fitbit integration!")
    print(f"📡 Frontend URL: {FRONTEND_URL}")

# Include ML risk assessment router
app.include_router(risk_router, tags=["Risk Assessment - ML Powered"])

# Models
class FitbitAuthRequest(BaseModel):
    code: str

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    connected_devices: List[str]

class ActivityMetrics(BaseModel):
    steps: int
    distance: float
    calories: int
    active_minutes: int
    heart_rate_avg: Optional[int]
    cadence: Optional[float]
    asymmetry_score: Optional[float]

class ACLRiskScore(BaseModel):
    overall_score: float  # 0-100
    risk_level: str  # "low", "moderate", "high"
    factors: Dict[str, float]
    timestamp: str

class PreventionRecommendation(BaseModel):
    category: str
    title: str
    description: str
    priority: str  # "high", "medium", "low"

# Mock data storage (replace with database in production)
users_db = {}
activity_data_db = {}

@app.get("/")
def read_root():
    return {
        "message": "ACL Guardian API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ============================================
# FITBIT OAUTH ENDPOINTS (REAL INTEGRATION)
# ============================================

@app.get("/api/fitbit/authorize")
async def fitbit_authorize():
    """
    Step 1: Redirect user to Fitbit OAuth authorization page.
    User clicks "Connect Fitbit" → This endpoint → Fitbit login page
    """
    auth_url = generate_authorization_url(state="acl_guardian_auth")
    return RedirectResponse(url=auth_url)


@app.get("/api/fitbit/callback")
async def fitbit_callback(code: str, state: str = None, db: Session = Depends(get_db)):
    """
    Step 2: Handle OAuth callback from Fitbit.
    Fitbit redirects here after user authorizes → Exchange code for tokens → Save to database
    """
    try:
        # Exchange authorization code for access and refresh tokens
        token_data = await exchange_code_for_tokens(code)
        
        # Extract token information
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']
        expires_in = token_data['expires_in']
        fitbit_user_id = token_data['user_id']
        
        # Calculate token expiration
        expires_at = calculate_token_expiry(expires_in)
        
        # Encrypt tokens before storing
        encrypted_access = encrypt_token(access_token)
        encrypted_refresh = encrypt_token(refresh_token)
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.fitbit_user_id == fitbit_user_id).first()
        
        if existing_user:
            # Update existing user's tokens
            existing_user.access_token_encrypted = encrypted_access
            existing_user.refresh_token_encrypted = encrypted_refresh
            existing_user.token_expires_at = expires_at
            existing_user.updated_at = datetime.utcnow()
            existing_user.is_active = True
            db.commit()
            user_id = existing_user.id
        else:
            # Create new user
            new_user = User(
                fitbit_user_id=fitbit_user_id,
                access_token_encrypted=encrypted_access,
                refresh_token_encrypted=encrypted_refresh,
                token_expires_at=expires_at,
                is_active=True
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user_id = new_user.id
        
        # Fetch initial user data from Fitbit
        fitbit_service = FitbitDataService(access_token)
        profile = await fitbit_service.get_user_profile()
        
        # Update user profile information
        user = db.query(User).filter(User.id == user_id).first()
        user.name = profile.get('fullName', 'Athlete')
        user.email = profile.get('email')
        db.commit()
        
        # Redirect back to frontend with success
        return RedirectResponse(url=f"{FRONTEND_URL}/?connected=true&user_id={user_id}")
        
    except Exception as e:
        print(f"❌ OAuth callback error: {e}")
        return RedirectResponse(url=f"{FRONTEND_URL}/?connected=false&error={str(e)}")


@app.post("/api/fitbit/disconnect/{user_id}")
async def disconnect_fitbit(user_id: int, db: Session = Depends(get_db)):
    """
    Disconnect user's Fitbit account.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    
    return {"message": "Fitbit disconnected successfully"}


# ============================================
# DATA SYNC ENDPOINTS
# ============================================

@app.post("/api/fitbit/sync/{user_id}")
async def sync_fitbit_data(user_id: int, days: int = 14, db: Session = Depends(get_db)):
    """
    Manually trigger Fitbit data sync for a user.
    Fetches last N days of activity, heart rate, and sleep data.
    """
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found or inactive")
    
    # Check if token needs refresh
    if is_token_expired(user.token_expires_at):
        # Refresh the access token
        refresh_token = decrypt_token(user.refresh_token_encrypted)
        token_data = await refresh_access_token(refresh_token)
        
        # Update tokens in database
        user.access_token_encrypted = encrypt_token(token_data['access_token'])
        user.refresh_token_encrypted = encrypt_token(token_data['refresh_token'])
        user.token_expires_at = calculate_token_expiry(token_data['expires_in'])
        db.commit()
    
    # Decrypt access token for API calls
    access_token = decrypt_token(user.access_token_encrypted)
    
    # Fetch data from Fitbit
    fitbit_service = FitbitDataService(access_token)
    historical_data = await fitbit_service.get_historical_activity(days=days)
    
    synced_count = 0
    
    for day_data in historical_data:
        target_date = day_data['date']
        activity = day_data['activity']
        heart_rate = day_data['heart_rate']
        sleep = day_data['sleep']
        
        # Check if we already have data for this date
        existing_data = db.query(ActivityData).filter(
            ActivityData.user_id == user_id,
            ActivityData.date == target_date
        ).first()
        
        # Calculate risk factor scores
        steps = activity.get('steps', 0)
        active_mins = activity.get('fairlyActiveMinutes', 0) + activity.get('veryActiveMinutes', 0)
        very_active_mins = activity.get('veryActiveMinutes', 0)
        
        cadence_score = calculate_cadence(steps, active_mins) if active_mins > 0 else 0
        load_score = calculate_load_score(active_mins, very_active_mins)
        impact_score = calculate_impact_score(heart_rate)
        
        sleep_efficiency = sleep.get('efficiency')
        sleep_duration = sleep.get('duration', 0) // 60000 if sleep.get('duration') else None  # Convert ms to minutes
        consistency_score = calculate_consistency_score(sleep_efficiency, sleep_duration)
        
        # Calculate total risk score (weighted average)
        # Asymmetry is 0 for now (needs intraday data)
        total_risk = (
            0 * 0.30 +  # Asymmetry (pending intraday approval)
            load_score * 0.25 +
            impact_score * 0.20 +
            (100 - cadence_score) * 0.15 +  # Invert cadence (higher is better)
            consistency_score * 0.10
        )
        
        if existing_data:
            # Update existing record
            existing_data.steps = steps
            existing_data.distance = activity.get('distances', [{}])[0].get('distance', 0) if activity.get('distances') else 0
            existing_data.calories = activity.get('caloriesOut', 0)
            existing_data.active_minutes = active_mins
            existing_data.sedentary_minutes = activity.get('sedentaryMinutes', 0)
            existing_data.lightly_active_minutes = activity.get('lightlyActiveMinutes', 0)
            existing_data.fairly_active_minutes = activity.get('fairlyActiveMinutes', 0)
            existing_data.very_active_minutes = very_active_mins
            existing_data.resting_heart_rate = heart_rate.get('restingHeartRate')
            existing_data.sleep_duration_minutes = sleep_duration
            existing_data.sleep_efficiency = sleep_efficiency
            existing_data.cadence_score = cadence_score
            existing_data.load_score = load_score
            existing_data.impact_score = impact_score
            existing_data.consistency_score = consistency_score
            existing_data.total_risk_score = total_risk
            existing_data.synced_at = datetime.utcnow()
        else:
            # Create new record
            new_data = ActivityData(
                user_id=user_id,
                date=target_date,
                steps=steps,
                distance=activity.get('distances', [{}])[0].get('distance', 0) if activity.get('distances') else 0,
                calories=activity.get('caloriesOut', 0),
                active_minutes=active_mins,
                sedentary_minutes=activity.get('sedentaryMinutes', 0),
                lightly_active_minutes=activity.get('lightlyActiveMinutes', 0),
                fairly_active_minutes=activity.get('fairlyActiveMinutes', 0),
                very_active_minutes=very_active_mins,
                resting_heart_rate=heart_rate.get('restingHeartRate'),
                sleep_duration_minutes=sleep_duration,
                sleep_efficiency=sleep_efficiency,
                cadence_score=cadence_score,
                load_score=load_score,
                impact_score=impact_score,
                consistency_score=consistency_score,
                total_risk_score=total_risk
            )
            db.add(new_data)
        
        synced_count += 1
    
    db.commit()
    user.last_sync_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": f"Successfully synced {synced_count} days of data",
        "user_id": user_id,
        "days_synced": synced_count,
        "last_sync": user.last_sync_at.isoformat()
    }


@app.get("/api/fitbit/activity/{user_id}")
async def get_fitbit_activity(user_id: int, days: int = 7, db: Session = Depends(get_db)):
    """
    Get user's Fitbit activity data from database.
    Returns last N days of synced activity data.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get activity data from database
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    activity_records = db.query(ActivityData).filter(
        ActivityData.user_id == user_id,
        ActivityData.date >= start_date,
        ActivityData.date <= end_date
    ).order_by(ActivityData.date.desc()).all()
    
    if not activity_records:
        return {
            "activities": [],
            "message": "No activity data found. Please sync your Fitbit data first."
        }
    
    # Format activity data for frontend
    activities = []
    for record in activity_records:
        activities.append({
            "date": record.date.isoformat(),
            "steps": record.steps,
            "distance": record.distance,
            "calories": record.calories,
            "active_minutes": record.active_minutes,
            "sedentary_minutes": record.sedentary_minutes,
            "lightly_active_minutes": record.lightly_active_minutes,
            "fairly_active_minutes": record.fairly_active_minutes,
            "very_active_minutes": record.very_active_minutes,
            "heart_rate_avg": record.resting_heart_rate,
            "sleep_hours": record.sleep_duration_minutes / 60 if record.sleep_duration_minutes else None,
            "sleep_efficiency": record.sleep_efficiency,
            "deep_sleep_minutes": record.deep_sleep_minutes,
            "light_sleep_minutes": record.light_sleep_minutes,
            "rem_sleep_minutes": record.rem_sleep_minutes,
            "cadence": record.cadence_score,
            "asymmetry_score": record.asymmetry_score or 0,
            "load_score": record.load_score,
            "impact_score": record.impact_score
        })
    
    return {"activities": activities}


@app.post("/api/user/{user_id}/profile")
async def update_user_profile(user_id: str, profile_data: dict, db: Session = Depends(get_db)):
    """
    Update user profile with manual health inputs for evidence-based risk calculation.
    """
    user = db.query(User).filter(User.fitbit_user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update profile fields
    if 'height_cm' in profile_data:
        user.height_cm = profile_data['height_cm']
    if 'sex' in profile_data:
        user.sex = profile_data['sex']
    if 'age' in profile_data:
        user.age = profile_data['age']
    if 'sport' in profile_data:
        user.sport = profile_data['sport']
    if 'limb_dominance' in profile_data:
        user.limb_dominance = profile_data['limb_dominance']
    if 'acl_history_flag' in profile_data:
        user.acl_history_flag = profile_data['acl_history_flag']
    if 'acl_injury_date' in profile_data:
        user.acl_injury_date = profile_data['acl_injury_date']
    if 'knee_pain_score' in profile_data:
        user.knee_pain_score = profile_data['knee_pain_score']
    if 'rehab_status' in profile_data:
        user.rehab_status = profile_data['rehab_status']
    if 'weight_kg' in profile_data:
        user.weight_kg = profile_data['weight_kg']
    
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return {
        "status": "success",
        "message": "Profile updated successfully",
        "profile": {
            "height_cm": user.height_cm,
            "sex": user.sex,
            "age": user.age,
            "sport": user.sport,
            "limb_dominance": user.limb_dominance,
            "acl_history_flag": user.acl_history_flag,
            "knee_pain_score": user.knee_pain_score,
            "rehab_status": user.rehab_status,
            "weight_kg": user.weight_kg
        }
    }


@app.get("/api/user/{user_id}/profile")
async def get_user_profile_data(user_id: str, db: Session = Depends(get_db)):
    """
    Get user profile data.
    """
    user = db.query(User).filter(User.fitbit_user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "height_cm": user.height_cm,
        "sex": user.sex,
        "age": user.age,
        "sport": user.sport,
        "limb_dominance": user.limb_dominance,
        "acl_history_flag": user.acl_history_flag,
        "acl_injury_date": user.acl_injury_date.isoformat() if user.acl_injury_date else None,
        "knee_pain_score": user.knee_pain_score,
        "rehab_status": user.rehab_status,
        "weight_kg": user.weight_kg
    }


@app.get("/user/{user_id}/profile")
def get_user_profile(user_id: str):
    """Get user profile information (legacy endpoint)"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

@app.get("/user/{user_id}/activity")
def get_activity_data(user_id: str, days: int = 7):
    """Get user activity data from Fitbit"""
    # Generate realistic demo data
    activity_history = []
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        
        # Generate realistic values with some variation
        base_steps = random.randint(8000, 15000)
        
        activity = {
            "date": date,
            "steps": base_steps,
            "distance": round(base_steps * 0.0007, 2),  # km
            "calories": base_steps // 20 + random.randint(1800, 2200),
            "active_minutes": random.randint(30, 120),
            "heart_rate_avg": random.randint(65, 85),
            "cadence": round(random.uniform(150, 180), 1),  # steps per minute
            "asymmetry_score": round(random.uniform(0.85, 0.98), 3),  # 1.0 is perfect symmetry
            "load_score": round(random.uniform(60, 95), 1),
            "peak_impact": round(random.uniform(2.0, 4.5), 1)  # G-force
        }
        
        activity_history.append(activity)
    
    return {"activities": activity_history}

def calculate_acl_risk_score(activity_data: List[dict]) -> ACLRiskScore:
    """
    Calculate ACL injury risk score based on biomechanical data
    
    Risk factors from NCBI research:
    - Gait asymmetry (higher asymmetry = higher risk)
    - Training load (sudden spikes = higher risk)
    - Impact forces (higher forces = higher risk)
    - Cadence variability (low cadence = higher risk)
    - Fatigue markers (high heart rate + low cadence = higher risk)
    """
    
    if not activity_data:
        raise ValueError("No activity data provided")
    
    # Extract metrics
    asymmetry_scores = [a.get('asymmetry_score', 0.95) for a in activity_data]
    load_scores = [a.get('load_score', 70) for a in activity_data]
    peak_impacts = [a.get('peak_impact', 3.0) for a in activity_data]
    cadences = [a.get('cadence', 170) for a in activity_data]
    
    # Calculate risk factors (0-100 scale, higher = more risk)
    
    # 1. Asymmetry Risk (inverted - lower asymmetry score = higher risk)
    avg_asymmetry = np.mean(asymmetry_scores)
    asymmetry_risk = (1 - avg_asymmetry) * 100  # 0.90 symmetry = 10 risk points
    
    # 2. Load Management Risk (check for spikes)
    if len(load_scores) > 1:
        load_changes = np.diff(load_scores)
        max_spike = np.max(np.abs(load_changes))
        load_risk = min(max_spike * 2, 100)  # Cap at 100
    else:
        load_risk = 0
    
    # 3. Impact Risk
    avg_impact = np.mean(peak_impacts)
    impact_risk = min((avg_impact - 2.0) * 25, 100)  # 2.0G is baseline, increases risk
    
    # 4. Cadence Risk (low cadence increases ACL stress)
    avg_cadence = np.mean(cadences)
    optimal_cadence = 170
    cadence_risk = max(0, (optimal_cadence - avg_cadence) / 2)
    
    # 5. Consistency Risk (high variability = poor neuromuscular control)
    cadence_variability = np.std(cadences)
    consistency_risk = min(cadence_variability * 3, 100)
    
    # Weighted overall risk score
    weights = {
        'asymmetry': 0.30,
        'load_management': 0.25,
        'impact': 0.20,
        'cadence': 0.15,
        'consistency': 0.10
    }
    
    factors = {
        'asymmetry': round(asymmetry_risk, 1),
        'load_management': round(load_risk, 1),
        'impact': round(impact_risk, 1),
        'cadence': round(cadence_risk, 1),
        'consistency': round(consistency_risk, 1)
    }
    
    overall_score = (
        asymmetry_risk * weights['asymmetry'] +
        load_risk * weights['load_management'] +
        impact_risk * weights['impact'] +
        cadence_risk * weights['cadence'] +
        consistency_risk * weights['consistency']
    )
    
    # Determine risk level
    if overall_score < 30:
        risk_level = "low"
    elif overall_score < 60:
        risk_level = "moderate"
    else:
        risk_level = "high"
    
    return ACLRiskScore(
        overall_score=round(overall_score, 1),
        risk_level=risk_level,
        factors=factors,
        timestamp=datetime.now().isoformat()
    )

@app.get("/user/{user_id}/risk-assessment")
def get_risk_assessment(user_id: str):
    """Get ACL injury risk assessment for user"""
    # Get recent activity data
    activity_response = get_activity_data(user_id, days=7)
    activities = activity_response["activities"]
    
    # Calculate risk score
    risk_score = calculate_acl_risk_score(activities)
    
    return risk_score

@app.get("/user/{user_id}/recommendations")
def get_recommendations(user_id: str):
    """Get personalized prevention recommendations based on risk assessment"""
    # Get risk assessment
    risk_data = get_risk_assessment(user_id)
    
    recommendations = []
    
    # Asymmetry-based recommendations
    if risk_data.factors['asymmetry'] > 20:
        recommendations.append(PreventionRecommendation(
            category="Biomechanics",
            title="Single-Leg Balance Training",
            description="Perform single-leg balance exercises for 3 sets of 30 seconds per leg daily. Focus on maintaining knee alignment over the ankle.",
            priority="high"
        ))
        recommendations.append(PreventionRecommendation(
            category="Biomechanics",
            title="Gait Analysis Recommended",
            description="Consider professional gait analysis to identify and correct movement asymmetries.",
            priority="medium"
        ))
    
    # Load management recommendations
    if risk_data.factors['load_management'] > 30:
        recommendations.append(PreventionRecommendation(
            category="Training Load",
            title="Reduce Training Volume",
            description="Recent spike in training load detected. Reduce your training volume by 20-30% for the next 3-5 days to allow adaptation.",
            priority="high"
        ))
        recommendations.append(PreventionRecommendation(
            category="Recovery",
            title="Additional Rest Day",
            description="Schedule an extra rest day this week to manage fatigue and reduce injury risk.",
            priority="high"
        ))
    
    # Impact recommendations
    if risk_data.factors['impact'] > 40:
        recommendations.append(PreventionRecommendation(
            category="Technique",
            title="Landing Mechanics Training",
            description="Practice soft landings with bent knees and hips. Perform jump-landing drills 2-3x per week, focusing on knee alignment.",
            priority="high"
        ))
    
    # Cadence recommendations
    if risk_data.factors['cadence'] > 25:
        recommendations.append(PreventionRecommendation(
            category="Running Form",
            title="Increase Cadence",
            description="Aim for 170-180 steps per minute to reduce ground reaction forces and ACL strain. Use a metronome during runs.",
            priority="medium"
        ))
    
    # General neuromuscular recommendations
    recommendations.append(PreventionRecommendation(
        category="Warmup",
        title="ACL Injury Prevention Protocol",
        description="Perform the FIFA 11+ warmup program before training sessions. Includes exercises for strength, balance, and neuromuscular control.",
        priority="high"
    ))
    
    recommendations.append(PreventionRecommendation(
        category="Strength",
        title="Hamstring-to-Quadriceps Ratio",
        description="Strengthen hamstrings with Nordic curls and Romanian deadlifts. Aim for H:Q ratio of 0.6-0.8 to protect the ACL.",
        priority="medium"
    ))
    
    return {"recommendations": recommendations}

@app.get("/ncbi/acl-research")
def get_ncbi_research_summary():
    """Get summary of ACL research from NCBI data"""
    return {
        "summary": "ACL injuries are common in sports involving cutting, pivoting, and jumping. Research shows that female athletes are 2-8x more likely to suffer ACL tears than males due to anatomical, hormonal, and neuromuscular factors.",
        "risk_factors": [
            "Poor neuromuscular control",
            "Gait asymmetry",
            "High BMI and obesity",
            "Previous ACL injury",
            "Family history",
            "Sport type (soccer, basketball, football)",
            "Improper landing mechanics"
        ],
        "prevention_strategies": [
            "Neuromuscular training programs (FIFA 11+, PEP)",
            "Strength training focusing on hamstrings and hip muscles",
            "Plyometric and agility training with proper technique",
            "Balance and proprioception exercises",
            "Gradual load progression",
            "Adequate rest and recovery"
        ],
        "incidence_rates": {
            "high_school_football": "11.1 per 100,000 athlete exposures",
            "ncaa_football": "14.4-18.0 per 100,000 athlete exposures",
            "nfl": "1.9% single-season risk"
        },
        "source": "Based on NCBI research literature"
    }

# ============================================
# MANUAL DATA ENTRY ENDPOINT
# ============================================

class ManualActivityData(BaseModel):
    date: str  # YYYY-MM-DD format
    steps: Optional[int] = None
    distance_km: Optional[float] = None
    calories: Optional[int] = None
    active_minutes: Optional[int] = None
    peak_minutes: Optional[int] = None
    resting_heart_rate: Optional[int] = None
    sleep_hours: Optional[float] = None
    sleep_efficiency: Optional[int] = None

@app.post("/api/manual-data/{user_id}")
def save_manual_activity_data(user_id: str, data: ManualActivityData, db: Session = Depends(get_db)):
    """
    Save manually entered activity data from any wearable device.
    This allows athletes using Whoop, Polar, or other devices to input their data.
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Parse date
        activity_date = datetime.strptime(data.date, "%Y-%m-%d").date()
        
        # Check if data already exists for this date
        existing = db.query(ActivityData).filter(
            ActivityData.user_id == user_id,
            ActivityData.date == activity_date
        ).first()
        
        if existing:
            # Update existing record
            if data.steps is not None:
                existing.steps = data.steps
            if data.distance_km is not None:
                existing.distance = data.distance_km
            if data.calories is not None:
                existing.calories = data.calories
            if data.active_minutes is not None:
                existing.active_minutes = data.active_minutes
            if data.peak_minutes is not None:
                existing.very_active_minutes = data.peak_minutes  # Map to very_active_minutes
            if data.resting_heart_rate is not None:
                existing.resting_heart_rate = data.resting_heart_rate
            if data.sleep_hours is not None:
                existing.sleep_duration_minutes = int(data.sleep_hours * 60)
            if data.sleep_efficiency is not None:
                existing.sleep_efficiency = data.sleep_efficiency
            
            db.commit()
            return {
                "status": "success",
                "message": f"Updated activity data for {data.date}",
                "data_updated": True
            }
        else:
            # Create new record
            new_activity = ActivityData(
                user_id=user_id,
                date=activity_date,
                steps=data.steps or 0,
                distance=data.distance_km or 0.0,
                calories=data.calories or 0,
                active_minutes=data.active_minutes or 0,
                very_active_minutes=data.peak_minutes or 0,
                resting_heart_rate=data.resting_heart_rate,
                sleep_duration_minutes=int(data.sleep_hours * 60) if data.sleep_hours else 0,
                sleep_efficiency=data.sleep_efficiency,
                # Default values for other fields
                sedentary_minutes=0,
                lightly_active_minutes=0,
                fairly_active_minutes=0,
                deep_sleep_minutes=0,
                light_sleep_minutes=0,
                rem_sleep_minutes=0
            )
            
            db.add(new_activity)
            db.commit()
            db.refresh(new_activity)
            
            return {
                "status": "success",
                "message": f"Saved activity data for {data.date}",
                "data_created": True,
                "activity_id": new_activity.id
            }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save manual data: {str(e)}")

# Demo data endpoint
@app.post("/demo/generate-sample-data")
def generate_sample_data():
    """Generate sample data for demonstration purposes"""
    user_id = "demo_user_2024"
    
    users_db[user_id] = {
        "user_id": user_id,
        "name": "Louisiana Football Athlete",
        "email": "demo@aclguardian.com",
        "connected_devices": ["Fitbit", "Apple Watch"],
        "sport": "Football",
        "position": "Running Back"
    }
    
    return {
        "message": "Sample data generated successfully",
        "user_id": user_id,
        "demo_link": f"/user/{user_id}/risk-assessment"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
