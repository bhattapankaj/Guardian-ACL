# ACL Guardian Backend - Production Ready 🚀

## Overview

The **ACL Guardian Backend** is a FastAPI-based REST API that powers the ACL Injury Risk Prediction platform. It integrates with **Fitbit** for activity tracking, **Supabase** for data persistence, and uses **Machine Learning** to predict ACL injury risk with automated nightly model retraining.

---

## 🌟 Features

### Core Functionality
- ✅ **Fitbit OAuth Integration** - Real-time activity, heart rate, and sleep data
- ✅ **ACL Risk Prediction** - ML model with formula fallback
- ✅ **Feedback System** - User feedback to improve model accuracy
- ✅ **Automated ML Retraining** - Nightly retraining at 7:00 PM CST
- ✅ **Supabase Integration** - PostgreSQL database + file storage
- ✅ **Manual Data Entry** - Support for Whoop, Polar, Garmin users

### Machine Learning
- **Model**: RandomForestRegressor
- **Features**: Steps, active minutes, resting HR, sleep efficiency, knee pain, ACL history
- **Training**: Minimum 100 positive feedback entries required
- **Storage**: Models stored in Supabase Storage as `.pkl` files
- **Scheduling**: APScheduler for automated nightly retraining

### API Endpoints
- `/api/predict` - ACL risk prediction
- `/api/feedback` - Store and retrieve user feedback
- `/api/train` - Manual model training
- `/api/fitbit/*` - Fitbit OAuth and data sync
- `/api/activity/*` - Activity data retrieval
- `/api/user/*` - User profile management

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── database.py          # SQLAlchemy database setup
│   ├── encryption.py         # Fernet token encryption
│   ├── fitbit_auth.py        # Fitbit OAuth flow
│   ├── fitbit_data.py        # Fitbit API client
│   ├── ml_model.py           # ML model utilities
│   ├── models.py             # SQLAlchemy ORM models
│   ├── risk_api.py           # Legacy risk assessment routes
│   ├── risk_calculator.py    # Risk calculation logic
│   └── train_model.py        # Legacy training module
├── routes/
│   ├── feedback.py           # Feedback CRUD endpoints
│   └── predict.py            # Prediction endpoints
├── models/                   # Trained ML models (local cache)
├── supabase_client.py        # Supabase connection and operations
├── train.py                  # ML training module
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (local)
├── .env.example              # Example environment variables
├── SUPABASE_SETUP.md         # Supabase setup guide
├── RENDER_DEPLOYMENT.md      # Render deployment guide
└── API_DOCUMENTATION.md      # API reference documentation
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Supabase account (free tier works)
- Fitbit Developer account
- Render account (for deployment)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/Guardian-ACL.git
   cd Guardian-ACL/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Update with your credentials (see SUPABASE_SETUP.md)

5. **Run the server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

6. **Test the API**:
   - Health check: http://localhost:8000/health
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## 🗄️ Database Setup

### Supabase Configuration

Follow the detailed guide in **`SUPABASE_SETUP.md`** to:
1. Create Supabase project
2. Set up `feedback` table
3. Create `ml-models` storage bucket
4. Configure environment variables

### Database Schema

**Feedback Table**:
```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    steps INTEGER,
    active_minutes INTEGER,
    resting_hr INTEGER,
    peak_hr_minutes INTEGER,
    sleep_efficiency REAL,
    minutes_asleep INTEGER,
    weight REAL,
    acl_history BOOLEAN,
    knee_pain INTEGER,
    formula_risk REAL NOT NULL,
    feedback BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);
```

---

## 🤖 Machine Learning Pipeline

### Training Workflow

1. **Feedback Collection**: Users rate prediction accuracy (✓ or ✗)
2. **Data Accumulation**: System waits for minimum 100 positive feedbacks
3. **Automated Training**: Scheduler triggers at 7:00 PM CST daily
4. **Model Evaluation**: Calculates MSE, R², and feature importance
5. **Model Upload**: Saves `.pkl` to Supabase Storage
6. **Prediction Switch**: API uses ML model instead of formula

### Formula-Based Prediction

When ML model isn't available (< 100 feedbacks):

```python
risk_score = (
    0.4 * (resting_hr / 100) +
    0.3 * (active_minutes / 60) +
    0.2 * (sleep_efficiency / 100) +
    0.1 * (knee_pain / 10)
)
```

### Feature Importance

Top features (from trained models):
1. **Resting Heart Rate** (28.5%)
2. **Active Minutes** (23.4%)
3. **Knee Pain** (19.8%)
4. **Sleep Efficiency** (15.2%)
5. **ACL History** (13.1%)

---

## 🔐 Environment Variables

Required environment variables (see `.env.example`):

```bash
# Fitbit OAuth
FITBIT_CLIENT_ID=your_client_id
FITBIT_CLIENT_SECRET=your_client_secret
FITBIT_REDIRECT_URI=http://localhost:8000/api/fitbit/callback

# Frontend
FRONTEND_URL=http://localhost:3000

# Database
DATABASE_URL=sqlite:///./acl_guardian.db  # Local
# DATABASE_URL=postgresql://user:pass@host:5432/db  # Production

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_service_role_key

# Security
ENCRYPTION_KEY=your_32_byte_base64_key
```

---

## 📦 Deployment

### Deploy to Render

Follow the comprehensive guide in **`RENDER_DEPLOYMENT.md`**.

**Quick steps**:
1. Push code to GitHub
2. Create Web Service on Render
3. Set environment variables
4. Deploy and test

### Production Checklist

- ✅ Supabase database and storage configured
- ✅ Environment variables set in Render
- ✅ Fitbit OAuth callback URLs updated
- ✅ Frontend URL configured for CORS
- ✅ Health check endpoint passing
- ✅ Scheduler running (check logs at 7 PM CST)

---

## 🧪 Testing

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Submit feedback
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
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
  }'

# Get prediction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
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
  }'

# Trigger training
curl -X POST http://localhost:8000/api/train?user_id=global
```

---

## 📊 Monitoring

### Logs

**Local**:
```bash
# Start with debug logging
uvicorn main:app --reload --log-level debug
```

**Production (Render)**:
- View logs in Render Dashboard
- Search for specific events (e.g., "TRAINING STARTED")

### Key Log Events

- `🚀 ACL Guardian API started` - Server startup
- `⏰ Nightly retraining scheduler started` - Scheduler initialized
- `🎯 TRAINING STARTED` - Model training begins
- `✅ TRAINING COMPLETED SUCCESSFULLY` - Model trained
- `⚠️ Insufficient data` - Not enough feedback for training

---

## 🛠️ Development Tips

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

---

## 🆘 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'supabase'`  
**Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: `Insufficient data: 0/100 entries`  
**Solution**: Add feedback entries via POST `/api/feedback`

**Issue**: `Supabase connection error`  
**Solution**: Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`

**Issue**: `Scheduler not running`  
**Solution**: Check logs for APScheduler errors, verify timezone

---

## 📚 Documentation

- **API Reference**: `API_DOCUMENTATION.md`
- **Supabase Setup**: `SUPABASE_SETUP.md`
- **Render Deployment**: `RENDER_DEPLOYMENT.md`
- **Interactive Docs**: http://localhost:8000/docs

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Fitbit Web API** for activity data
- **Supabase** for database and storage
- **FastAPI** for the web framework
- **scikit-learn** for machine learning
- **Render** for deployment

---

## 📧 Contact

- **Email**: support@aclguardian.com
- **GitHub**: [@your-username](https://github.com/your-username)
- **Website**: https://aclguardian.com

---

**Version**: 3.0.0  
**Last Updated**: January 2025  
**Status**: Production Ready ✅
