# Fitbit Integration Guide for ACL Guardian

## Overview

To get real athlete Fitbit data into your app, you'll use the **Fitbit Web API** with OAuth 2.0 authentication. This allows athletes to authorize your app to access their health data securely.

---

## 🎯 What You Need

### 1. **Fitbit Developer Account** (Free)
- Sign up at: https://dev.fitbit.com/
- Register your application
- Get your **Client ID** and **Client Secret**

### 2. **OAuth 2.0 Flow**
- Athletes click "Connect Fitbit" in your app
- They log into Fitbit and authorize your app
- You receive an **access token** to fetch their data
- Token expires after 8 hours, refresh token lasts 1 year

### 3. **Data You Can Access**
For ACL injury prevention, you'll track:
- ✅ **Activity** - Steps, distance, calories, active minutes
- ✅ **Heart Rate** - Resting HR, heart rate zones, variability
- ✅ **Sleep** - Sleep stages, duration, efficiency
- ✅ **Intraday Time Series** - Minute-by-minute steps, heart rate (requires special approval)
- ✅ **Device** - Battery level, last sync time

---

## 📋 Step-by-Step Setup

### **STEP 1: Register Your Fitbit App**

1. Go to https://dev.fitbit.com/apps/new
2. Fill in the form:

```
Application Name: ACL Guardian
Description: AI-powered ACL injury prevention using Fitbit data
Application Website: http://localhost:3000 (for development)
Organization: [Your Name/School]
Organization Website: http://localhost:3000

OAuth 2.0 Application Type: Server
Callback URL: http://localhost:3000/api/fitbit/callback
```

3. **Default Access Type**: Choose "Personal" for tournament demo
   - For production: Choose "Read-Only" or "Read & Write"

4. Click **Register** → You'll get:
   - **Client ID**: `23XXXX` (8 characters)
   - **Client Secret**: `abcdef1234567890` (32 characters)

⚠️ **SAVE THESE CREDENTIALS SECURELY!**

---

### **STEP 2: Request Intraday Access** (Important!)

For ACL prevention, you need **minute-by-minute data** (cadence, asymmetry detection).

1. Go to your app settings: https://dev.fitbit.com/apps
2. Click your app → "Edit Settings"
3. Scroll to **Intraday Access**
4. Fill out the form:
   ```
   Purpose: ACL injury prevention research for Louisiana HealthTech DevDay 2024
   Data needed: Minute-by-minute steps and heart rate for gait analysis
   Use case: Detect asymmetry patterns and overload to prevent ACL injuries
   ```
5. Submit → Usually approved in 1-3 business days

**For the tournament:** Start with hourly data, mention you're waiting for intraday approval.

---

## 🔧 Technical Implementation

### **Architecture Overview**

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Athlete   │   (1)   │  ACL Guardian│   (2)   │   Fitbit    │
│  (Browser)  ├────────>│   Frontend   ├────────>│  OAuth Page │
└─────────────┘         └──────────────┘         └──────┬──────┘
                                                         │ (3)
                        ┌──────────────┐                │
                        │  ACL Guardian│<───────────────┘
                        │   Backend    │   Authorization Code
                        └──────┬───────┘
                               │ (4) Exchange code for tokens
                               │
                        ┌──────▼───────┐
                        │   Fitbit API │
                        │ (Access Data)│
                        └──────────────┘
```

**Flow:**
1. User clicks "Connect Fitbit"
2. Frontend redirects to Fitbit OAuth page
3. User authorizes → Fitbit redirects back with code
4. Backend exchanges code for access token
5. Backend fetches athlete data every 15 minutes
6. Data stored in database, analyzed by ML model

---

### **Data You'll Fetch**

#### **For ACL Risk Assessment:**

1. **Activity Data** (GET /1/user/-/activities/date/[date].json)
   ```json
   {
     "steps": 12453,
     "distance": 9.2,
     "calories": 2341,
     "activeMinutes": 87,
     "sedentaryMinutes": 620
   }
   ```

2. **Heart Rate** (GET /1/user/-/activities/heart/date/[date]/1d.json)
   ```json
   {
     "restingHeartRate": 62,
     "heartRateZones": [
       {"name": "Peak", "minutes": 12},
       {"name": "Cardio", "minutes": 34}
     ]
   }
   ```

3. **Intraday Steps** (GET /1/user/-/activities/steps/date/[date]/1d/1min.json)
   ```json
   {
     "activities-steps-intraday": {
       "dataset": [
         {"time": "00:00:00", "value": 0},
         {"time": "00:01:00", "value": 3},
         {"time": "08:32:00", "value": 87}  // High cadence!
       ]
     }
   }
   ```

4. **Sleep Data** (GET /1.2/user/-/sleep/date/[date].json)
   ```json
   {
     "sleep": [{
       "duration": 28800000,  // 8 hours
       "efficiency": 92,
       "minutesAsleep": 442
     }]
   }
   ```

---

## 🚀 Implementation Plan

### **Phase 1: Basic OAuth Connection** (Today)
- ✅ Set up Fitbit developer account
- ✅ Create OAuth endpoints in backend
- ✅ Add "Connect Real Fitbit" button
- ✅ Store access/refresh tokens securely
- ✅ Fetch basic activity data

### **Phase 2: Data Sync** (Day 2)
- ✅ Automatic data refresh every 15 minutes
- ✅ Store historical data (14 days for trends)
- ✅ Handle token refresh (tokens expire every 8 hours)
- ✅ Error handling for sync failures

### **Phase 3: Advanced Analysis** (Day 3)
- ✅ Intraday data integration (when approved)
- ✅ Cadence calculation from minute steps
- ✅ Asymmetry detection (left/right stride patterns)
- ✅ Load management alerts

---

## 💾 Database Schema

You'll need to store:

```sql
-- Users table
users:
  - user_id (primary key)
  - email
  - name
  - fitbit_user_id
  - access_token (encrypted!)
  - refresh_token (encrypted!)
  - token_expires_at
  - created_at

-- Activity data table
activity_data:
  - id (primary key)
  - user_id (foreign key)
  - date
  - steps
  - distance
  - calories
  - active_minutes
  - resting_hr
  - sleep_duration
  - sleep_efficiency
  - synced_at

-- Intraday data (for detailed analysis)
intraday_steps:
  - id
  - user_id
  - timestamp (minute precision)
  - steps_count
  - cadence_calculated
```

---

## 🔒 Security Best Practices

### **1. Never Expose Credentials**
```python
# ❌ WRONG - Hard-coded secrets
CLIENT_ID = "23ABCD"
CLIENT_SECRET = "abc123def456"

# ✅ CORRECT - Environment variables
import os
CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET")
```

### **2. Encrypt Tokens in Database**
```python
from cryptography.fernet import Fernet

# Generate encryption key (store in .env)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt before storing
encrypted_token = cipher.encrypt(access_token.encode())

# Decrypt when using
access_token = cipher.decrypt(encrypted_token).decode()
```

### **3. Use HTTPS in Production**
- Fitbit requires HTTPS callback URLs in production
- Use ngrok for local testing: `ngrok http 3000`

---

## 📊 Data Refresh Strategy

### **Option 1: Polling (Simple)**
```python
# Backend cron job runs every 15 minutes
@scheduler.scheduled_job('interval', minutes=15)
def sync_all_users():
    users = get_active_users()
    for user in users:
        fetch_fitbit_data(user)
```

### **Option 2: Webhooks (Advanced)**
- Fitbit sends notifications when new data arrives
- More efficient, but requires HTTPS endpoint
- Best for production with many users

### **For Tournament: Use Polling**
- Simpler to set up
- Works on localhost
- 15-minute intervals are fine for demo

---

## 🧪 Testing Your Integration

### **1. Personal Data Test**
- Connect your own Fitbit
- Verify data appears in dashboard
- Check all 5 risk factors calculate correctly

### **2. Multi-Day Test**
- Let it sync for 3-5 days
- Verify trend charts work
- Test risk score changes over time

### **3. Edge Cases**
- What if Fitbit is dead/not synced?
- What if athlete doesn't wear it to bed?
- Handle missing data gracefully

---

## 📱 User Experience Flow

### **First-Time Connection:**
```
1. Athlete opens ACL Guardian
2. Clicks "Connect My Fitbit"
3. Redirected to Fitbit login
4. Authorizes app permissions
5. Redirected back to dashboard
6. Initial data sync (shows loading state)
7. Dashboard populates with real data ✅
```

### **Returning User:**
```
1. Opens app → Automatically logged in
2. Dashboard shows latest synced data
3. Sync happens in background every 15 min
4. Notification if sync fails or Fitbit not worn
```

---

## 🎓 Fitbit API Resources

- **Main Docs**: https://dev.fitbit.com/build/reference/web-api/
- **OAuth Guide**: https://dev.fitbit.com/build/reference/web-api/oauth2/
- **Activity Endpoints**: https://dev.fitbit.com/build/reference/web-api/activity/
- **Heart Rate**: https://dev.fitbit.com/build/reference/web-api/heartrate-timeseries/
- **Intraday Data**: https://dev.fitbit.com/build/reference/web-api/intraday/
- **Rate Limits**: 150 requests/hour per user

---

## 🏆 Tournament Demo Strategy

Since you might not have intraday access approved yet:

### **Plan A: Real Fitbit Data (Approved)**
- Show your actual activity data
- Live sync during demo
- "This is MY real Fitbit data from this week"

### **Plan B: Hybrid Mode (Pending Approval)**
- Connect real Fitbit for basic metrics
- Use synthetic data for minute-level analysis
- Explain: "We're waiting for intraday approval, but here's how it works..."

### **Demo Script:**
```
"ACL Guardian connects directly to an athlete's Fitbit.
[Click 'Connect Fitbit' button]
The athlete authorizes our app just once.
[Show OAuth flow]
Now we're syncing their data automatically every 15 minutes.
[Show real dashboard with your data]
Our AI analyzes their movement patterns to predict ACL injury risk."
```

---

## 🚦 Next Steps

**Ready to implement?** Here's what we'll build:

1. **Backend OAuth Endpoints** (30 min)
   - `/api/fitbit/authorize` - Start OAuth flow
   - `/api/fitbit/callback` - Handle authorization
   - `/api/fitbit/sync` - Fetch latest data

2. **Frontend Connection Button** (15 min)
   - Replace "Demo" button with "Connect Fitbit"
   - Show connection status
   - Display last sync time

3. **Data Sync Service** (45 min)
   - Background job to refresh data
   - Token refresh logic
   - Error handling

4. **Database Setup** (20 min)
   - SQLite for development
   - User and activity tables
   - Encrypted token storage

**Total Time**: ~2 hours for basic integration

---

## ❓ FAQ

**Q: Can I test without a Fitbit device?**
A: Yes! Create a Fitbit account, install the Fitbit app on your phone, and use "MobileTrack" mode. It uses your phone's sensors.

**Q: How much does the API cost?**
A: Free! Fitbit Web API is completely free for developers.

**Q: What about other devices (Apple Watch, Garmin)?**
A: Each has its own API. For the tournament, focus on Fitbit. Mention "expanding to Apple HealthKit and Garmin soon" in your demo.

**Q: How do I handle multiple users?**
A: Each user gets their own access token. Store it in your database with their user_id.

**Q: What if token refresh fails?**
A: User needs to re-authorize. Show a friendly "Reconnect Fitbit" button in the dashboard.

---

**Ready to start? Let me know and I'll help you implement each step!** 🚀
