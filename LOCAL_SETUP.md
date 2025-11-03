# Local Development Setup Guide

## Backend (FastAPI)

### 1. Install Dependencies
```bash
cd /Users/pankaj/Desktop/EnZury/acl-guardian/backend
pip3 install -r requirements.txt
```

### 2. Check .env file (for Fitbit OAuth credentials)
Make sure `.env` exists with:
```
FITBIT_CLIENT_ID=your_client_id
FITBIT_CLIENT_SECRET=your_client_secret
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:///./acl_guardian.db  # Local SQLite
```

### 3. Start Backend
```bash
cd /Users/pankaj/Desktop/EnZury/acl-guardian/backend
./start.sh
```

Or manually:
```bash
cd /Users/pankaj/Desktop/EnZury/acl-guardian/backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend will run at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

---

## Frontend (Next.js)

### 1. Install Dependencies
```bash
cd /Users/pankaj/Desktop/EnZury/acl-guardian
npm install
```

### 2. Check .env.local
Make sure `.env.local` exists with:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Frontend
```bash
cd /Users/pankaj/Desktop/EnZury/acl-guardian
npm run dev
```

Frontend will run at: **http://localhost:3000**

---

## Testing the App

1. **Without Fitbit (Manual Entry)**:
   - Open http://localhost:3000
   - Click "Manual Entry" button
   - Fill your profile (height, weight, age, sex, sport)
   - Fill manual activity data
   - See your risk score!

2. **With Fitbit**:
   - Need valid Fitbit OAuth credentials in backend `.env`
   - Click "Connect with Fitbit"
   - Complete OAuth
   - Sync data
   - Fill profile
   - See personalized risk!

---

## Quick Troubleshooting

**Backend won't start:**
- Check all dependencies installed: `pip3 list | grep -i fastapi`
- Check PYTHONPATH: `export PYTHONPATH=/Users/pankaj/Desktop/EnZury/acl-guardian/backend`
- Port 8000 in use: `lsof -ti:8000 | xargs kill -9`

**Frontend won't start:**
- Check node version: `node --version` (should be 16+)
- Clear cache: `rm -rf .next`
- Reinstall: `rm -rf node_modules && npm install`

**Database errors:**
- SQLite file will be created automatically
- Location: `/Users/pankaj/Desktop/EnZury/acl-guardian/backend/acl_guardian.db`

---

## What Works Locally

✅ Manual data entry (no Fitbit needed)
✅ Risk calculation with profile data
✅ All tabs (Dashboard, Risk, Prevention, Trends, Profile)
✅ SQLite database (auto-created)
❓ Fitbit OAuth (needs valid credentials in .env)
