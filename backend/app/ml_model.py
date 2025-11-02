"""
ACL Injury Risk ML Model
Based on biomechanical research and activity pattern analysis
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import joblib
import os

class ACLRiskModel:
    """
    ML Model for predicting ACL injury risk based on Fitbit activity data.
    
    Risk factors analyzed:
    - Step asymmetry (biomechanical imbalance)
    - Cadence variability (movement inconsistency)
    - Training load spikes (sudden volume increases)
    - Fatigue indicators (poor recovery)
    - Activity consistency (irregular training patterns)
    """
    
    def __init__(self, model_path=None):
        self.scaler = StandardScaler()
        self.model = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize a pre-trained model with research-based parameters"""
        # Gradient Boosting is effective for injury prediction
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        # Pre-train with synthetic data based on ACL injury research
        self._pretrain_model()
    
    def _pretrain_model(self):
        """
        Pre-train model with synthetic data based on ACL injury research literature:
        - Asymmetry > 10% increases risk
        - Load spikes > 30% increase risk
        - Cadence variance > 15% increases risk
        """
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic training data
        X = []
        y = []
        
        for _ in range(n_samples):
            # Low risk profile
            if np.random.rand() < 0.7:
                step_asymmetry = np.random.uniform(0, 8)  # Low asymmetry
                cadence_variance = np.random.uniform(5, 12)  # Low variance
                load_spike = np.random.uniform(0, 20)  # Gradual increase
                fatigue_score = np.random.uniform(0, 30)  # Well-rested
                consistency = np.random.uniform(70, 95)  # Very consistent
                risk = 0  # Low risk
            else:
                # High risk profile
                step_asymmetry = np.random.uniform(10, 25)  # High asymmetry
                cadence_variance = np.random.uniform(15, 30)  # High variance
                load_spike = np.random.uniform(30, 60)  # Sudden spike
                fatigue_score = np.random.uniform(50, 90)  # Fatigued
                consistency = np.random.uniform(20, 50)  # Inconsistent
                risk = 1  # High risk
            
            X.append([step_asymmetry, cadence_variance, load_spike, fatigue_score, consistency])
            y.append(risk)
        
        X = np.array(X)
        y = np.array(y)
        
        # Fit scaler and model
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
    
    def extract_features(self, activity_data: list) -> dict:
        """
        Extract ML features from Fitbit activity data.
        
        Args:
            activity_data: List of ActivityData objects from last 14 days
        
        Returns:
            dict: Extracted features for risk prediction
        """
        if not activity_data or len(activity_data) < 3:
            return self._default_features()
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([{
            'date': d.date,
            'steps': d.steps or 0,
            'distance': d.distance or 0,
            'calories': d.calories or 0,
            'heart_rate': d.heart_rate or 70,
            'sleep_minutes': d.sleep_minutes or 420,
        } for d in activity_data])
        
        # Feature 1: Step Asymmetry (estimated from step variance)
        step_asymmetry = self._calculate_step_asymmetry(df)
        
        # Feature 2: Cadence Variability
        cadence_variance = self._calculate_cadence_variance(df)
        
        # Feature 3: Training Load Spike
        load_spike = self._calculate_load_spike(df)
        
        # Feature 4: Fatigue Score
        fatigue_score = self._calculate_fatigue_score(df)
        
        # Feature 5: Activity Consistency
        consistency = self._calculate_consistency(df)
        
        return {
            'step_asymmetry': step_asymmetry,
            'cadence_variance': cadence_variance,
            'load_spike': load_spike,
            'fatigue_score': fatigue_score,
            'consistency': consistency,
        }
    
    def _calculate_step_asymmetry(self, df: pd.DataFrame) -> float:
        """
        Estimate step asymmetry from day-to-day step variance.
        High variance suggests inconsistent gait patterns.
        """
        if len(df) < 2:
            return 0.0
        
        step_std = df['steps'].std()
        step_mean = df['steps'].mean() if df['steps'].mean() > 0 else 1
        asymmetry = (step_std / step_mean) * 100
        
        return min(asymmetry, 25.0)  # Cap at 25%
    
    def _calculate_cadence_variance(self, df: pd.DataFrame) -> float:
        """
        Calculate cadence variance from distance/steps ratio.
        High variance indicates inconsistent pace.
        """
        df['cadence'] = df['steps'] / (df['distance'] + 1)  # Avoid division by zero
        cadence_cv = (df['cadence'].std() / df['cadence'].mean()) * 100 if df['cadence'].mean() > 0 else 10
        
        return min(cadence_cv, 30.0)  # Cap at 30%
    
    def _calculate_load_spike(self, df: pd.DataFrame) -> float:
        """
        Detect sudden training load increases.
        Compare recent week vs previous week.
        """
        if len(df) < 7:
            return 0.0
        
        recent_week = df.tail(7)['steps'].sum()
        previous_week = df.iloc[-14:-7]['steps'].sum() if len(df) >= 14 else recent_week
        
        if previous_week == 0:
            return 0.0
        
        spike = ((recent_week - previous_week) / previous_week) * 100
        
        return max(0, min(spike, 60.0))  # Clamp between 0-60%
    
    def _calculate_fatigue_score(self, df: pd.DataFrame) -> float:
        """
        Estimate fatigue from heart rate and sleep patterns.
        Higher score = more fatigued.
        """
        # Poor sleep increases fatigue
        avg_sleep = df['sleep_minutes'].mean()
        sleep_deficit = max(0, 420 - avg_sleep)  # 420 min = 7 hours
        sleep_penalty = (sleep_deficit / 420) * 50
        
        # Elevated resting HR suggests fatigue
        avg_hr = df['heart_rate'].mean()
        hr_penalty = max(0, (avg_hr - 65) / 65) * 30
        
        fatigue = sleep_penalty + hr_penalty
        
        return min(fatigue, 90.0)  # Cap at 90
    
    def _calculate_consistency(self, df: pd.DataFrame) -> float:
        """
        Calculate training consistency score.
        Higher = more consistent (better).
        """
        # Count days with activity
        active_days = (df['steps'] > 3000).sum()
        total_days = len(df)
        
        consistency = (active_days / total_days) * 100 if total_days > 0 else 0
        
        return consistency
    
    def _default_features(self) -> dict:
        """Return default features when insufficient data"""
        return {
            'step_asymmetry': 5.0,
            'cadence_variance': 10.0,
            'load_spike': 0.0,
            'fatigue_score': 20.0,
            'consistency': 70.0,
        }
    
    def predict_risk(self, features: dict) -> dict:
        """
        Predict ACL injury risk from extracted features.
        
        Args:
            features: Dictionary of extracted features
        
        Returns:
            dict: Risk prediction with score and breakdown
        """
        # Convert features to array
        X = np.array([[
            features['step_asymmetry'],
            features['cadence_variance'],
            features['load_spike'],
            features['fatigue_score'],
            100 - features['consistency'],  # Invert: lower consistency = higher risk
        ]])
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get probability of high risk
        risk_prob = self.model.predict_proba(X_scaled)[0][1]
        
        # Convert to 0-100 risk score
        risk_score = int(risk_prob * 100)
        
        # Determine risk level
        if risk_score < 30:
            risk_level = "LOW"
            risk_color = "green"
        elif risk_score < 60:
            risk_level = "MODERATE"
            risk_color = "yellow"
        else:
            risk_level = "HIGH"
            risk_color = "red"
        
        # Calculate component scores
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'components': {
                'asymmetry': int((features['step_asymmetry'] / 25) * 100),
                'cadence': int((features['cadence_variance'] / 30) * 100),
                'load': int((features['load_spike'] / 60) * 100),
                'fatigue': int((features['fatigue_score'] / 90) * 100),
                'consistency': int(features['consistency']),
            },
            'recommendations': self._generate_recommendations(features, risk_score)
        }
    
    def _generate_recommendations(self, features: dict, risk_score: int) -> list:
        """Generate personalized recommendations based on risk factors"""
        recommendations = []
        
        if features['step_asymmetry'] > 10:
            recommendations.append("High step asymmetry detected. Consider gait analysis or physical therapy.")
        
        if features['load_spike'] > 30:
            recommendations.append("Sudden training load increase. Gradually increase volume by <10% per week.")
        
        if features['fatigue_score'] > 50:
            recommendations.append("Fatigue indicators high. Prioritize recovery and sleep (7-9 hours).")
        
        if features['consistency'] < 50:
            recommendations.append("Inconsistent training pattern. Maintain regular activity schedule.")
        
        if risk_score < 30:
            recommendations.append("Great job! Your training pattern shows low injury risk.")
        
        return recommendations
    
    def save_model(self, path: str):
        """Save trained model to disk"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, path)
    
    def load_model(self, path: str):
        """Load trained model from disk"""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']


# Global model instance
_model_instance = None

def get_model() -> ACLRiskModel:
    """Get singleton model instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = ACLRiskModel()
    return _model_instance
