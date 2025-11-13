# ACL Guardian API Documentation

## Base URL

**Local Development**: `http://localhost:8000`  
**Production**: `https://acl-guardian-backend.onrender.com`

---

## Authentication

Currently, the API uses Fitbit OAuth 2.0 for user authentication. No additional API keys required for most endpoints.

---

## API Endpoints

### 🏥 Health & Status

#### `GET /health`

Check API health status.

**Response**:
```json
{
  "status": "healthy"
}
```

---

### 📊 Feedback System

#### `POST /api/feedback`

Store user feedback on ACL risk prediction.

**Request Body**:
```json
{
  "user_id": "ABC123",
  "date": "2025-01-20",
  "steps": 10000,
  "active_minutes": 60,
  "resting_hr": 65,
  "peak_hr_minutes": 30,
  "sleep_efficiency": 85.5,
  "minutes_asleep": 420,
  "weight": 75.0,
  "acl_history": false,
  "knee_pain": 2,
  "formula_risk": 0.35,
  "feedback": true
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Feedback stored successfully",
  "feedback_id": 123
}
```

---

#### `GET /api/feedback/{user_id}`

Get feedback history for a user.

**Query Parameters**:
- `limit` (optional): Number of records to return (default: 100)

**Response**:
```json
{
  "user_id": "ABC123",
  "total_count": 45,
  "feedback": [
    {
      "id": 1,
      "date": "2025-01-20",
      "formula_risk": 0.35,
      "feedback": true,
      "created_at": "2025-01-20T10:30:00"
    }
  ]
}
```

---

#### `GET /api/feedback/stats/{user_id}`

Get feedback statistics for a user.

**Response**:
```json
{
  "user_id": "ABC123",
  "total_feedback": 45,
  "positive_feedback": 38,
  "negative_feedback": 7,
  "accuracy_rate": 84.4,
  "average_risk": 0.42,
  "model_ready": false,
  "feedback_needed": 55
}
```

---

### 🎯 ACL Risk Prediction

#### `POST /api/predict`

Get ACL injury risk prediction.

**Request Body**:
```json
{
  "user_id": "ABC123",
  "steps": 10000,
  "active_minutes": 60,
  "resting_hr": 65,
  "peak_hr_minutes": 30,
  "sleep_efficiency": 85.5,
  "minutes_asleep": 420,
  "weight": 75.0,
  "acl_history": false,
  "knee_pain": 2,
  "age": 25,
  "sex": "male"
}
```

**Response**:
```json
{
  "risk_score": 0.35,
  "risk_level": "low",
  "method": "formula",
  "confidence": 0.75,
  "recommendations": [
    "Maintain current activity levels - you're doing great!",
    "Continue monitoring knee pain levels",
    "Keep up good sleep habits (85% efficiency is excellent)"
  ]
}
```

**Risk Levels**:
- `low`: risk_score < 0.4
- `moderate`: 0.4 ≤ risk_score < 0.7
- `high`: risk_score ≥ 0.7

---

#### `GET /api/predict/health`

Check prediction service health.

**Response**:
```json
{
  "status": "healthy",
  "ml_model_available": false,
  "fallback_method": "formula"
}
```

---

### 🤖 Model Training

#### `POST /api/train`

Manually trigger ML model training.

**Query Parameters**:
- `user_id` (optional): User ID to train model for (default: "global")

**Response** (Success):
```json
{
  "status": "success",
  "message": "Model trained successfully",
  "results": {
    "user_id": "global",
    "training_date": "2025-01-20T19:00:00",
    "data_points": 150,
    "train_size": 120,
    "test_size": 30,
    "train_mse": 0.0234,
    "test_mse": 0.0289,
    "train_r2": 0.876,
    "test_r2": 0.843,
    "model_path": "models/user_global.pkl",
    "feature_importance": [
      {"feature": "resting_hr", "importance": 0.285},
      {"feature": "active_minutes", "importance": 0.234},
      {"feature": "knee_pain", "importance": 0.198}
    ]
  }
}
```

**Response** (Insufficient Data):
```json
{
  "status": "skipped",
  "message": "Insufficient data (need 100 positive feedback entries)",
  "results": null
}
```

---

### 🏃 Fitbit Integration

#### `GET /api/fitbit/authorize`

Redirect user to Fitbit OAuth authorization.

**Usage**: Redirect browser to this endpoint.

---

#### `GET /api/fitbit/callback`

OAuth callback handler (automatic redirect from Fitbit).

**Query Parameters**:
- `code`: Authorization code from Fitbit
- `state`: CSRF protection token

---

#### `POST /api/fitbit/sync/{user_id}`

Manually sync Fitbit data.

**Query Parameters**:
- `days` (optional): Number of days to sync (default: 14)

**Response**:
```json
{
  "message": "Successfully synced 14 days of data",
  "user_id": 123,
  "days_synced": 14,
  "last_sync": "2025-01-20T10:30:00"
}
```

---

#### `POST /api/fitbit/disconnect/{user_id}`

Disconnect user's Fitbit account.

**Response**:
```json
{
  "message": "Fitbit disconnected successfully"
}
```

---

### 📊 Activity Data

#### `GET /api/activity/{user_id}`

Get user's activity data.

**Query Parameters**:
- `days` (optional): Number of days to retrieve (default: 7)

**Response**:
```json
{
  "activities": [
    {
      "date": "2025-01-20",
      "steps": 10000,
      "distance": 7.5,
      "calories": 2500,
      "active_minutes": 60,
      "heart_rate_avg": 65,
      "sleep_hours": 7.5,
      "sleep_efficiency": 85,
      "cadence": 170,
      "load_score": 75
    }
  ]
}
```

---

#### `POST /api/manual-data/{user_id}`

Manually enter activity data (for non-Fitbit users).

**Request Body**:
```json
{
  "date": "2025-01-20",
  "steps": 10000,
  "distance_km": 7.5,
  "calories": 2500,
  "active_minutes": 60,
  "peak_minutes": 30,
  "resting_heart_rate": 65,
  "sleep_hours": 7.5,
  "sleep_efficiency": 85
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Saved activity data for 2025-01-20",
  "data_created": true,
  "activity_id": 456
}
```

---

### 👤 User Profile

#### `GET /api/user/{user_id}/profile`

Get user profile data.

**Response**:
```json
{
  "height_cm": 180,
  "sex": "male",
  "age": 25,
  "sport": "soccer",
  "limb_dominance": "right",
  "acl_history_flag": false,
  "acl_injury_date": null,
  "knee_pain_score": 2,
  "rehab_status": "none",
  "weight_kg": 75.0
}
```

---

#### `POST /api/user/{user_id}/profile`

Update user profile.

**Request Body**:
```json
{
  "height_cm": 180,
  "sex": "male",
  "age": 25,
  "sport": "soccer",
  "limb_dominance": "right",
  "acl_history_flag": false,
  "knee_pain_score": 2,
  "rehab_status": "none",
  "weight_kg": 75.0
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Profile updated successfully",
  "profile": {
    "height_cm": 180,
    "sex": "male",
    "age": 25
  }
}
```

---

## Automated Tasks

### Nightly Model Retraining

**Schedule**: Every day at 7:00 PM CST  
**Function**: `retrain_all_models()`  
**Trigger**: APScheduler (BackgroundScheduler)

**What it does**:
1. Fetches all positive feedback entries (minimum 100 required)
2. Trains RandomForestRegressor model
3. Evaluates performance (MSE, R², feature importance)
4. Uploads trained model to Supabase Storage
5. Logs results

**To monitor**: Check server logs at 19:00 CST daily.

---

## Error Codes

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 404 | Not Found (user/resource doesn't exist) |
| 422 | Validation Error (Pydantic model validation failed) |
| 500 | Internal Server Error |

---

## Rate Limits

Currently no rate limits enforced. Consider implementing for production.

---

## Examples

### Complete Workflow Example

```python
import requests

BASE_URL = "https://acl-guardian-backend.onrender.com"

# 1. Connect Fitbit (via browser redirect)
# User clicks: GET /api/fitbit/authorize

# 2. Sync Fitbit data
response = requests.post(f"{BASE_URL}/api/fitbit/sync/ABC123?days=14")
print(response.json())

# 3. Get risk prediction
prediction = requests.post(f"{BASE_URL}/api/predict", json={
    "user_id": "ABC123",
    "steps": 10000,
    "active_minutes": 60,
    "resting_hr": 65,
    "peak_hr_minutes": 30,
    "sleep_efficiency": 85.5,
    "minutes_asleep": 420,
    "weight": 75.0,
    "acl_history": False,
    "knee_pain": 2,
    "age": 25,
    "sex": "male"
})
print(f"Risk Score: {prediction.json()['risk_score']}")

# 4. Submit feedback
feedback = requests.post(f"{BASE_URL}/api/feedback", json={
    "user_id": "ABC123",
    "date": "2025-01-20",
    "steps": 10000,
    "active_minutes": 60,
    "resting_hr": 65,
    "peak_hr_minutes": 30,
    "sleep_efficiency": 85.5,
    "minutes_asleep": 420,
    "weight": 75.0,
    "acl_history": False,
    "knee_pain": 2,
    "formula_risk": 0.35,
    "feedback": True  # Accurate prediction
})
print(feedback.json())

# 5. Check feedback stats
stats = requests.get(f"{BASE_URL}/api/feedback/stats/ABC123")
print(f"Feedback accuracy: {stats.json()['accuracy_rate']}%")

# 6. Manually trigger training (admin only)
training = requests.post(f"{BASE_URL}/api/train?user_id=global")
print(training.json())
```

---

## Interactive Documentation

Visit the auto-generated interactive API docs:

**Swagger UI**: `https://acl-guardian-backend.onrender.com/docs`  
**ReDoc**: `https://acl-guardian-backend.onrender.com/redoc`

---

## WebSocket Support

Not currently implemented. Consider adding for real-time updates.

---

## Versioning

Current version: **v3.0.0**

API follows semantic versioning. Breaking changes will increment major version.

---

## Support

For issues or questions:
- **GitHub Issues**: [Create an issue](https://github.com/your-username/Guardian-ACL/issues)
- **Email**: support@aclguardian.com

---

**Last Updated**: January 2025  
**API Version**: 3.0.0
