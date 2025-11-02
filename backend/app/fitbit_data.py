"""
Fitbit API data fetching service.
Retrieves activity, heart rate, sleep, and intraday data.
"""

import httpx
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()

FITBIT_API_BASE_URL = os.getenv("FITBIT_API_BASE_URL", "https://api.fitbit.com")


class FitbitDataService:
    """Service for fetching data from Fitbit Web API."""
    
    def __init__(self, access_token: str):
        """
        Initialize Fitbit API client with access token.
        
        Args:
            access_token (str): Valid Fitbit OAuth access token
        """
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
    
    async def get_user_profile(self) -> Dict:
        """
        Get user profile information.
        
        Returns:
            dict: User profile data including user ID, name, etc.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FITBIT_API_BASE_URL}/1/user/-/profile.json",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()['user']
    
    async def get_activity_summary(self, date: date) -> Dict:
        """
        Get daily activity summary for a specific date.
        
        Args:
            date (date): Date to fetch activity for
        
        Returns:
            dict: Activity data including steps, distance, calories, active minutes
        """
        date_str = date.strftime('%Y-%m-%d')
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FITBIT_API_BASE_URL}/1/user/-/activities/date/{date_str}.json",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()['summary']
    
    async def get_heart_rate(self, date: date) -> Dict:
        """
        Get heart rate data for a specific date.
        
        Args:
            date (date): Date to fetch heart rate for
        
        Returns:
            dict: Heart rate zones and resting heart rate
        """
        date_str = date.strftime('%Y-%m-%d')
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FITBIT_API_BASE_URL}/1/user/-/activities/heart/date/{date_str}/1d.json",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('activities-heart'):
                return data['activities-heart'][0].get('value', {})
            return {}
    
    async def get_sleep(self, date: date) -> Dict:
        """
        Get sleep data for a specific date.
        
        Args:
            date (date): Date to fetch sleep for
        
        Returns:
            dict: Sleep stages, duration, and efficiency
        """
        date_str = date.strftime('%Y-%m-%d')
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FITBIT_API_BASE_URL}/1.2/user/-/sleep/date/{date_str}.json",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('sleep') and len(data['sleep']) > 0:
                return data['sleep'][0]  # Return main sleep session
            return {}
    
    async def get_intraday_steps(self, date: date, detail_level: str = "1min") -> List[Dict]:
        """
        Get minute-by-minute step data for a specific date.
        REQUIRES INTRADAY DATA ACCESS APPROVAL FROM FITBIT!
        
        Args:
            date (date): Date to fetch intraday data for
            detail_level (str): '1min', '5min', or '15min'
        
        Returns:
            list: List of timestamped step counts
        """
        date_str = date.strftime('%Y-%m-%d')
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{FITBIT_API_BASE_URL}/1/user/-/activities/steps/date/{date_str}/1d/{detail_level}.json",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                return data.get('activities-steps-intraday', {}).get('dataset', [])
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    # Intraday access not approved yet
                    print("⚠️  Intraday data access not approved. Apply at https://dev.fitbit.com/apps")
                    return []
                raise
    
    async def get_historical_activity(self, days: int = 14) -> List[Dict]:
        """
        Get activity data for the last N days.
        
        Args:
            days (int): Number of days to fetch (default 14)
        
        Returns:
            list: List of daily activity summaries
        """
        results = []
        today = date.today()
        
        for i in range(days):
            target_date = today - timedelta(days=i)
            
            try:
                activity = await self.get_activity_summary(target_date)
                heart_rate = await self.get_heart_rate(target_date)
                sleep = await self.get_sleep(target_date)
                
                results.append({
                    'date': target_date,
                    'activity': activity,
                    'heart_rate': heart_rate,
                    'sleep': sleep
                })
            except Exception as e:
                print(f"Error fetching data for {target_date}: {e}")
                continue
        
        return results


def calculate_cadence(steps: int, active_minutes: int) -> float:
    """
    Calculate average cadence (steps per minute during activity).
    
    Args:
        steps (int): Total steps for the day
        active_minutes (int): Total active minutes
    
    Returns:
        float: Average cadence (steps/min)
    """
    if active_minutes == 0:
        return 0.0
    return round(steps / active_minutes, 2)


def calculate_load_score(active_minutes: int, very_active_minutes: int) -> float:
    """
    Calculate load score based on activity intensity.
    Lower score = lower risk (good load management).
    
    Args:
        active_minutes (int): Total active minutes
        very_active_minutes (int): Very active minutes
    
    Returns:
        float: Load score (0-100)
    """
    # Ideal: 30-60 active minutes, <30% very active
    if active_minutes == 0:
        return 100.0  # No activity = high risk
    
    # Calculate intensity ratio
    intensity_ratio = (very_active_minutes / active_minutes) * 100 if active_minutes > 0 else 0
    
    # Optimal range: 45-60 active minutes, 20-30% very active
    if 45 <= active_minutes <= 60 and 20 <= intensity_ratio <= 30:
        return 20.0  # Low risk
    elif 30 <= active_minutes < 45:
        return 40.0  # Moderate-low risk
    elif active_minutes > 60:
        return 60.0  # Moderate-high risk (overload)
    else:
        return 80.0  # High risk (too little or too much)


def calculate_impact_score(heart_rate_zones: dict) -> float:
    """
    Calculate impact score from heart rate zones.
    
    Args:
        heart_rate_zones (dict): Heart rate zone data from Fitbit
    
    Returns:
        float: Impact score (0-100)
    """
    if not heart_rate_zones or 'heartRateZones' not in heart_rate_zones:
        return 50.0  # Default moderate risk
    
    zones = heart_rate_zones['heartRateZones']
    peak_minutes = sum(z.get('minutes', 0) for z in zones if z.get('name') == 'Peak')
    cardio_minutes = sum(z.get('minutes', 0) for z in zones if z.get('name') == 'Cardio')
    
    # Lower impact = lower risk
    total_high_intensity = peak_minutes + cardio_minutes
    
    if total_high_intensity < 20:
        return 30.0  # Low risk
    elif total_high_intensity < 40:
        return 50.0  # Moderate risk
    else:
        return 70.0  # Higher risk (high impact)


def calculate_consistency_score(sleep_efficiency: Optional[float], sleep_duration: Optional[int]) -> float:
    """
    Calculate consistency score based on sleep quality and recovery.
    
    Args:
        sleep_efficiency (float): Sleep efficiency percentage
        sleep_duration (int): Sleep duration in minutes
    
    Returns:
        float: Consistency score (0-100, lower = better)
    """
    if sleep_efficiency is None or sleep_duration is None:
        return 60.0  # Default moderate risk if no data
    
    # Ideal: >85% efficiency, 420-540 minutes (7-9 hours)
    if sleep_efficiency >= 85 and 420 <= sleep_duration <= 540:
        return 15.0  # Excellent recovery
    elif sleep_efficiency >= 75 and 360 <= sleep_duration <= 600:
        return 35.0  # Good recovery
    elif sleep_efficiency >= 65:
        return 55.0  # Fair recovery
    else:
        return 75.0  # Poor recovery = higher injury risk
