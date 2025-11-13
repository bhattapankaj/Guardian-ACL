# Supabase Setup Guide for ACL Guardian

## Overview
This guide walks you through setting up Supabase for the ACL Guardian backend, including database tables, storage buckets, and environment configuration.

---

## 1️⃣ Create Supabase Project

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Click **"New Project"**
3. Fill in project details:
   - **Name**: `acl-guardian`
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose closest to your users (e.g., `US West`)
4. Click **"Create new project"** (takes 1-2 minutes)

---

## 2️⃣ Create Database Tables

### Option A: Using Supabase SQL Editor (Recommended)

1. Navigate to **SQL Editor** in the Supabase dashboard
2. Click **"New Query"**
3. Copy and paste the following SQL:

```sql
-- ============================================
-- FEEDBACK TABLE
-- Stores user feedback on ACL risk predictions
-- ============================================

CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    
    -- Activity metrics
    steps INTEGER,
    active_minutes INTEGER,
    resting_hr INTEGER,
    peak_hr_minutes INTEGER,
    
    -- Sleep metrics
    sleep_efficiency REAL,
    minutes_asleep INTEGER,
    
    -- User profile
    weight REAL,
    acl_history BOOLEAN DEFAULT FALSE,
    knee_pain INTEGER CHECK (knee_pain >= 0 AND knee_pain <= 10),
    
    -- Risk prediction
    formula_risk REAL NOT NULL CHECK (formula_risk >= 0 AND formula_risk <= 1),
    
    -- User feedback
    feedback BOOLEAN NOT NULL,  -- TRUE = accurate, FALSE = inaccurate
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes for performance
    CONSTRAINT unique_user_date UNIQUE (user_id, date)
);

-- Create indexes for faster queries
CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_date ON feedback(date);
CREATE INDEX idx_feedback_positive ON feedback(feedback) WHERE feedback = TRUE;
CREATE INDEX idx_feedback_created_at ON feedback(created_at);

-- Enable Row Level Security (RLS)
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust for your security needs)
CREATE POLICY "Allow all operations on feedback" ON feedback
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- GRANT PERMISSIONS
-- ============================================
GRANT ALL ON TABLE feedback TO postgres;
GRANT ALL ON TABLE feedback TO service_role;
```

4. Click **"Run"** to execute the SQL
5. Verify the table was created under **"Table Editor"**

### Option B: Using Python Script

The `supabase_client.py` file includes SQL schema documentation. You can also create tables programmatically using the Supabase SDK.

---

## 3️⃣ Create Storage Bucket for ML Models

1. Navigate to **Storage** in the Supabase dashboard
2. Click **"Create a new bucket"**
3. Configure bucket:
   - **Name**: `ml-models`
   - **Public**: **No** (private bucket)
   - **File size limit**: 50 MB
   - **Allowed MIME types**: Leave blank (allow all)
4. Click **"Create bucket"**

### Set Bucket Policies

1. Click on the `ml-models` bucket
2. Go to **"Policies"** tab
3. Click **"New Policy"**
4. Create policy:
   - **Policy Name**: `Allow service role full access`
   - **Target Roles**: `service_role`
   - **Operations**: SELECT, INSERT, UPDATE, DELETE
5. Click **"Review"** → **"Save policy"**

---

## 4️⃣ Get API Credentials

1. Navigate to **Settings** → **API**
2. Copy the following values:

### Project URL
```
https://your-project-id.supabase.co
```

### API Keys

**Anon Key** (Public - safe for client-side):
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Service Role Key** (Secret - server-side only):
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

⚠️ **NEVER commit the service role key to Git!**

---

## 5️⃣ Update Environment Variables

### Local Development (`.env`)

Update `backend/.env`:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_service_role_key_here
```

### Production (Render)

Add environment variables in Render dashboard:

1. Go to your service in Render
2. Navigate to **Environment** tab
3. Add the following:
   - `SUPABASE_URL`: `https://your-project-id.supabase.co`
   - `SUPABASE_KEY`: `your_service_role_key_here`

---

## 6️⃣ Test Connection

Run the following Python script to test your Supabase connection:

```python
import os
from supabase import create_client

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

# Test database connection
result = supabase.table("feedback").select("*").limit(1).execute()
print(f"✅ Database connection successful: {result}")

# Test storage connection
buckets = supabase.storage.list_buckets()
print(f"✅ Storage buckets: {[b['name'] for b in buckets]}")
```

Save as `test_supabase.py` and run:

```bash
cd backend
python test_supabase.py
```

---

## 7️⃣ Database Schema Reference

### Feedback Table Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key (auto-increment) |
| `user_id` | TEXT | User identifier (Fitbit ID or manual) |
| `date` | DATE | Activity date |
| `steps` | INTEGER | Daily step count |
| `active_minutes` | INTEGER | Total active minutes |
| `resting_hr` | INTEGER | Resting heart rate (bpm) |
| `peak_hr_minutes` | INTEGER | Minutes in peak HR zone |
| `sleep_efficiency` | REAL | Sleep efficiency (0-100%) |
| `minutes_asleep` | INTEGER | Total sleep duration |
| `weight` | REAL | User weight (kg) |
| `acl_history` | BOOLEAN | Previous ACL injury? |
| `knee_pain` | INTEGER | Knee pain level (0-10) |
| `formula_risk` | REAL | Calculated risk score (0-1) |
| `feedback` | BOOLEAN | User feedback (true/false) |
| `created_at` | TIMESTAMP | Record creation time |

---

## 8️⃣ Storage Structure

```
ml-models/
├── models/
│   ├── user_global.pkl      # Global model (all users)
│   ├── user_ABC123.pkl      # User-specific model
│   └── user_XYZ789.pkl      # User-specific model
```

---

## 9️⃣ Next Steps

1. ✅ **Verify tables created**: Check Supabase Table Editor
2. ✅ **Verify storage bucket**: Check Supabase Storage
3. ✅ **Test connection**: Run `test_supabase.py`
4. ✅ **Update environment variables**: Local `.env` and Render dashboard
5. ✅ **Deploy to Render**: Follow `RENDER_DEPLOYMENT.md`

---

## 🆘 Troubleshooting

### Connection Errors

**Error**: `supabase.exceptions.SupabaseException: Invalid API key`

**Solution**: Verify you're using the **service role key** (not anon key)

---

### Table Not Found

**Error**: `relation "feedback" does not exist`

**Solution**: Run the SQL schema creation script in Supabase SQL Editor

---

### Storage Bucket Not Found

**Error**: `Bucket not found: ml-models`

**Solution**: Create the `ml-models` bucket in Supabase Storage

---

### Permission Denied

**Error**: `permission denied for table feedback`

**Solution**: Ensure RLS policies are configured correctly (see Step 2)

---

## 📚 Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python SDK](https://supabase.com/docs/reference/python/introduction)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

---

## 🔒 Security Best Practices

1. ✅ **Never commit** `SUPABASE_KEY` to Git
2. ✅ **Use environment variables** for all secrets
3. ✅ **Enable RLS** on all tables
4. ✅ **Use anon key** for client-side operations
5. ✅ **Use service role key** for server-side operations only
6. ✅ **Rotate keys** periodically
7. ✅ **Monitor usage** in Supabase dashboard

---

**Last Updated**: January 2025  
**Version**: 1.0.0
