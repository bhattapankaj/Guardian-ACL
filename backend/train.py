"""
Model training module for ACL Guardian.
Handles automated training of RandomForest model on positive feedback data.
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from datetime import datetime
from supabase_client import get_positive_feedback, upload_model_to_storage
from typing import Optional, Tuple


# Minimum number of positive feedback entries required for training
MIN_FEEDBACK_COUNT = 100

# Model parameters
MODEL_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42,
    'n_jobs': -1
}


def prepare_training_data(feedback_data: list) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare training data from feedback entries.
    
    Args:
        feedback_data: List of feedback dictionaries from Supabase
        
    Returns:
        Tuple of (X_features, y_target)
    """
    # Convert to DataFrame
    df = pd.DataFrame(feedback_data)
    
    # Select feature columns
    feature_columns = [
        'steps',
        'active_minutes',
        'resting_hr',
        'peak_hr_minutes',
        'sleep_efficiency',
        'minutes_asleep',
        'weight',
        'acl_history',
        'knee_pain'
    ]
    
    # Fill missing values with defaults
    df['steps'] = df['steps'].fillna(0)
    df['active_minutes'] = df['active_minutes'].fillna(0)
    df['resting_hr'] = df['resting_hr'].fillna(70.0)
    df['peak_hr_minutes'] = df['peak_hr_minutes'].fillna(0)
    df['sleep_efficiency'] = df['sleep_efficiency'].fillna(85.0)
    df['minutes_asleep'] = df['minutes_asleep'].fillna(0)
    df['weight'] = df['weight'].fillna(70.0)
    df['acl_history'] = df['acl_history'].fillna(False).astype(int)
    df['knee_pain'] = df['knee_pain'].fillna(0)
    
    # Extract features and target
    X = df[feature_columns]
    y = df['formula_risk']  # Use formula_risk as the target to learn from
    
    return X, y


def train_model(user_id: str = "global") -> Optional[dict]:
    """
    Train RandomForest model on positive feedback data.
    
    Args:
        user_id: User ID to train model for (default: "global" for all users)
        
    Returns:
        Dictionary with training results or None if insufficient data
    """
    print(f"\n{'='*60}")
    print(f"🎯 TRAINING STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        # Get positive feedback data from Supabase
        print("📊 Fetching positive feedback data from Supabase...")
        feedback_data = get_positive_feedback(min_count=MIN_FEEDBACK_COUNT)
        
        # Check if we have enough data
        if len(feedback_data) < MIN_FEEDBACK_COUNT:
            print(f"⚠️ Insufficient data: {len(feedback_data)}/{MIN_FEEDBACK_COUNT} entries")
            print("   Skipping training - need more positive feedback")
            return None
        
        print(f"✅ Found {len(feedback_data)} positive feedback entries")
        
        # Prepare training data
        print("🔧 Preparing training data...")
        X, y = prepare_training_data(feedback_data)
        
        print(f"   Features shape: {X.shape}")
        print(f"   Target shape: {y.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"   Train set: {X_train.shape[0]} samples")
        print(f"   Test set: {X_test.shape[0]} samples")
        
        # Train model
        print(f"\n🤖 Training RandomForest model...")
        print(f"   Parameters: {MODEL_PARAMS}")
        
        model = RandomForestRegressor(**MODEL_PARAMS)
        model.fit(X_train, y_train)
        
        # Evaluate model
        print("\n📈 Evaluating model performance...")
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_mse = mean_squared_error(y_train, train_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        print(f"   Train MSE: {train_mse:.4f}")
        print(f"   Test MSE: {test_mse:.4f}")
        print(f"   Train R²: {train_r2:.4f}")
        print(f"   Test R²: {test_r2:.4f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n🔍 Feature Importance:")
        for idx, row in feature_importance.iterrows():
            print(f"   {row['feature']:20s}: {row['importance']:.4f}")
        
        # Save model locally
        os.makedirs('models', exist_ok=True)
        local_model_path = f"models/user_{user_id}.pkl"
        joblib.dump(model, local_model_path)
        print(f"\n💾 Model saved locally: {local_model_path}")
        
        # Upload to Supabase Storage
        print("☁️  Uploading model to Supabase Storage...")
        storage_path = upload_model_to_storage(user_id, local_model_path)
        print(f"✅ Model uploaded successfully: {storage_path}")
        
        # Training results
        results = {
            'success': True,
            'user_id': user_id,
            'training_date': datetime.now().isoformat(),
            'data_points': len(feedback_data),
            'train_size': X_train.shape[0],
            'test_size': X_test.shape[0],
            'train_mse': float(train_mse),
            'test_mse': float(test_mse),
            'train_r2': float(train_r2),
            'test_r2': float(test_r2),
            'model_path': storage_path,
            'feature_importance': feature_importance.to_dict('records')
        }
        
        print(f"\n{'='*60}")
        print(f"✅ TRAINING COMPLETED SUCCESSFULLY")
        print(f"{'='*60}\n")
        
        return results
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ TRAINING FAILED: {str(e)}")
        print(f"{'='*60}\n")
        raise


def retrain_all_models():
    """
    Retrain models for all users (or global model).
    Called by the scheduler for nightly retraining.
    """
    print(f"\n🌙 NIGHTLY RETRAINING JOB: {datetime.now().strftime('%Y-%m-%d %H:%M:%S CST')}")
    
    try:
        # For now, train a single global model
        # In the future, you can train per-user models
        results = train_model(user_id="global")
        
        if results:
            print(f"✅ Nightly retraining successful")
            print(f"   Model performance - Test R²: {results['test_r2']:.4f}")
        else:
            print(f"⏭️  Skipped retraining - insufficient feedback data")
            
    except Exception as e:
        print(f"❌ Nightly retraining failed: {e}")


# Manual training endpoint (for testing or manual triggers)
def manual_train(user_id: str = "global") -> dict:
    """
    Manually trigger model training.
    Can be called via API endpoint or CLI.
    """
    try:
        results = train_model(user_id)
        
        if results:
            return {
                "status": "success",
                "message": "Model trained successfully",
                "results": results
            }
        else:
            return {
                "status": "skipped",
                "message": f"Insufficient data (need {MIN_FEEDBACK_COUNT} positive feedback entries)",
                "results": None
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "results": None
        }


if __name__ == "__main__":
    # Test training locally
    print("🧪 Running manual training test...")
    result = manual_train()
    print(f"\nResult: {result}")
