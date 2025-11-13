"""
Feedback API routes for ACL Guardian.
Handles storing and retrieving user feedback data from Supabase.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date as date_type
from supabase_client import store_feedback, get_user_feedback

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    """Request model for storing feedback."""
    user_id: str = Field(..., description="Unique user identifier")
    date: date_type = Field(..., description="Date of the activity")
    steps: Optional[int] = Field(None, description="Daily step count")
    active_minutes: Optional[int] = Field(None, description="Active minutes")
    resting_hr: Optional[float] = Field(None, description="Resting heart rate")
    peak_hr_minutes: Optional[int] = Field(None, description="Peak heart rate minutes")
    sleep_efficiency: Optional[float] = Field(None, description="Sleep efficiency percentage")
    minutes_asleep: Optional[int] = Field(None, description="Total minutes asleep")
    weight: Optional[float] = Field(None, description="Weight in kg")
    sport_type: Optional[str] = Field(None, description="Type of sport")
    acl_history: bool = Field(False, description="Previous ACL injury history")
    knee_pain: Optional[int] = Field(None, ge=0, le=10, description="Knee pain level (0-10)")
    formula_risk: float = Field(..., description="Calculated risk score from formula")
    feedback: bool = Field(..., description="User feedback (true=accurate, false=inaccurate)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "date": "2025-11-13",
                "steps": 8500,
                "active_minutes": 45,
                "resting_hr": 65.0,
                "peak_hr_minutes": 20,
                "sleep_efficiency": 85.5,
                "minutes_asleep": 420,
                "weight": 70.5,
                "sport_type": "football",
                "acl_history": False,
                "knee_pain": 2,
                "formula_risk": 0.35,
                "feedback": True
            }
        }


class FeedbackResponse(BaseModel):
    """Response model for feedback operations."""
    success: bool
    message: str
    data: Optional[dict] = None


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(feedback_req: FeedbackRequest):
    """
    Store new feedback record in Supabase.
    
    This endpoint receives user feedback on risk predictions and stores it
    for future model training.
    """
    try:
        # Convert Pydantic model to dict
        feedback_data = feedback_req.model_dump()
        
        # Convert date to string for Supabase
        feedback_data['date'] = feedback_data['date'].isoformat()
        
        # Store in Supabase
        result = store_feedback(feedback_data)
        
        return FeedbackResponse(
            success=True,
            message="Feedback stored successfully",
            data=result
        )
    except Exception as e:
        print(f"❌ Error in create_feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store feedback: {str(e)}"
        )


@router.get("/{user_id}", response_model=List[dict])
async def get_feedback_history(user_id: str, limit: int = 100):
    """
    Retrieve feedback history for a specific user.
    
    Returns the most recent feedback entries for the given user ID.
    """
    try:
        # Validate limit
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 1000"
            )
        
        # Get feedback from Supabase
        feedback_history = get_user_feedback(user_id, limit)
        
        if not feedback_history:
            return []
        
        return feedback_history
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_feedback_history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve feedback: {str(e)}"
        )


@router.get("/stats/{user_id}")
async def get_feedback_stats(user_id: str):
    """
    Get feedback statistics for a user.
    
    Returns summary statistics about user's feedback history.
    """
    try:
        feedback_history = get_user_feedback(user_id, limit=1000)
        
        if not feedback_history:
            return {
                "user_id": user_id,
                "total_entries": 0,
                "positive_feedback": 0,
                "negative_feedback": 0,
                "accuracy_rate": 0.0
            }
        
        total = len(feedback_history)
        positive = sum(1 for entry in feedback_history if entry.get('feedback') is True)
        negative = total - positive
        accuracy_rate = (positive / total * 100) if total > 0 else 0.0
        
        return {
            "user_id": user_id,
            "total_entries": total,
            "positive_feedback": positive,
            "negative_feedback": negative,
            "accuracy_rate": round(accuracy_rate, 2),
            "latest_entry": feedback_history[0].get('date') if feedback_history else None
        }
    except Exception as e:
        print(f"❌ Error in get_feedback_stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve feedback stats: {str(e)}"
        )
