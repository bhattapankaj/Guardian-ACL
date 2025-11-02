# 🚀 Deploy ACL Guardian Backend to Render

## Step 1: Push Backend Code to GitHub

```bash
cd /Users/pankaj/Desktop/EnZury/acl-guardian-backend
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

## Step 2: Create Backend Service on Render

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Click "New +"** → **"Web Service"**
3. **Connect Repository**: Select `bhattapankaj/Guardian-ACL`
4. **Configure Service**:
   - **Name**: `acl-guardian-backend`
   - **Region**: Same as frontend (US East recommended)
   - **Branch**: `main`
   - **Root Directory**: `acl-guardian-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - **Plan**: **Free**

## Step 3: Add Environment Variables

In the Render dashboard for your backend service, add these environment variables:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `FRONTEND_URL` | `https://guardian-acl-4trn.onrender.com` |
| `FITBIT_CLIENT_ID` | `23TP8C` |
| `FITBIT_CLIENT_SECRET` | `117003e35e738367920f46aca5c44a2f` |
| `ENCRYPTION_KEY` | `vHUPIyUwW5_ut3nUUneEc6EixO3vYCiTvdm9UjGDtwI=` |
| `DATABASE_URL` | `sqlite:///./acl_guardian.db` |

⚠️ **IMPORTANT**: Copy these values from your local `.env` file!

## Step 4: Deploy Backend

Click **"Create Web Service"** and wait for deployment to complete (~2-3 minutes).

Your backend URL will be: `https://acl-guardian-backend-XXXX.onrender.com`

## Step 5: Update Fitbit OAuth Callback URL

1. Go to: https://dev.fitbit.com/apps
2. Click on your app: **ACL Guardian**
3. Under **OAuth 2.0 Application Type** → **Redirect URL**
4. Add **BOTH** URLs:
   ```
   http://localhost:3000/api/fitbit/callback
   https://guardian-acl-4trn.onrender.com/api/fitbit/callback
   ```
5. Click **Save**

## Step 6: Update Frontend to Use Production Backend

You'll need to update your frontend environment variables to point to the production backend URL.

### Option A: Create `.env.local` in Frontend

```bash
cd /Users/pankaj/Desktop/EnZury/acl-guardian
echo "NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-URL.onrender.com" > .env.local
```

### Option B: Add Environment Variable on Render

1. Go to your **frontend** service on Render
2. Add environment variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://YOUR-BACKEND-URL.onrender.com`

## Step 7: Update Frontend API Calls

Your frontend code needs to use the backend URL from environment variables.

## 🎉 Testing Production Deployment

1. Visit: `https://guardian-acl-4trn.onrender.com`
2. Click **"Connect My Fitbit"**
3. Log in with Fitbit credentials
4. Authorize the app
5. See your REAL data!

## 📊 Monitor Your Services

- **Frontend**: https://dashboard.render.com/web/srv-d43c96hr0fns73eru4e0
- **Backend**: https://dashboard.render.com (your new backend service)

## ⚠️ Important Notes

### Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~50 seconds
- Database is ephemeral (resets on redeploy)

### For Production
- Upgrade to paid tier for:
  - Always-on services
  - Persistent disk for SQLite database
  - Faster response times
  - No cold starts

### Database Persistence
If you need persistent data on free tier, consider:
- **PostgreSQL** (Render provides free tier)
- **MongoDB Atlas** (free tier)
- **Supabase** (free PostgreSQL)

## 🔧 Troubleshooting

### Backend won't start?
- Check logs in Render dashboard
- Verify all environment variables are set
- Check `requirements.txt` includes all dependencies

### OAuth redirect failing?
- Verify Fitbit callback URL includes production URL
- Check CORS settings in `main.py`

### Database errors?
- SQLite works but resets on redeploy
- Consider PostgreSQL for production

## 🚀 Next Steps

1. Test the full OAuth flow in production
2. Monitor logs for any errors
3. Consider upgrading for persistent database
4. Add monitoring/alerting for uptime
