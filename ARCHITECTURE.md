# ACL Guardian - System Architecture

## Overview

This document provides a visual representation of the ACL Guardian system architecture, showing how all components interact.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                            │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js / Vercel)                     │
│  ┌───────────────┐  ┌───────────────┐  ┌────────────────────────┐ │
│  │   Dashboard   │  │ Risk Display  │  │  Feedback Submission   │ │
│  └───────────────┘  └───────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTP/HTTPS
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI / Render)                      │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                        API Endpoints                          │ │
│  │  /api/predict │ /api/feedback │ /api/train │ /api/fitbit/*  │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────┐  ┌────────────────┐  ┌───────────────────────┐ │
│  │   Prediction  │  │    Feedback    │  │   Training Module    │ │
│  │   Service     │  │    Service     │  │  (RandomForest ML)   │ │
│  └───────────────┘  └────────────────┘  └───────────────────────┘ │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │            APScheduler (Nightly @ 7:00 PM CST)             │   │
│  │                   retrain_all_models()                     │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
           │                        │                        │
           │                        │                        │
           ▼                        ▼                        ▼
┌──────────────────┐   ┌──────────────────────┐   ┌─────────────────┐
│  Fitbit API      │   │   Supabase           │   │  Supabase       │
│                  │   │   (PostgreSQL)       │   │  Storage        │
│  - Activity Data │   │                      │   │                 │
│  - Heart Rate    │   │  ┌────────────────┐  │   │  ┌───────────┐  │
│  - Sleep Data    │   │  │ feedback table │  │   │  │ ML Models │  │
│  - OAuth Tokens  │   │  │ - user_id      │  │   │  │  .pkl     │  │
└──────────────────┘   │  │ - date         │  │   │  └───────────┘  │
                       │  │ - metrics      │  │   │                 │
                       │  │ - risk_score   │  │   │                 │
                       │  │ - feedback     │  │   │                 │
                       │  └────────────────┘  │   │                 │
                       └──────────────────────┘   └─────────────────┘
```

---

## 🔄 Data Flow

### 1. User Connects Fitbit

```
User clicks "Connect Fitbit"
         │
         ▼
Frontend redirects to /api/fitbit/authorize
         │
         ▼
Backend generates OAuth URL
         │
         ▼
User authorizes on Fitbit.com
         │
         ▼
Fitbit redirects to /api/fitbit/callback
         │
         ▼
Backend exchanges code for tokens
         │
         ▼
Tokens encrypted and stored in Supabase
         │
         ▼
User redirected to frontend with success
```

### 2. Risk Prediction Request

```
User requests risk assessment
         │
         ▼
Frontend: POST /api/predict
         │
         ▼
Backend checks for ML model
         │
    ┌────┴────┐
    ▼         ▼
ML Model   Formula
Available  Fallback
    │         │
    └────┬────┘
         ▼
Calculate risk_score (0-1)
         │
         ▼
Classify risk_level (low/moderate/high)
         │
         ▼
Generate personalized recommendations
         │
         ▼
Return JSON response to frontend
         │
         ▼
Frontend displays results
```

### 3. Feedback Submission

```
User submits feedback (✓ or ✗)
         │
         ▼
Frontend: POST /api/feedback
         │
         ▼
Backend validates request
         │
         ▼
Supabase stores feedback entry
         │
         ▼
Backend returns success
         │
         ▼
Frontend shows confirmation
```

### 4. Automated Model Training

```
    7:00 PM CST Daily
         │
         ▼
APScheduler triggers retrain_all_models()
         │
         ▼
Fetch positive feedback (feedback=true)
         │
    ┌────┴────┐
    ▼         ▼
  ≥100      <100
  entries   entries
    │         │
    │         └─→ Skip training
    ▼
Prepare training data (features, target)
    │
    ▼
Split train/test (80/20)
    │
    ▼
Train RandomForestRegressor
    │
    ▼
Evaluate (MSE, R², feature importance)
    │
    ▼
Save model as .pkl file locally
    │
    ▼
Upload to Supabase Storage
    │
    ▼
Log training results
    │
    ▼
Model available for next predictions
```

---

## 🗂️ Database Schema

### Feedback Table (Supabase PostgreSQL)

```sql
CREATE TABLE feedback (
    id              SERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    date            DATE NOT NULL,
    
    -- Activity Metrics
    steps           INTEGER,
    active_minutes  INTEGER,
    resting_hr      INTEGER,
    peak_hr_minutes INTEGER,
    
    -- Sleep Metrics
    sleep_efficiency REAL,
    minutes_asleep   INTEGER,
    
    -- User Profile
    weight          REAL,
    acl_history     BOOLEAN DEFAULT FALSE,
    knee_pain       INTEGER CHECK (knee_pain >= 0 AND knee_pain <= 10),
    
    -- Risk Prediction
    formula_risk    REAL NOT NULL CHECK (formula_risk >= 0 AND formula_risk <= 1),
    
    -- User Feedback
    feedback        BOOLEAN NOT NULL,
    
    -- Metadata
    created_at      TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, date)
);

-- Indexes
CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_date ON feedback(date);
CREATE INDEX idx_feedback_positive ON feedback(feedback) WHERE feedback = TRUE;
```

---

## 📦 Supabase Storage Structure

```
ml-models/
└── models/
    ├── user_global.pkl          # Global model (all users)
    ├── user_ABC123.pkl          # User-specific model
    └── user_XYZ789.pkl          # User-specific model
```

---

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/health` | Health check |
| `POST` | `/api/predict` | Get ACL risk prediction |
| `GET` | `/api/predict/health` | Check prediction service health |
| `POST` | `/api/feedback` | Submit user feedback |
| `GET` | `/api/feedback/{user_id}` | Get feedback history |
| `GET` | `/api/feedback/stats/{user_id}` | Get feedback statistics |
| `POST` | `/api/train` | Manually trigger model training |

### Fitbit Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/fitbit/authorize` | Initiate OAuth flow |
| `GET` | `/api/fitbit/callback` | OAuth callback handler |
| `POST` | `/api/fitbit/sync/{user_id}` | Sync Fitbit data |
| `POST` | `/api/fitbit/disconnect/{user_id}` | Disconnect Fitbit |

### Activity Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/activity/{user_id}` | Get activity data |
| `POST` | `/api/manual-data/{user_id}` | Submit manual data |

### User Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/user/{user_id}/profile` | Get user profile |
| `POST` | `/api/user/{user_id}/profile` | Update user profile |

---

## 🤖 Machine Learning Pipeline

### Training Process

```
┌────────────────────────────────────────────────────────────┐
│                   TRAINING PIPELINE                        │
└────────────────────────────────────────────────────────────┘

1. DATA COLLECTION
   │
   ├─→ Query Supabase: SELECT * FROM feedback WHERE feedback = true
   │
   └─→ Minimum 100 entries required

2. DATA PREPARATION
   │
   ├─→ Extract features: [steps, active_minutes, resting_hr, ...]
   │
   ├─→ Extract target: formula_risk
   │
   └─→ Fill missing values with defaults

3. TRAIN/TEST SPLIT
   │
   └─→ 80% training, 20% testing (random_state=42)

4. MODEL TRAINING
   │
   ├─→ RandomForestRegressor
   │
   ├─→ Parameters:
   │   ├─ n_estimators: 100
   │   ├─ max_depth: 10
   │   ├─ min_samples_split: 5
   │   └─ random_state: 42
   │
   └─→ Fit on training data

5. MODEL EVALUATION
   │
   ├─→ Calculate MSE (Mean Squared Error)
   │
   ├─→ Calculate R² (Coefficient of Determination)
   │
   └─→ Analyze feature importance

6. MODEL DEPLOYMENT
   │
   ├─→ Save as .pkl file (joblib)
   │
   ├─→ Upload to Supabase Storage
   │
   └─→ Log training results
```

### Prediction Process

```
┌────────────────────────────────────────────────────────────┐
│                  PREDICTION PIPELINE                       │
└────────────────────────────────────────────────────────────┘

1. RECEIVE REQUEST
   │
   └─→ POST /api/predict with user metrics

2. CHECK MODEL AVAILABILITY
   │
   ├─→ Try to load from Supabase Storage
   │   ├─ Success → Use ML model
   │   └─ Fail → Use formula fallback
   │
   └─→ ML Model Path: models/user_{user_id}.pkl

3. CALCULATE RISK SCORE
   │
   ├─→ ML Model:
   │   ├─ Prepare features
   │   ├─ model.predict(features)
   │   └─ confidence = model.score()
   │
   └─→ Formula:
       ├─ 0.4 × (resting_hr / 100)
       ├─ 0.3 × (active_minutes / 60)
       ├─ 0.2 × (sleep_efficiency / 100)
       └─ 0.1 × (knee_pain / 10)

4. CLASSIFY RISK LEVEL
   │
   ├─→ Low: risk_score < 0.4
   ├─→ Moderate: 0.4 ≤ risk_score < 0.7
   └─→ High: risk_score ≥ 0.7

5. GENERATE RECOMMENDATIONS
   │
   └─→ Personalized based on risk factors

6. RETURN RESPONSE
   │
   └─→ JSON: {risk_score, risk_level, method, recommendations}
```

---

## 🔐 Security Architecture

```
┌────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                        │
└────────────────────────────────────────────────────────────┘

1. TRANSPORT LAYER
   │
   └─→ HTTPS/TLS for all API communications

2. AUTHENTICATION
   │
   ├─→ Fitbit OAuth 2.0
   │   ├─ Authorization Code Flow
   │   └─ Token refresh mechanism
   │
   └─→ Encrypted token storage (Fernet)

3. DATABASE SECURITY
   │
   ├─→ Row Level Security (RLS) enabled
   │
   ├─→ Service role key for backend
   │
   └─→ Anon key for client (if needed)

4. ENVIRONMENT VARIABLES
   │
   ├─→ Never committed to Git
   │
   ├─→ Stored in Render dashboard
   │
   └─→ Accessed via os.getenv()

5. CORS POLICY
   │
   └─→ Only frontend URL allowed
```

---

## 📊 Monitoring & Logging

```
┌────────────────────────────────────────────────────────────┐
│                   MONITORING POINTS                        │
└────────────────────────────────────────────────────────────┘

1. APPLICATION LOGS (Render)
   │
   ├─→ Server startup/shutdown
   ├─→ API request/response
   ├─→ Training job execution
   └─→ Error stack traces

2. DATABASE LOGS (Supabase)
   │
   ├─→ Query performance
   ├─→ Connection errors
   └─→ Storage usage

3. SCHEDULER LOGS (APScheduler)
   │
   ├─→ Job execution times
   ├─→ Success/failure status
   └─→ Next scheduled run

4. METRICS
   │
   ├─→ API response times
   ├─→ Prediction accuracy rate
   ├─→ Model training duration
   └─→ Database storage usage
```

---

## 🔄 Deployment Workflow

```
┌────────────────────────────────────────────────────────────┐
│                  CI/CD PIPELINE                            │
└────────────────────────────────────────────────────────────┘

1. LOCAL DEVELOPMENT
   │
   ├─→ Code changes
   ├─→ Test locally
   └─→ Git commit

2. GITHUB
   │
   ├─→ Push to main branch
   └─→ Trigger webhook

3. RENDER (Backend)
   │
   ├─→ Pull latest code
   ├─→ Install dependencies
   ├─→ Health check
   └─→ Deploy

4. VERCEL (Frontend)
   │
   ├─→ Pull latest code
   ├─→ Build Next.js
   ├─→ Deploy
   └─→ Update environment variables

5. POST-DEPLOYMENT
   │
   ├─→ Smoke tests
   ├─→ Monitor logs
   └─→ Verify endpoints
```

---

## 📈 Scalability Considerations

### Current Architecture (Free Tier)

- **Backend**: Single Render instance
- **Database**: Supabase free tier (500 MB)
- **Storage**: Supabase free tier (1 GB)
- **Requests**: ~100 req/min

### Scaling Path

```
Phase 1: Free Tier (Current)
├─ Single instance
├─ SQLite fallback
└─ Manual training

Phase 2: Starter Tier ($7-25/month)
├─ Always-on backend
├─ PostgreSQL database
└─ Automated training

Phase 3: Production Tier ($50-100/month)
├─ Multiple instances
├─ Load balancer
├─ CDN for static assets
├─ Redis caching
└─ Advanced monitoring

Phase 4: Enterprise Tier ($200+/month)
├─ Kubernetes cluster
├─ Microservices architecture
├─ Auto-scaling
├─ Multi-region deployment
└─ Real-time ML inference
```

---

## 🎯 Performance Benchmarks

| Metric | Target | Current |
|--------|--------|---------|
| API Response Time (p95) | < 500ms | ~300ms |
| Health Check | < 100ms | ~50ms |
| Prediction Endpoint | < 1s | ~400ms |
| Training Duration | < 60s | ~25s (100 samples) |
| Database Query | < 100ms | ~30ms |
| Model Load | < 500ms | ~200ms |

---

**Last Updated**: January 2025  
**Version**: 3.0.0  
**Status**: Production Ready ✅
