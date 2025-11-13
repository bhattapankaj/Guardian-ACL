# 🚀 ACL Guardian - Production Deployment Guide

This guide walks you through deploying ACL Guardian to production:
- **Backend (FastAPI)** → Render
- **Frontend (Next.js)** → Vercel

---

## 📋 Prerequisites

- [x] GitHub account
- [x] Render account (https://render.com)
- [x] Vercel account (https://vercel.com)
- [x] Supabase project with credentials
- [x] Fitbit Developer App credentials

---

## 🔧 Step 1: Prepare Your Repository

### 1.1 Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit changes
git commit -m "Production-ready ACL Guardian with Supabase integration"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/bhattapankaj/Guardian-ACL.git

# Push to GitHub
git push -u origin main
```

### 1.2 Verify .gitignore

Make sure these are in `.gitignore`:
```
.env
.env.local
backend/.env
node_modules/
.next/
__pycache__/
*.db
models/*.pkl
```

---

## 🐍 Step 2: Deploy Backend to Render

### 2.1 Create Web Service

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `bhattapankaj/Guardian-ACL`
4. Configure the service:
   - **Name**: `acl-guardian-backend`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

### 2.2 Add Environment Variables

In Render dashboard, go to **Environment** tab and add:

| Key | Value | Where to Get It |
|-----|-------|----------------|
| `PYTHON_VERSION` | `3.11.0` | Fixed value |
| `FRONTEND_URL` | `https://your-app.vercel.app` | From Vercel (add after frontend deploy) |
| `FITBIT_CLIENT_ID` | Your Fitbit Client ID | Fitbit Developer Dashboard |
| `FITBIT_CLIENT_SECRET` | Your Fitbit Client Secret | Fitbit Developer Dashboard |
| `ENCRYPTION_KEY` | Generate new key (see below) | Generate using Python |
| `SUPABASE_URL` | `https://aatfljhlyyrgkjbegbvf.supabase.co` | Your Supabase project URL |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIs...` | Supabase service role key |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIs...` | Supabase anon key |

**Generate ENCRYPTION_KEY**:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2.3 Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Your backend URL will be: `https://acl-guardian-backend.onrender.com`
4. Test it: `https://acl-guardian-backend.onrender.com/docs`

---

## 🌐 Step 3: Deploy Frontend to Vercel

### 3.1 Deploy via Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository: `bhattapankaj/Guardian-ACL`
4. Configure project:
   - **Framework Preset**: `Next.js` (auto-detected)
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

### 3.2 Add Environment Variable

In **Environment Variables** section, add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://acl-guardian-backend.onrender.com` |

### 3.3 Deploy

1. Click **"Deploy"**
2. Wait for build (2-5 minutes)
3. Your frontend URL will be: `https://guardian-acl.vercel.app`

---

## 🔄 Step 4: Update Cross-Origin Settings

### 4.1 Update Render Backend

Go back to Render dashboard and update `FRONTEND_URL`:
```
FRONTEND_URL=https://guardian-acl.vercel.app
```

Redeploy the backend.

### 4.2 Update Fitbit Redirect URI

In Fitbit Developer Dashboard (https://dev.fitbit.com):
1. Go to your app settings
2. Update **Redirect URL**:
   ```
   https://guardian-acl.vercel.app
   https://acl-guardian-backend.onrender.com/api/fitbit/callback
   ```

---

## ✅ Step 5: Verify Deployment

### 5.1 Test Backend

```bash
# Health check
curl https://acl-guardian-backend.onrender.com/api/predict/health

# Should return:
# {"status":"healthy","service":"ACL Risk Prediction","methods":["ml_model","formula"]}
```

### 5.2 Test Frontend

1. Open `https://guardian-acl.vercel.app`
2. Try connecting Fitbit
3. View dashboard
4. Submit feedback

### 5.3 Test Supabase Integration

```bash
# Check feedback endpoint
curl https://acl-guardian-backend.onrender.com/api/feedback/stats/test_user

# Should return feedback statistics
```

---

## 🔧 Troubleshooting

### Backend Issues

**Problem**: Module import errors
- **Solution**: Check `requirements.txt` includes all dependencies
- Run: `pip freeze > requirements.txt` locally and commit

**Problem**: Database errors
- **Solution**: Verify Supabase credentials in Render environment variables
- Check Supabase project is not paused

**Problem**: CORS errors
- **Solution**: Verify `FRONTEND_URL` matches your Vercel deployment URL

### Frontend Issues

**Problem**: API calls fail
- **Solution**: Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend is deployed and accessible

**Problem**: Build fails
- **Solution**: Check Next.js version compatibility
- Run `npm run build` locally first

---

## 📊 Monitoring

### Render Dashboard
- View logs: `Logs` tab in Render dashboard
- Monitor metrics: CPU, Memory usage
- Check deployment status

### Vercel Dashboard
- View deployment logs
- Monitor function execution
- Check analytics

### Supabase Dashboard
- Monitor database queries
- Check storage usage
- View API logs

---

## 🔄 Continuous Deployment

Both Render and Vercel auto-deploy on git push:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Backend and frontend auto-deploy!
```

---

## 💰 Cost Estimation

### Free Tier Limits

**Render (Free)**:
- 750 hours/month
- Spins down after 15 min inactivity
- 512 MB RAM
- **Cost**: $0/month

**Vercel (Hobby)**:
- 100 GB bandwidth/month
- Unlimited requests
- Automatic SSL
- **Cost**: $0/month

**Supabase (Free)**:
- 500 MB database
- 1 GB file storage
- 50,000 monthly active users
- **Cost**: $0/month

### Production Recommendations

For production with high traffic, consider:
- **Render**: Upgrade to Starter ($7/month) - always on
- **Vercel**: Pro plan ($20/month) - better performance
- **Supabase**: Pro plan ($25/month) - more storage

---

## 🎉 You're Live!

Your ACL Guardian is now in production:

- **Frontend**: https://guardian-acl.vercel.app
- **Backend API**: https://acl-guardian-backend.onrender.com
- **API Docs**: https://acl-guardian-backend.onrender.com/docs

### Next Steps

1. ✅ Share with users
2. 📊 Monitor feedback collection
3. 🤖 Wait for first ML model training (7 PM CST with 100+ feedback)
4. 📈 Analyze performance metrics
5. 🚀 Scale as needed

---

## 📞 Support

- **Backend Issues**: Check Render logs
- **Frontend Issues**: Check Vercel logs
- **Database Issues**: Check Supabase logs
- **General Help**: See `TROUBLESHOOTING.md`

**Happy deploying! 🚀**
