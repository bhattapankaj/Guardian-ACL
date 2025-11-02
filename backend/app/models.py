"""
Database models for ACL Guardian Fitbit integration.
Stores user information, Fitbit tokens, and activity data.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    """
    User model storing athlete information and encrypted Fitbit tokens.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)
    
    # Fitbit user identifier
    fitbit_user_id = Column(String, unique=True, index=True, nullable=False)
    
    # Encrypted OAuth tokens (NEVER store plain tokens!)
    access_token_encrypted = Column(Text, nullable=False)
    refresh_token_encrypted = Column(Text, nullable=False)
    
    # Token expiration tracking
    token_expires_at = Column(DateTime, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync_at = Column(DateTime, nullable=True)
    
    # Connection status
    is_active = Column(Boolean, default=True)
    
    # Relationship to activity data
    activity_data = relationship("ActivityData", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, fitbit_user_id={self.fitbit_user_id}, name={self.name})>"


class ActivityData(Base):
    """
    Daily activity data from Fitbit API.
    Stores aggregated metrics for ACL risk assessment.
    """
    __tablename__ = "activity_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Date of the activity data
    date = Column(DateTime, nullable=False, index=True)
    
    # Activity metrics
    steps = Column(Integer, default=0)
    distance = Column(Float, default=0.0)  # in kilometers
    calories = Column(Integer, default=0)
    active_minutes = Column(Integer, default=0)
    sedentary_minutes = Column(Integer, default=0)
    lightly_active_minutes = Column(Integer, default=0)
    fairly_active_minutes = Column(Integer, default=0)
    very_active_minutes = Column(Integer, default=0)
    
    # Heart rate data
    resting_heart_rate = Column(Integer, nullable=True)
    heart_rate_zones = Column(Text, nullable=True)  # JSON string
    
    # Sleep data
    sleep_duration_minutes = Column(Integer, nullable=True)
    sleep_efficiency = Column(Float, nullable=True)  # percentage
    deep_sleep_minutes = Column(Integer, nullable=True)
    light_sleep_minutes = Column(Integer, nullable=True)
    rem_sleep_minutes = Column(Integer, nullable=True)
    wake_minutes = Column(Integer, nullable=True)
    
    # Calculated ACL risk factors (computed from raw data)
    cadence_score = Column(Float, nullable=True)  # steps per minute during activity
    load_score = Column(Float, nullable=True)  # based on activity intensity
    impact_score = Column(Float, nullable=True)  # based on heart rate zones
    consistency_score = Column(Float, nullable=True)  # based on daily patterns
    asymmetry_score = Column(Float, nullable=True)  # from intraday data (if available)
    
    # Overall risk assessment
    total_risk_score = Column(Float, nullable=True)  # 0-100
    
    # Metadata
    synced_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="activity_data")

    def __repr__(self):
        return f"<ActivityData(user_id={self.user_id}, date={self.date}, steps={self.steps})>"


class IntradaySteps(Base):
    """
    Minute-by-minute step data for detailed cadence and asymmetry analysis.
    Only populated if Fitbit grants intraday data access.
    """
    __tablename__ = "intraday_steps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamp with minute precision
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Steps in this minute
    steps = Column(Integer, default=0)
    
    # Calculated metrics
    cadence = Column(Float, nullable=True)  # steps per minute
    
    # Metadata
    synced_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<IntradaySteps(user_id={self.user_id}, timestamp={self.timestamp}, steps={self.steps})>"


class SyncLog(Base):
    """
    Log of Fitbit data sync operations for debugging and monitoring.
    """
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Sync operation details
    sync_type = Column(String, nullable=False)  # 'activity', 'heart_rate', 'sleep', 'intraday'
    status = Column(String, nullable=False)  # 'success', 'error', 'partial'
    
    # Error information
    error_message = Column(Text, nullable=True)
    
    # Sync metrics
    records_synced = Column(Integer, default=0)
    sync_duration_seconds = Column(Float, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SyncLog(user_id={self.user_id}, sync_type={self.sync_type}, status={self.status})>"
