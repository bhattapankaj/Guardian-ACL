"""
Prediction API routes for ACL Guardian.
Handles risk score predictions using ML model or formula fallback.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import joblib
import os
import numpy as np
from supabase_client import download_model_from_storage, model_exists_in_storage

router = APIRouter(prefix="/predict", tags=["Prediction"])


class PredictRequest(BaseModel):
    """Request model for ACL risk prediction."""
    user_id: str = Field(..., description="Unique user identifier")
    steps: Optional[int] = Field(None, description="Daily step count")
    active_minutes: Optional[int] = Field(None, description="Active minutes")
    resting_hr: Optional[float] = Field(None, description="Resting heart rate")
    peak_hr_minutes: Optional[int] = Field(None, description="Peak heart rate minutes")
    sleep_efficiency: Optional[float] = Field(None, description="Sleep efficiency percentage (0-100)")
    minutes_asleep: Optional[int] = Field(None, description="Total minutes asleep")
    weight: Optional[float] = Field(None, description="Weight in kg")
    sport_type: Optional[str] = Field(None, description="Type of sport")
    acl_history: bool = Field(False, description="Previous ACL injury history")
    knee_pain: Optional[int] = Field(0, ge=0, le=10, description="Knee pain level (0-10)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "steps": 8500,
                "active_minutes": 45,
                "resting_hr": 65.0,
                "peak_hr_minutes": 20,
                "sleep_efficiency": 85.5,
                "minutes_asleep": 420,
                "weight": 70.5,
                "sport_type": "football",
                "acl_history": False,
                "knee_pain": 2
            }
        }


class PredictResponse(BaseModel):
    """Response model for risk prediction."""
    user_id: str
    risk_score: float = Field(..., description="Risk score (0-1 range)")
    risk_level: str = Field(..., description="Risk level: low, moderate, or high")
    method: str = Field(..., description="Prediction method: ml_model or formula")
    confidence: Optional[float] = Field(None, description="Model confidence (for ML predictions)")
    recommendations: list[str] = Field(default_factory=list, description="Risk mitigation recommendations")


def calculate_formula_risk(data: PredictRequest) -> float:
    """
    Calculate ACL injury risk using weighted formula (fallback method).
    
    Formula:
    risk_score = 0.4*(resting_hr/100) + 0.3*(active_minutes/60) + 
                 0.2*(sleep_efficiency/100) + 0.1*(knee_pain/10)
    
    Normalized to range [0, 1]
    """
    # Default values if metrics are missing
    resting_hr = data.resting_hr or 70.0
    active_minutes = data.active_minutes or 30
    sleep_efficiency = data.sleep_efficiency or 85.0
    knee_pain = data.knee_pain or 0
    
    # Calculate weighted risk
    risk = (
        0.4 * (resting_hr / 100) +
        0.3 * (active_minutes / 60) +
        0.2 * (sleep_efficiency / 100) +
        0.1 * (knee_pain / 10)
    )
    
    # Adjust for ACL history (increases risk by 30%)
    if data.acl_history:
        risk *= 1.3
    
    # Normalize to 0-1 range
    risk = min(max(risk, 0.0), 1.0)
    
    return risk


def load_ml_model(user_id: str) -> Optional[object]:
    """
    Load ML model from Supabase Storage if it exists.
    Returns model object or None if not found.
    """
    try:
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        local_model_path = f"models/user_{user_id}.pkl"
        
        # Try to download from Supabase Storage
        if download_model_from_storage(user_id, local_model_path):
            # Load the model
            model = joblib.load(local_model_path)
            print(f"✅ Loaded ML model for user {user_id}")
            return model
        else:
            return None
    except Exception as e:
        print(f"⚠️ Could not load ML model: {e}")
        return None


def predict_with_model(model, data: PredictRequest) -> tuple[float, float]:
    """
    Make prediction using trained ML model.
    Returns (risk_score, confidence)
    """
    try:
        # Prepare features (must match training data structure)
        features = np.array([[
            data.steps or 0,
            data.active_minutes or 0,
            data.resting_hr or 70.0,
            data.peak_hr_minutes or 0,
            data.sleep_efficiency or 85.0,
            data.minutes_asleep or 0,
            data.weight or 70.0,
            1 if data.acl_history else 0,
            data.knee_pain or 0
        ]])
        
        # Make prediction
        risk_score = model.predict(features)[0]
        
        # Get confidence (if model supports it)
        confidence = 0.85  # Default confidence
        if hasattr(model, 'predict_proba'):
            try:
                proba = model.predict_proba(features)[0]
                confidence = max(proba)
            except:
                pass
        
        return float(risk_score), float(confidence)
    except Exception as e:
        print(f"⚠️ Error during ML prediction: {e}")
        raise


def get_risk_level(risk_score: float) -> str:
    """Convert risk score to risk level."""
    if risk_score < 0.3:
        return "low"
    elif risk_score < 0.6:
        return "moderate"
    else:
        return "high"


def get_recommendations(risk_score: float, data: PredictRequest) -> list[str]:
    """Generate personalized recommendations based on risk factors."""
    recommendations = []
    
    # High risk recommendations
    if risk_score >= 0.6:
        recommendations.append("⚠️ HIGH RISK: Consider consulting a sports medicine professional")
        recommendations.append("Reduce training intensity by 20-30% for the next week")
    
    # Knee pain specific
    if data.knee_pain and data.knee_pain > 5:
        recommendations.append("🦵 Significant knee pain detected - schedule medical evaluation")
        recommendations.append("Avoid high-impact activities until pain subsides")
    
    # Sleep recommendations
    if data.sleep_efficiency and data.sleep_efficiency < 75:
        recommendations.append("😴 Poor sleep quality - prioritize 8+ hours of quality sleep")
        recommendations.append("Consider sleep hygiene improvements and recovery protocols")
    
    # Activity recommendations
    if data.active_minutes and data.active_minutes > 90:
        recommendations.append("🏃 High training volume - ensure adequate rest days")
        recommendations.append("Incorporate active recovery and mobility work")
    
    # Heart rate recommendations
    if data.resting_hr and data.resting_hr > 75:
        recommendations.append("❤️ Elevated resting heart rate - may indicate overtraining or fatigue")
        recommendations.append("Take an extra rest day and monitor recovery metrics")
    
    # ACL history specific
    if data.acl_history:
        recommendations.append("🔄 Previous ACL injury - maintain neuromuscular training program")
        recommendations.append("Focus on hamstring strengthening and landing mechanics")
    
    # General recommendations
    if risk_score < 0.3:
        recommendations.append("✅ Low risk - maintain current training load and recovery practices")
    elif risk_score < 0.6:
        recommendations.append("⚡ Moderate risk - monitor fatigue and adjust training as needed")
    
    # Always include prevention basics
    recommendations.append("🔧 Continue ACL injury prevention exercises (FIFA 11+, PEP program)")
    
    return recommendations


@router.post("/", response_model=PredictResponse)
async def predict_acl_risk(data: PredictRequest):
    """
    Predict ACL injury risk score.
    
    Attempts to use trained ML model if available, otherwise falls back to formula.
    Returns risk score (0-1), risk level, and personalized recommendations.
    """
    try:
        risk_score = None
        method = "formula"
        confidence = None
        
        # Try to use ML model first
        model = load_ml_model(data.user_id)
        
        if model is not None:
            try:
                risk_score, confidence = predict_with_model(model, data)
                method = "ml_model"
                print(f"✅ Switched to ML model prediction for user {data.user_id}")
            except Exception as e:
                print(f"⚠️ ML prediction failed, falling back to formula: {e}")
                risk_score = None
        
        # Fallback to formula if ML model not available or failed
        if risk_score is None:
            risk_score = calculate_formula_risk(data)
            method = "formula"
            print(f"📊 Using formula-based prediction for user {data.user_id}")
        
        # Get risk level and recommendations
        risk_level = get_risk_level(risk_score)
        recommendations = get_recommendations(risk_score, data)
        
        return PredictResponse(
            user_id=data.user_id,
            risk_score=round(risk_score, 3),
            risk_level=risk_level,
            method=method,
            confidence=round(confidence, 3) if confidence else None,
            recommendations=recommendations
        )
    
    except Exception as e:
        print(f"❌ Error in predict_acl_risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/health")
async def prediction_health():
    """Health check endpoint for prediction service."""
    return {
        "status": "healthy",
        "service": "ACL Risk Prediction",
        "methods": ["ml_model", "formula"]
    }
