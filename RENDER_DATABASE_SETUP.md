# 🗄️ Render PostgreSQL Database Setup Guide

## Why You Need This

Your app currently uses **SQLite** (a local file), which **DOES NOT work on Render** because:
- ❌ Files are deleted on every deploy
- ❌ Data gets wiped when the server restarts
- ❌ No persistence across deployments

**Solution**: Use Render's **free PostgreSQL database** for persistent storage.

---

## 📋 Step-by-Step Setup (5 minutes)

### **1. Create a PostgreSQL Database on Render**

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `acl-guardian-db` (or any name)
   - **Database**: `acl_guardian` (default is fine)
   - **User**: (auto-generated)
   - **Region**: Same as your backend (e.g., `Oregon (US West)`)
   - **Instance Type**: **Free** (perfect for hackathon/MVP)
4. Click **"Create Database"**
5. **Wait 2-3 minutes** for it to provision

---

### **2. Get the Database Connection String**

1. Once created, click on your database
2. Scroll to **"Connections"** section
3. Copy the **"Internal Database URL"** (it looks like):
   ```
   postgres://user:password@dpg-xxxxx.oregon-postgres.render.com/acl_guardian
   ```
   ⚠️ **Use "Internal" not "External"** for faster, free connections!

---

### **3. Add Database URL to Your Backend Service**

1. Go to your **backend service** on Render (the one running your FastAPI app)
2. Click **"Environment"** tab (left sidebar)
3. Click **"Add Environment Variable"**
4. Add:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the Internal Database URL you copied
5. Click **"Save Changes"**
6. Render will **automatically redeploy** your backend

---

### **4. Verify It's Working**

After the redeploy completes (~2-3 minutes):

1. Open your backend URL: `https://acl-guardian-backend.onrender.com/docs`
2. Check the logs - you should see:
   ```
   ✅ Using PostgreSQL database (Production)
   ✅ Database tables created successfully!
   ```
3. Test an endpoint (e.g., `/api/fitbit/activity/{user_id}`)

---

## 🎯 What This Fixes

### Before (SQLite - ❌ Broken on Render):
```
DATABASE_URL = "sqlite:///./acl_guardian.db"  # Local file
```
- Data lost on every deploy
- Users have to re-enter profile every time
- Fitbit data disappears

### After (PostgreSQL - ✅ Works on Render):
```
DATABASE_URL = "postgresql://user:pass@render-host/db"  # Cloud database
```
- **Persistent storage** - data survives deploys
- **Fast internal network** - faster than external connections
- **Free tier** - 90 days free, then 256MB free forever
- **Automatic backups** - Render handles this

---

## 🔧 Your Code Changes (Already Done!)

I've updated `backend/app/database.py` to:
- ✅ Auto-detect PostgreSQL vs SQLite
- ✅ Handle Render's `postgres://` → `postgresql://` URL format
- ✅ Use production-ready connection pooling for PostgreSQL
- ✅ Keep SQLite for local development (when no DATABASE_URL is set)

---

## 🧪 Local Development Still Works!

**No DATABASE_URL?** → Uses SQLite automatically
```bash
cd backend
python -m uvicorn main:app --reload
# ✅ Using SQLite database (Local Development)
```

**With DATABASE_URL?** → Uses PostgreSQL
```bash
export DATABASE_URL="postgresql://..."
python -m uvicorn main:app --reload
# ✅ Using PostgreSQL database (Production)
```

---

## 📊 Database Tables Created Automatically

When your app starts, it creates these tables:
- `users` - User profiles with Fitbit tokens, health data
- `activity_data` - Daily Fitbit activity records
- `intraday_steps` - Minute-level step data (if available)
- `sync_logs` - Fitbit sync operation logs

No manual SQL needed! SQLAlchemy creates everything from your models.

---

## 🚨 Troubleshooting

### **"Connection refused" or "could not connect"**
- Make sure you used **Internal Database URL** (not External)
- Check DATABASE_URL has no typos
- Verify database is in same region as backend

### **"relation does not exist"**
- Tables not created yet
- Check logs for `✅ Database tables created successfully!`
- Restart the service if needed

### **"SSL required"**
- Render PostgreSQL requires SSL by default
- Our code handles this automatically with `psycopg2-binary`

---

## 💰 Cost

- **First 90 days**: Completely FREE
- **After 90 days**: 256 MB storage FREE forever
- **Need more?**: $7/month for 1GB (plenty for thousands of users)

---

## ✅ Checklist

- [ ] Create PostgreSQL database on Render
- [ ] Copy "Internal Database URL"
- [ ] Add DATABASE_URL to backend environment variables
- [ ] Wait for redeploy
- [ ] Check logs show "Using PostgreSQL database"
- [ ] Test API endpoints work
- [ ] Verify user data persists after redeploy

---

## 🎉 You're Done!

Your database is now:
- ✅ Persistent (survives deploys)
- ✅ Fast (internal network)
- ✅ Free (90 days + 256MB forever)
- ✅ Production-ready

Your users' profiles, Fitbit data, and risk assessments will now be **permanently stored**! 🚀
