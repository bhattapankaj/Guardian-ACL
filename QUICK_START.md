# ⚡ Quick Start Guide - ACL Guardian Backend

Get your ACL Guardian backend running in **5 minutes**!

---

## 🚀 Local Development

### Step 1: Clone & Setup (1 min)

```bash
# Clone repository
git clone https://github.com/your-username/Guardian-ACL.git
cd Guardian-ACL/backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate
```

### Step 2: Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment (2 mins)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your credentials:
# - FITBIT_CLIENT_ID (from https://dev.fitbit.com/apps)
# - FITBIT_CLIENT_SECRET
# - SUPABASE_URL (from https://app.supabase.com)
# - SUPABASE_KEY (service role key)
```

**Quick .env setup:**
```env
FITBIT_CLIENT_ID=your_client_id
FITBIT_CLIENT_SECRET=your_secret
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_service_role_key
ENCRYPTION_KEY=lTrh_g77tj2RmSUZ_z0oJFsKoAEsOlqJxGVpGSSfUN4=
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:///./acl_guardian.db
```

### Step 4: Run Server (1 min)

```bash
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
🚀 ACL Guardian API started with Fitbit integration!
📡 Frontend URL: http://localhost:3000
⏰ Nightly retraining scheduler started (7:00 PM CST)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Test API

Open your browser:
- **Health Check**: http://localhost:8000/health
- **Interactive Docs**: http://localhost:8000/docs
- **API Reference**: http://localhost:8000/redoc

---

## 📊 Test Prediction API

```bash
# Test prediction endpoint
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "steps": 10000,
    "active_minutes": 60,
    "resting_hr": 65,
    "peak_hr_minutes": 30,
    "sleep_efficiency": 85,
    "minutes_asleep": 420,
    "weight": 75,
    "acl_history": false,
    "knee_pain": 2,
    "age": 25,
    "sex": "male"
  }'
```

**Expected response:**
```json
{
  "risk_score": 0.35,
  "risk_level": "low",
  "method": "formula",
  "confidence": 0.75,
  "recommendations": [
    "Maintain current activity levels - you're doing great!",
    "Continue monitoring knee pain levels"
  ]
}
```

---

## 🗄️ Set Up Supabase (Optional for Local Dev)

### Quick Supabase Setup

1. **Create project** at https://app.supabase.com
2. **Run SQL** (from `SUPABASE_SETUP.md`):

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
    acl_history BOOLEAN DEFAULT FALSE,
    knee_pain INTEGER,
    formula_risk REAL NOT NULL,
    feedback BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);
```

3. **Create storage bucket** named `ml-models`
4. **Get credentials** from Settings → API
5. **Update .env** with your Supabase URL and key

---

## 🎯 Test Feedback System

```bash
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
    "sleep_efficiency": 85,
    "minutes_asleep": 420,
    "weight": 75,
    "acl_history": false,
    "knee_pain": 2,
    "formula_risk": 0.35,
    "feedback": true
  }'
```

---

## 🤖 Test Model Training

```bash
# Trigger manual training
curl -X POST http://localhost:8000/api/train?user_id=global
```

**Expected response (insufficient data):**
```json
{
  "status": "skipped",
  "message": "Insufficient data (need 100 positive feedback entries)",
  "results": null
}
```

---

## 🚀 Deploy to Production

### Quick Render Deployment

1. **Push to GitHub**:
```bash
git add .
git commit -m "Production ready"
git push origin main
```

2. **Create Render service**:
   - Go to: https://dashboard.render.com/
   - Click "New +" → "Blueprint"
   - Select your repo
   - Render auto-detects `render.yaml`

3. **Add environment variables** in Render dashboard

4. **Deploy** and test at `https://your-service.onrender.com`

**Full deployment guide**: `RENDER_DEPLOYMENT.md`

---

## 🛠️ Troubleshooting

### Server won't start?

```bash
# Check Python version (need 3.11+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for errors
python -c "import fastapi; print('FastAPI OK')"
python -c "from supabase import create_client; print('Supabase OK')"
```

### Supabase connection error?

```bash
# Test connection
python -c "
import os
from dotenv import load_dotenv
from supabase_client import get_supabase_client

load_dotenv()
client = get_supabase_client()
print('✅ Supabase connected!')
"
```

### Port already in use?

```bash
# Use different port
uvicorn main:app --reload --port 8001
```

---

## 📚 Next Steps

### Learn More

- **API Documentation**: `API_DOCUMENTATION.md`
- **Architecture**: `ARCHITECTURE.md`
- **Full Setup**: `SUPABASE_SETUP.md`
- **Deployment**: `RENDER_DEPLOYMENT.md`

### Development Tips

- Use `--reload` flag for auto-restart on code changes
- Check `/docs` for interactive API testing
- Monitor logs with `--log-level debug`
- Test with sample data before connecting Fitbit

---

## 🎉 You're Ready!

Your ACL Guardian backend is now running locally!

**Try these next:**
1. ✅ Test prediction endpoint
2. ✅ Submit feedback entries
3. ✅ Connect Fitbit (need dev account)
4. ✅ Deploy to Render

**Need help?** Check the documentation or create a GitHub issue.

---

**Quick Links:**
- Local Server: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Supabase Dashboard: https://app.supabase.com
- Render Dashboard: https://dashboard.render.com

---

**Version**: 3.0.0  
**Status**: Ready to Rock! 🚀
