# 🚀 QUICK DEPLOY GUIDE - ACL Guardian Backend to Render

## ✅ Step 1: Code Already Pushed to GitHub!
- Repository: `bhattapankaj/Guardian-ACL`
- Backend location: `/backend/` folder
- Commit: `c1948ad`

## 📋 Step 2: Create Backend Service on Render

### 2.1 Open Render Dashboard
👉 **https://dashboard.render.com/**

### 2.2 Create New Web Service
1. Click **"New +"** (top right)
2. Select **"Web Service"**
3. Find and click **"Connect"** next to `bhattapankaj/Guardian-ACL`

### 2.3 Configure Service
```
Name: acl-guardian-backend
Region: Oregon (US West) - or same as frontend
Branch: main
Root Directory: backend        ⭐ VERY IMPORTANT!
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
Instance Type: Free
```

## 🔐 Step 3: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** for each:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `FRONTEND_URL` | `https://guardian-acl-4trn.onrender.com` |
| `FITBIT_CLIENT_ID` | `23TP8C` |
| `FITBIT_CLIENT_SECRET` | `117003e35e738367920f46aca5c44a2f` |
| `ENCRYPTION_KEY` | `vHUPIyUwW5_ut3nUUneEc6EixO3vYCiTvdm9UjGDtwI=` |
| `SECRET_KEY` | `LMNkRaY_6JdU5W7AmG-369XOGwrOx7tTV00IfNI0Gmk` |
| `DATABASE_URL` | `sqlite:///./acl_guardian.db` |

⚠️ **Copy exact values from above!**

## 🚀 Step 4: Deploy!

1. Click **"Create Web Service"**
2. Wait 2-3 minutes
3. Watch for: ✅ **"Your service is live 🎉"**
4. **COPY YOUR BACKEND URL**: `https://acl-guardian-backend-XXXX.onrender.com`

## 🔗 Step 5: Update Fitbit OAuth Callback

1. Go to: **https://dev.fitbit.com/apps**
2. Click your app: **"ACL Guardian"**
3. Find **"OAuth 2.0 Application Type"** → **"Redirect URL"**
4. Add **BOTH** URLs (keep existing localhost):
   ```
   http://localhost:3000/api/fitbit/callback
   https://guardian-acl-4trn.onrender.com/api/fitbit/callback
   ```
5. Click **"Save"**

## 🎯 Step 6: Update Frontend to Use Backend URL

### Option A: Via Render Dashboard (RECOMMENDED)
1. Go to your **frontend** service: https://dashboard.render.com/web/srv-d43c96hr0fns73eru4e0
2. Click **"Environment"** tab
3. Add variable:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://YOUR-BACKEND-URL.onrender.com` (from Step 4)
4. Click **"Save Changes"**
5. Frontend will auto-redeploy (2-3 minutes)

### Option B: Update Code
```bash
# In your frontend folder
cd /Users/pankaj/Desktop/EnZury/acl-guardian
echo "NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-URL.onrender.com" > .env.local
git add .env.local
git commit -m "Add production backend URL"
git push
```

## ✅ Step 7: Test Production!

1. Visit: **https://guardian-acl-4trn.onrender.com**
2. Click **"Connect My Fitbit"**
3. Login with Fitbit credentials
4. Click **"Allow"**
5. See your **REAL data**! 🎉

## 📊 Your Deployed Services

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | https://guardian-acl-4trn.onrender.com | ✅ Live |
| **Backend** | https://acl-guardian-backend-XXXX.onrender.com | 🔄 Deploy now |

## ⚠️ Important Notes

### Free Tier Limitations
- ⏰ Services spin down after 15 min inactivity
- 🐌 First request after sleep: ~50 seconds
- 💾 Database resets on each redeploy
- 💰 Upgrade to **$7/month** per service for:
  - Always-on (no cold starts)
  - Persistent disk (database survives redeploys)
  - Better performance

### Next Steps After Deployment
1. ✅ Test full OAuth flow
2. ✅ Verify data syncs correctly
3. ✅ Connect your personal Fitbit
4. ✅ Monitor logs for errors
5. 📈 Consider upgrading for Louisiana tournament

## 🆘 Troubleshooting

### Backend won't deploy?
- Check **Root Directory** is set to `backend`
- Verify all environment variables are added
- Check logs for specific errors

### OAuth redirect not working?
- Verify Fitbit callback URL includes production URL
- Check CORS settings in main.py
- Verify FRONTEND_URL env var is correct

### Frontend can't reach backend?
- Verify NEXT_PUBLIC_API_URL is set
- Check backend is actually running (visit backend URL)
- Check browser console for CORS errors

## 🎉 You're Almost There!

Just go to Render dashboard and create the backend service!
All your code is ready and pushed to GitHub.

**Start at Step 2 above** 👆
