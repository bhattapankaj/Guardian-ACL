# 🚀 Deploy ACL Guardian Backend to Render

## Prerequisites

Before deploying, ensure you have:

- ✅ **GitHub repository** with your code
- ✅ **Supabase project** set up (see `SUPABASE_SETUP.md`)
- ✅ **Fitbit OAuth app** configured
- ✅ **Render account** (free tier works)

---

## Step 1: Push Code to GitHub

```bash
cd d:\ACL\Guardian-ACL
git add .
git commit -m "Add Supabase integration and Render deployment config"
git push origin main
```

---

## Step 2: Create Web Service on Render

### Using Blueprint (render.yaml)

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Click "New +"** → **"Blueprint"**
3. **Connect Repository**: Select your GitHub repo `Guardian-ACL`
4. Render will automatically detect `render.yaml` and configure the service
5. Click **"Apply"**

### Manual Setup (Alternative)

If you prefer manual setup:

1. **Click "New +"** → **"Web Service"**
2. **Connect Repository**: Select `Guardian-ACL`
3. **Configure Service**:
   - **Name**: `acl-guardian-backend`
   - **Region**: `Oregon` (or closest to your users)
   - **Branch**: `main`
   - **Root Directory**: Leave blank (will use `backend/` from commands)
   - **Runtime**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free** (upgrade for production)

---

## Step 3: Configure Environment Variables

In the Render dashboard for your backend service, add these environment variables:

### Required Variables

| Key | Value | Description |
|-----|-------|-------------|
| `PYTHON_VERSION` | `3.11.9` | Python runtime version |
| `FRONTEND_URL` | `https://your-app.vercel.app` | Your Vercel frontend URL |
| `DATABASE_URL` | `postgresql://user:pass@host:5432/db` | Supabase PostgreSQL connection string |
| `SUPABASE_URL` | `https://xxx.supabase.co` | From Supabase dashboard |
| `SUPABASE_KEY` | `eyJhbG...` | Service role key (NOT anon key) |
| `ENCRYPTION_KEY` | `lTrh_g77...` | From `.env` file |
| `FITBIT_CLIENT_ID` | `your_client_id` | From Fitbit dev console |
| `FITBIT_CLIENT_SECRET` | `your_secret` | From Fitbit dev console |
| `FITBIT_REDIRECT_URI` | `https://xxx.onrender.com/api/fitbit/callback` | Your Render URL + callback path |

### How to Get Supabase DATABASE_URL

1. Go to Supabase Dashboard → **Settings** → **Database**
2. Scroll to **Connection String**
3. Select **URI** tab
4. Copy the connection string:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your database password

⚠️ **IMPORTANT**: Never commit these values to Git! Only add them in Render dashboard.

---

## Step 4: Deploy Backend

Click **"Create Web Service"** (or **"Apply"** for Blueprint).

**Deployment process** (~3-5 minutes):
1. ✅ Cloning repository
2. ✅ Installing Python dependencies
3. ✅ Running build command
4. ✅ Starting web service
5. ✅ Health check passing

Your backend URL will be: `https://acl-guardian-backend.onrender.com`

---

## Step 5: Update Fitbit OAuth Callback URL

1. Go to: https://dev.fitbit.com/apps
2. Click on your app: **ACL Guardian**
3. Under **OAuth 2.0 Application Type** → **Redirect URL**
4. Add **BOTH** URLs (one per line):
   ```
   http://localhost:8000/api/fitbit/callback
   https://acl-guardian-backend.onrender.com/api/fitbit/callback
   ```
5. Click **Save**

---

## Step 6: Update Frontend Environment Variables

### On Vercel (Production)

1. Go to Vercel Dashboard → Your Project → **Settings** → **Environment Variables**
2. Add:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://acl-guardian-backend.onrender.com`
   - **Environments**: Production, Preview, Development
3. Click **Save**
4. **Redeploy** your frontend

### Locally (Development)

Update `frontend/.env.local`:

```bash
# Local backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production backend (for testing)
# NEXT_PUBLIC_API_URL=https://acl-guardian-backend.onrender.com
```

---

## Step 7: Verify Deployment

### Test Backend Health

```bash
curl https://acl-guardian-backend.onrender.com/health
```

Expected response:
```json
{"status": "healthy"}
```

### Test API Endpoints

```bash
# Test root endpoint
curl https://acl-guardian-backend.onrender.com/

# Test docs (interactive)
open https://acl-guardian-backend.onrender.com/docs
```

### Test Supabase Connection

Monitor Render logs for:
```
✅ Supabase client initialized successfully
```

If you see errors:
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check Supabase project is active
- Verify tables and storage buckets exist

---

## Step 8: Test Full Flow

1. Visit your frontend: `https://your-app.vercel.app`
2. Click **"Connect My Fitbit"**
3. Authorize the app
4. Verify data syncs correctly
5. Submit feedback → Check Supabase dashboard
6. Manually trigger training: `POST /api/train`

---

## 🎉 Production Deployment Checklist

- ✅ Backend deployed on Render
- ✅ Frontend deployed on Vercel
- ✅ Supabase database and storage configured
- ✅ Environment variables set in Render
- ✅ Fitbit OAuth callback URLs updated
- ✅ Health check endpoint passing
- ✅ CORS configured for frontend URL
- ✅ Nightly retraining scheduler active (check logs at 7:00 PM CST)

---

## 📊 Monitor Your Services

### Render Dashboard

- **Logs**: Real-time logs for debugging
- **Metrics**: CPU, memory, response times
- **Events**: Deployments, crashes, restarts
- **Environment**: Manage environment variables

### Supabase Dashboard

- **Database**: Query feedback table
- **Storage**: View uploaded ML models
- **Logs**: API requests and errors
- **Usage**: Track database and storage usage

---

## ⚠️ Important Notes

### Free Tier Limitations

**Render Free Tier**:
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30-60 seconds (cold start)
- 750 hours/month (enough for one always-on service)

**Supabase Free Tier**:
- 500 MB database storage
- 1 GB file storage
- 2 GB data transfer
- Paused after 1 week of inactivity

### For Production (Paid Tier Benefits)

**Render Starter Plan** ($7/month):
- ✅ Always-on (no cold starts)
- ✅ Faster response times
- ✅ More CPU/memory
- ✅ Custom domains

**Supabase Pro Plan** ($25/month):
- ✅ 8 GB database storage
- ✅ 100 GB file storage
- ✅ 50 GB data transfer
- ✅ No inactivity pause
- ✅ Daily backups

---

## 🔧 Troubleshooting

### Backend Won't Start

**Error**: `Application startup failed`

**Solutions**:
1. Check Render logs for specific error
2. Verify `requirements.txt` includes all dependencies
3. Ensure environment variables are set correctly
4. Test locally with same environment variables

---

### Supabase Connection Errors

**Error**: `supabase.exceptions.SupabaseException: Invalid API key`

**Solutions**:
1. Verify `SUPABASE_KEY` is the **service role key** (not anon key)
2. Check Supabase project is active (not paused)
3. Ensure `SUPABASE_URL` matches your project

---

### Scheduler Not Running

**Error**: Nightly retraining not triggering

**Solutions**:
1. Check Render logs at 7:00 PM CST
2. Verify APScheduler is installed (`pip list | grep APScheduler`)
3. Check timezone is correct (America/Chicago)
4. Ensure service is running (not spun down)

**Note**: Free tier services spin down, so scheduler won't run unless there's active traffic. Use Render Cron Jobs (paid feature) or external cron service for reliable scheduling.

---

### OAuth Redirect Failing

**Error**: `redirect_uri_mismatch`

**Solutions**:
1. Verify Fitbit callback URL includes production URL
2. Check `FITBIT_REDIRECT_URI` environment variable
3. Ensure no trailing slashes in URLs
4. Wait 5 minutes after updating Fitbit app settings

---

### Model Training Fails

**Error**: `Insufficient data: 0/100 entries`

**Solutions**:
1. Add feedback entries via `POST /api/feedback`
2. Verify feedback table has data (check Supabase dashboard)
3. Ensure `feedback = true` for positive entries
4. Check Supabase connection is working

---

## 🚀 Next Steps

### Immediate Tasks

1. ✅ Test full OAuth flow in production
2. ✅ Submit test feedback entries
3. ✅ Manually trigger training (`POST /api/train`)
4. ✅ Verify model uploads to Supabase Storage
5. ✅ Test prediction endpoint (`POST /api/predict`)

### Production Enhancements

1. 🔒 **Security**: Implement API rate limiting
2. 📧 **Notifications**: Email alerts for model retraining
3. 📊 **Analytics**: Track prediction accuracy over time
4. 🎯 **A/B Testing**: Compare model versions
5. 📱 **Mobile App**: React Native frontend
6. 🤖 **Advanced ML**: Try XGBoost, LightGBM models
7. 🔄 **CI/CD**: GitHub Actions for automated testing

### Monitoring Setup

1. **Sentry**: Error tracking
2. **Uptime Robot**: Uptime monitoring
3. **New Relic**: Performance monitoring
4. **LogTail**: Log aggregation

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Fitbit Web API](https://dev.fitbit.com/build/reference/web-api/)

---

## 🆘 Need Help?

- **Render Support**: https://render.com/docs/support
- **Supabase Support**: https://supabase.com/docs/support
- **GitHub Issues**: Create an issue in your repository

---

**Last Updated**: January 2025  
**Version**: 3.0.0 - Production with Supabase & ML

