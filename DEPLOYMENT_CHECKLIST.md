# 🚀 ACL Guardian Production Deployment Checklist

## Overview
Use this checklist to ensure a complete and successful deployment of the ACL Guardian backend with Supabase integration.

---

## ✅ Pre-Deployment Setup

### 1. Supabase Configuration

- [ ] **Create Supabase Project**
  - Project name: `acl-guardian`
  - Region: US West (or closest to users)
  - Save database password securely

- [ ] **Create Database Tables**
  - [ ] Run SQL schema from `SUPABASE_SETUP.md`
  - [ ] Verify `feedback` table exists
  - [ ] Confirm indexes created
  - [ ] Enable Row Level Security (RLS)
  - [ ] Create RLS policies

- [ ] **Create Storage Bucket**
  - [ ] Bucket name: `ml-models`
  - [ ] Set to private (not public)
  - [ ] Configure bucket policies for service role

- [ ] **Get API Credentials**
  - [ ] Copy Project URL: `https://xxx.supabase.co`
  - [ ] Copy Service Role Key (NOT anon key)
  - [ ] Save credentials securely (password manager)

### 2. Fitbit OAuth Setup

- [ ] **Create Fitbit App**
  - Go to: https://dev.fitbit.com/apps
  - [ ] Create new application
  - [ ] Set OAuth 2.0 Application Type: `Server`
  - [ ] Add redirect URLs:
    - `http://localhost:8000/api/fitbit/callback`
    - `https://YOUR-BACKEND.onrender.com/api/fitbit/callback`

- [ ] **Get Credentials**
  - [ ] Copy Client ID
  - [ ] Copy Client Secret
  - [ ] Save credentials securely

### 3. Local Environment

- [ ] **Clone Repository**
  ```bash
  git clone https://github.com/your-username/Guardian-ACL.git
  cd Guardian-ACL/backend
  ```

- [ ] **Create Virtual Environment**
  ```bash
  python -m venv .venv
  .venv\Scripts\activate  # Windows
  ```

- [ ] **Install Dependencies**
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Configure .env File**
  - [ ] Copy `.env.example` to `.env`
  - [ ] Update `SUPABASE_URL`
  - [ ] Update `SUPABASE_KEY`
  - [ ] Update `FITBIT_CLIENT_ID`
  - [ ] Update `FITBIT_CLIENT_SECRET`
  - [ ] Verify `ENCRYPTION_KEY` is set

- [ ] **Test Local Connection**
  ```bash
  # Test Supabase
  python -c "from supabase_client import get_supabase_client; print('✅ Supabase OK')"
  
  # Test server
  uvicorn main:app --reload --port 8000
  ```

---

## ✅ Deployment to Render

### 1. GitHub Setup

- [ ] **Push Code to GitHub**
  ```bash
  git add .
  git commit -m "Production ready with Supabase integration"
  git push origin main
  ```

### 2. Render Service Creation

- [ ] **Create Web Service**
  - Go to: https://dashboard.render.com/
  - [ ] Click "New +" → "Web Service"
  - [ ] Connect GitHub repository
  - [ ] Select `Guardian-ACL` repo
  - [ ] Configure service:
    - Name: `acl-guardian-backend`
    - Region: Oregon (or closest)
    - Branch: `main`
    - Runtime: Python 3
    - Build: `cd backend && pip install -r requirements.txt`
    - Start: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables (Render)

Add the following in Render Dashboard → Environment:

- [ ] `PYTHON_VERSION` = `3.11.9`
- [ ] `FRONTEND_URL` = `https://your-app.vercel.app`
- [ ] `DATABASE_URL` = `postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres`
- [ ] `SUPABASE_URL` = `https://xxx.supabase.co`
- [ ] `SUPABASE_KEY` = `eyJhbG...` (service role key)
- [ ] `ENCRYPTION_KEY` = `lTrh_g77...` (from local `.env`)
- [ ] `FITBIT_CLIENT_ID` = `your_client_id`
- [ ] `FITBIT_CLIENT_SECRET` = `your_client_secret`
- [ ] `FITBIT_REDIRECT_URI` = `https://acl-guardian-backend.onrender.com/api/fitbit/callback`

### 4. Deploy

- [ ] **Click "Create Web Service"**
- [ ] **Wait for deployment** (~3-5 minutes)
- [ ] **Verify deployment succeeded**
  - Check logs for: `🚀 ACL Guardian API started`
  - Check logs for: `⏰ Nightly retraining scheduler started`

---

## ✅ Post-Deployment Verification

### 1. Health Checks

- [ ] **Test API Health**
  ```bash
  curl https://acl-guardian-backend.onrender.com/health
  # Expected: {"status": "healthy"}
  ```

- [ ] **Test Interactive Docs**
  - Open: https://acl-guardian-backend.onrender.com/docs
  - [ ] Verify all endpoints visible
  - [ ] Test a simple GET request

### 2. Database Connection

- [ ] **Check Supabase Logs**
  - Supabase Dashboard → Logs → API
  - [ ] Verify connections from Render IP

- [ ] **Test Feedback Endpoint**
  ```bash
  curl -X POST https://acl-guardian-backend.onrender.com/api/feedback \
    -H "Content-Type: application/json" \
    -d '{
      "user_id": "test_deploy",
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

- [ ] **Verify in Supabase**
  - Supabase Dashboard → Table Editor → `feedback`
  - [ ] Confirm test record exists

### 3. Fitbit OAuth Flow

- [ ] **Update Fitbit Redirect URL**
  - Fitbit Dev Console → Your App → OAuth 2.0
  - [ ] Add production URL: `https://acl-guardian-backend.onrender.com/api/fitbit/callback`
  - [ ] Save changes (wait 5 minutes for propagation)

- [ ] **Test OAuth Flow**
  - Visit: `https://acl-guardian-backend.onrender.com/api/fitbit/authorize`
  - [ ] Redirects to Fitbit login
  - [ ] Authorize app
  - [ ] Redirects to frontend with `connected=true`

### 4. Prediction System

- [ ] **Test Formula Prediction**
  ```bash
  curl -X POST https://acl-guardian-backend.onrender.com/api/predict \
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
  # Expected: risk_score, risk_level, method: "formula"
  ```

- [ ] **Check Prediction Health**
  ```bash
  curl https://acl-guardian-backend.onrender.com/api/predict/health
  # Expected: {"status": "healthy", "ml_model_available": false}
  ```

### 5. Training System

- [ ] **Test Manual Training**
  ```bash
  curl -X POST https://acl-guardian-backend.onrender.com/api/train?user_id=global
  # Expected: {"status": "skipped", "message": "Insufficient data..."}
  ```

- [ ] **Verify Scheduler Active**
  - Check Render logs
  - [ ] Look for: `⏰ Nightly retraining scheduler started (7:00 PM CST)`

---

## ✅ Frontend Integration

### 1. Update Frontend Environment

- [ ] **Vercel Environment Variables**
  - Vercel Dashboard → Settings → Environment Variables
  - [ ] Add `NEXT_PUBLIC_API_URL` = `https://acl-guardian-backend.onrender.com`
  - [ ] Apply to: Production, Preview, Development

### 2. Update Frontend Code

- [ ] **Verify API Calls Use Env Variable**
  ```typescript
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  ```

- [ ] **Redeploy Frontend**
  - Commit changes
  - Push to GitHub
  - Vercel auto-deploys

### 3. Test End-to-End

- [ ] **Full User Flow**
  - [ ] Visit frontend: `https://your-app.vercel.app`
  - [ ] Click "Connect Fitbit"
  - [ ] Authorize app
  - [ ] Sync data
  - [ ] View risk assessment
  - [ ] Submit feedback
  - [ ] Check Supabase for feedback entry

---

## ✅ Production Monitoring

### 1. Set Up Alerts

- [ ] **Render Dashboard**
  - [ ] Enable deployment notifications (Slack/Email)
  - [ ] Set up crash alerts

- [ ] **Supabase Dashboard**
  - [ ] Monitor database usage (500 MB free tier)
  - [ ] Monitor storage usage (1 GB free tier)
  - [ ] Set up usage alerts

### 2. Monitor Logs

- [ ] **Check Nightly Training**
  - [ ] View Render logs at 7:00 PM CST daily
  - [ ] Look for: `🎯 TRAINING STARTED`
  - [ ] Verify completion: `✅ TRAINING COMPLETED SUCCESSFULLY`

- [ ] **Monitor Errors**
  - [ ] Check for 500 errors in Render logs
  - [ ] Check Supabase error logs
  - [ ] Set up error tracking (e.g., Sentry)

### 3. Performance Metrics

- [ ] **Response Times**
  - [ ] Health endpoint < 200ms
  - [ ] Prediction endpoint < 1s
  - [ ] Training endpoint < 30s (after 100 feedbacks)

- [ ] **Uptime**
  - [ ] Set up Uptime Robot (free tier)
  - [ ] Ping `/health` every 5 minutes

---

## ✅ Security Audit

- [ ] **Environment Variables**
  - [ ] No secrets committed to Git
  - [ ] `.env` file in `.gitignore`
  - [ ] All secrets stored in Render dashboard

- [ ] **API Keys**
  - [ ] Using Supabase service role key (not anon key)
  - [ ] Fitbit client secret not exposed
  - [ ] Encryption key is 32-byte base64

- [ ] **CORS**
  - [ ] Only frontend URL in `allow_origins`
  - [ ] Credentials enabled properly

- [ ] **Database**
  - [ ] RLS enabled on all tables
  - [ ] Proper policies configured
  - [ ] Storage buckets set to private

---

## ✅ Documentation

- [ ] **Update README**
  - [ ] Production URLs documented
  - [ ] API endpoints listed
  - [ ] Deployment steps clear

- [ ] **API Documentation**
  - [ ] All endpoints documented
  - [ ] Request/response examples provided
  - [ ] Error codes explained

- [ ] **User Guide**
  - [ ] How to connect Fitbit
  - [ ] How to view risk assessment
  - [ ] How to submit feedback

---

## 🎉 Launch Checklist

Final verification before going live:

- [ ] All health checks passing ✅
- [ ] Fitbit OAuth working ✅
- [ ] Data syncing correctly ✅
- [ ] Predictions accurate ✅
- [ ] Feedback stored in Supabase ✅
- [ ] Scheduler running ✅
- [ ] Frontend connected ✅
- [ ] Monitoring set up ✅
- [ ] Documentation complete ✅
- [ ] Security audited ✅

---

## 📊 Metrics to Track

### Week 1
- [ ] Total users connected
- [ ] Total feedback entries
- [ ] API response times
- [ ] Error rate
- [ ] Uptime percentage

### Week 2
- [ ] Feedback accuracy rate
- [ ] Model training frequency
- [ ] Database growth
- [ ] Storage usage

### Month 1
- [ ] User retention
- [ ] Prediction accuracy improvement
- [ ] Feature usage analytics
- [ ] Cost analysis (Render + Supabase)

---

## 🆘 Rollback Plan

If critical issues occur:

1. **Revert Render Deployment**
   - Render Dashboard → Deployments → Previous Deployment → Redeploy

2. **Restore Database**
   - Supabase Dashboard → Database → Backups → Restore

3. **Notify Users**
   - Post status update
   - Email notification (if applicable)

---

## 📞 Support Contacts

- **Render Support**: https://render.com/docs/support
- **Supabase Support**: https://supabase.com/docs/support
- **Fitbit Developer**: https://dev.fitbit.com/build/reference/

---

**Last Updated**: January 2025  
**Version**: 3.0.0  
**Status**: Production Ready ✅
