"""
REAL ML Model Training Pipeline for ACL Guardian
Train on actual user data with injury outcomes
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix
)
import joblib
import os
from datetime import datetime, timedelta
from typing import List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class ACLModelTrainer:
    """
    Real training pipeline for ACL injury prediction model.
    
    This trainer:
    1. Collects real user data from database
    2. Engineers features from activity patterns
    3. Trains multiple models with hyperparameter tuning
    4. Validates with cross-validation
    5. Selects best model based on recall (minimize false negatives)
    6. Saves trained model for production use
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.best_model = None
        self.best_score = 0
        self.training_history = []
        
    def collect_training_data(self, db_session) -> pd.DataFrame:
        """
        Collect real training data from database.
        
        For REAL training, you need:
        1. User activity data (steps, HR, sleep, distance)
        2. Injury outcomes (did user get injured? when?)
        3. Time period before injury (14-30 days)
        
        Returns:
            DataFrame with features and labels
        """
        from app.models import User, ActivityData, InjuryRecord
        
        # Query users with injury records
        users_with_injuries = db_session.query(User).join(InjuryRecord).all()
        
        training_samples = []
        
        for user in users_with_injuries:
            # Get injury records for this user
            injuries = db_session.query(InjuryRecord).filter(
                InjuryRecord.user_id == user.id
            ).all()
            
            for injury in injuries:
                injury_date = injury.injury_date
                
                # Get activity data 14-30 days BEFORE injury
                lookback_start = injury_date - timedelta(days=30)
                lookback_end = injury_date - timedelta(days=14)
                
                activities = db_session.query(ActivityData).filter(
                    ActivityData.user_id == user.id,
                    ActivityData.date >= lookback_start,
                    ActivityData.date < lookback_end
                ).order_by(ActivityData.date).all()
                
                if len(activities) >= 10:  # Need enough data
                    # Extract features from this period
                    features = self._extract_features_from_activities(activities)
                    features['label'] = 1  # This led to injury
                    training_samples.append(features)
        
        # Also collect negative samples (users who DIDN'T get injured)
        healthy_users = db_session.query(User).filter(
            ~User.id.in_([u.id for u in users_with_injuries])
        ).limit(len(training_samples) * 2).all()  # 2:1 ratio
        
        for user in healthy_users:
            # Get random 14-day periods from healthy users
            activities = db_session.query(ActivityData).filter(
                ActivityData.user_id == user.id
            ).order_by(ActivityData.date).limit(14).all()
            
            if len(activities) >= 10:
                features = self._extract_features_from_activities(activities)
                features['label'] = 0  # No injury
                training_samples.append(features)
        
        return pd.DataFrame(training_samples)
    
    def _extract_features_from_activities(self, activities: list) -> dict:
        """
        Extract the same 5 features used in prediction.
        
        Features:
        1. Step asymmetry - day-to-day step variance
        2. Cadence variance - inconsistent pace
        3. Training load spike - sudden volume increase
        4. Fatigue score - poor recovery indicators
        5. Activity consistency - training regularity
        """
        # Convert to DataFrame for easier processing
        df = pd.DataFrame([{
            'date': a.date,
            'steps': a.steps,
            'distance': a.distance,
            'heart_rate': a.heart_rate_avg,
            'sleep_hours': a.sleep_hours or 7.0  # Default if missing
        } for a in activities])
        
        # Feature 1: Step Asymmetry
        step_std = df['steps'].std()
        step_mean = df['steps'].mean()
        step_asymmetry = (step_std / step_mean * 100) if step_mean > 0 else 0
        
        # Feature 2: Cadence Variance
        df['cadence'] = df['distance'] / (df['steps'] / 1000) if df['steps'].mean() > 0 else 0
        cadence_variance = (df['cadence'].std() / df['cadence'].mean() * 100) if df['cadence'].mean() > 0 else 0
        
        # Feature 3: Training Load Spike
        df_sorted = df.sort_values('date')
        first_week = df_sorted.head(7)['steps'].sum()
        second_week = df_sorted.tail(7)['steps'].sum()
        load_spike = ((second_week - first_week) / first_week * 100) if first_week > 0 else 0
        
        # Feature 4: Fatigue Score
        hr_penalty = max(0, (df['heart_rate'].mean() - 60) / 60 * 50) if df['heart_rate'].mean() > 0 else 0
        sleep_penalty = max(0, (7 - df['sleep_hours'].mean()) / 7 * 50)
        fatigue_score = hr_penalty + sleep_penalty
        
        # Feature 5: Consistency
        active_days = len(df[df['steps'] > 5000])
        consistency = (active_days / len(df) * 100)
        
        return {
            'step_asymmetry': step_asymmetry,
            'cadence_variance': cadence_variance,
            'load_spike': load_spike,
            'fatigue_score': fatigue_score,
            'consistency': consistency
        }
    
    def train_models(self, X_train, y_train, X_val, y_val) -> dict:
        """
        Train multiple models and compare performance.
        
        Models tested:
        - Gradient Boosting (current)
        - Random Forest
        - AdaBoost
        - Logistic Regression
        
        Returns best model based on recall score.
        """
        models = {
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=6,
                random_state=42
            ),
            'Random Forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                random_state=42
            ),
            'AdaBoost': AdaBoostClassifier(
                n_estimators=100,
                random_state=42
            ),
            'Logistic Regression': LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        }
        
        results = {}
        
        for name, model in models.items():
            print(f"\n🔧 Training {name}...")
            
            # Train
            model.fit(X_train, y_train)
            
            # Predict
            y_pred = model.predict(X_val)
            y_pred_proba = model.predict_proba(X_val)[:, 1]
            
            # Evaluate
            accuracy = accuracy_score(y_val, y_pred)
            precision = precision_score(y_val, y_pred, zero_division=0)
            recall = recall_score(y_val, y_pred, zero_division=0)
            f1 = f1_score(y_val, y_pred, zero_division=0)
            auc = roc_auc_score(y_val, y_pred_proba)
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,  # MOST IMPORTANT - don't miss injuries!
                'f1': f1,
                'auc': auc
            }
            
            print(f"  Accuracy:  {accuracy:.3f}")
            print(f"  Precision: {precision:.3f}")
            print(f"  Recall:    {recall:.3f} ⭐ (minimize false negatives)")
            print(f"  F1 Score:  {f1:.3f}")
            print(f"  AUC-ROC:   {auc:.3f}")
        
        # Select best model based on RECALL (we want to catch all potential injuries)
        best_model_name = max(results, key=lambda k: results[k]['recall'])
        self.best_model = results[best_model_name]['model']
        self.best_score = results[best_model_name]['recall']
        
        print(f"\n🏆 Best Model: {best_model_name} (Recall: {self.best_score:.3f})")
        
        return results
    
    def hyperparameter_tuning(self, X_train, y_train) -> GradientBoostingClassifier:
        """
        Fine-tune the best model with GridSearchCV.
        
        This takes TIME but improves accuracy!
        """
        print("\n🔬 Hyperparameter tuning (this may take 10-30 minutes)...")
        
        param_grid = {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [3, 5, 7],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        grid_search = GridSearchCV(
            GradientBoostingClassifier(random_state=42),
            param_grid,
            cv=5,
            scoring='recall',  # Optimize for recall
            n_jobs=-1,
            verbose=2
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"\n✅ Best parameters: {grid_search.best_params_}")
        print(f"✅ Best cross-validation recall: {grid_search.best_score_:.3f}")
        
        return grid_search.best_estimator_
    
    def train_full_pipeline(self, db_session, use_tuning=True) -> dict:
        """
        Complete training pipeline from data collection to model saving.
        
        Steps:
        1. Collect training data from database
        2. Split into train/validation/test sets
        3. Scale features
        4. Train multiple models
        5. (Optional) Hyperparameter tuning
        6. Validate on test set
        7. Save best model
        
        Returns:
            dict with training results
        """
        print("=" * 80)
        print("🧠 ACL INJURY PREDICTION MODEL - REAL TRAINING PIPELINE")
        print("=" * 80)
        
        # Step 1: Collect data
        print("\n📊 Step 1: Collecting training data from database...")
        df = self.collect_training_data(db_session)
        
        if len(df) < 50:
            raise ValueError(
                f"Not enough training data! Found {len(df)} samples, need at least 50.\n"
                "Collect more user data with injury outcomes to train the model."
            )
        
        print(f"✅ Collected {len(df)} training samples")
        print(f"   - Injured cases: {df['label'].sum()}")
        print(f"   - Healthy cases: {len(df) - df['label'].sum()}")
        
        # Step 2: Split data
        print("\n📊 Step 2: Splitting into train/val/test sets...")
        feature_cols = ['step_asymmetry', 'cadence_variance', 'load_spike', 
                       'fatigue_score', 'consistency']
        X = df[feature_cols].values
        y = df['label'].values
        
        # 70% train, 15% validation, 15% test
        X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
        X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.176, random_state=42)
        
        print(f"✅ Train: {len(X_train)}, Validation: {len(X_val)}, Test: {len(X_test)}")
        
        # Step 3: Scale features
        print("\n📊 Step 3: Scaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        print("✅ Features scaled")
        
        # Step 4: Train models
        print("\n📊 Step 4: Training multiple models...")
        results = self.train_models(X_train_scaled, y_train, X_val_scaled, y_val)
        
        # Step 5: Hyperparameter tuning (optional)
        if use_tuning:
            print("\n📊 Step 5: Hyperparameter tuning...")
            self.best_model = self.hyperparameter_tuning(X_train_scaled, y_train)
        else:
            print("\n⏭️  Step 5: Skipped hyperparameter tuning (set use_tuning=True to enable)")
        
        # Step 6: Final validation on test set
        print("\n📊 Step 6: Final validation on test set...")
        y_pred = self.best_model.predict(X_test_scaled)
        y_pred_proba = self.best_model.predict_proba(X_test_scaled)[:, 1]
        
        test_accuracy = accuracy_score(y_test, y_pred)
        test_precision = precision_score(y_test, y_pred, zero_division=0)
        test_recall = recall_score(y_test, y_pred, zero_division=0)
        test_f1 = f1_score(y_test, y_pred, zero_division=0)
        test_auc = roc_auc_score(y_test, y_pred_proba)
        
        print("\n" + "=" * 80)
        print("🎯 FINAL TEST SET PERFORMANCE")
        print("=" * 80)
        print(f"Accuracy:  {test_accuracy:.3f}")
        print(f"Precision: {test_precision:.3f}")
        print(f"Recall:    {test_recall:.3f} ⭐")
        print(f"F1 Score:  {test_f1:.3f}")
        print(f"AUC-ROC:   {test_auc:.3f}")
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['No Injury', 'Injury']))
        
        # Step 7: Save model
        print("\n📊 Step 7: Saving trained model...")
        model_path = 'acl_risk_model_trained.pkl'
        scaler_path = 'acl_risk_scaler.pkl'
        
        joblib.dump(self.best_model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        print(f"✅ Model saved to: {model_path}")
        print(f"✅ Scaler saved to: {scaler_path}")
        
        return {
            'test_accuracy': test_accuracy,
            'test_precision': test_precision,
            'test_recall': test_recall,
            'test_f1': test_f1,
            'test_auc': test_auc,
            'model_path': model_path,
            'scaler_path': scaler_path,
            'training_samples': len(df),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }


# Example usage:
if __name__ == "__main__":
    """
    HOW TO TRAIN THE MODEL:
    
    1. Collect real user data with injury outcomes
    2. Add InjuryRecord model to database
    3. Run this script to train
    4. Replace the pre-trained model in ml_model.py
    """
    
    # This is a DEMO - you need real database connection
    print("""
    ⚠️  TO TRAIN ON REAL DATA:
    
    1. Create InjuryRecord table in database:
       - user_id
       - injury_date
       - injury_type (ACL tear, sprain, etc.)
       
    2. Collect data from users:
       - 14-30 days activity BEFORE injury
       - Mark injury outcomes
       - Get healthy user data too
       
    3. Run this training pipeline:
       from train_model import ACLModelTrainer
       from app.database import SessionLocal
       
       db = SessionLocal()
       trainer = ACLModelTrainer()
       results = trainer.train_full_pipeline(db, use_tuning=True)
       
    4. Replace model in production:
       - Copy acl_risk_model_trained.pkl
       - Update ml_model.py to load it
       
    ⏱️  Training time: 30 minutes - 2 hours (depends on data size)
    🎯 Goal: >90% recall (catch all potential injuries)
    """)
