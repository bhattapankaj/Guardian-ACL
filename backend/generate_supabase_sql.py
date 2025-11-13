"""
Simple Supabase Setup - Execute SQL via Dashboard
This script generates the SQL you need to run in Supabase Dashboard
"""

import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://aatfljhlyyrgkjbegbvf.supabase.co")
PROJECT_REF = SUPABASE_URL.split("//")[1].split(".")[0]

SQL_SETUP = """
-- ============================================
-- ACL GUARDIAN DATABASE SETUP
-- ============================================
-- Run this SQL in Supabase Dashboard SQL Editor
-- URL: https://app.supabase.com/project/{project_ref}/sql/new
-- ============================================

-- Drop table if exists (for clean setup)
DROP TABLE IF EXISTS feedback CASCADE;

-- Create feedback table
CREATE TABLE feedback (
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
    feedback BOOLEAN NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_user_date UNIQUE (user_id, date)
);

-- Create indexes
CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_date ON feedback(date);
CREATE INDEX idx_feedback_positive ON feedback(feedback) WHERE feedback = TRUE;
CREATE INDEX idx_feedback_created_at ON feedback(created_at);

-- Enable Row Level Security
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Create RLS policy (allow all for now - adjust for production)
CREATE POLICY "Allow all operations on feedback" ON feedback
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Grant permissions
GRANT ALL ON TABLE feedback TO postgres;
GRANT ALL ON TABLE feedback TO service_role;
GRANT ALL ON TABLE feedback TO anon;
GRANT ALL ON TABLE feedback TO authenticated;

-- ============================================
-- VERIFICATION
-- ============================================
-- Check if table was created successfully
SELECT 
    tablename, 
    schemaname 
FROM pg_tables 
WHERE tablename = 'feedback';

-- Check indexes
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'feedback';

-- Check RLS is enabled
SELECT 
    tablename, 
    rowsecurity 
FROM pg_tables 
WHERE tablename = 'feedback';

-- ============================================
-- SUCCESS!
-- ============================================
-- If you see results above, your database is ready!
-- Next: Create storage bucket for ML models
-- ============================================
"""

def main():
    print("\n" + "="*70)
    print("🗄️  SUPABASE DATABASE SETUP SQL")
    print("="*70 + "\n")
    
    print("📋 INSTRUCTIONS:\n")
    print(f"1. Open Supabase SQL Editor:")
    print(f"   https://app.supabase.com/project/{PROJECT_REF}/sql/new\n")
    print("2. Copy the SQL below and paste it into the editor\n")
    print("3. Click 'RUN' to execute\n")
    print("4. Verify the success messages at the bottom\n")
    
    print("="*70)
    print("SQL TO EXECUTE:")
    print("="*70 + "\n")
    
    sql = SQL_SETUP.replace("{project_ref}", PROJECT_REF)
    print(sql)
    
    print("\n" + "="*70)
    print("📦 STORAGE BUCKET SETUP")
    print("="*70 + "\n")
    
    print("After running the SQL above, create the storage bucket:\n")
    print(f"1. Open Supabase Storage:")
    print(f"   https://app.supabase.com/project/{PROJECT_REF}/storage/buckets\n")
    print("2. Click 'New bucket'\n")
    print("3. Settings:")
    print("   - Name: ml-models")
    print("   - Public: NO (keep private)")
    print("   - File size limit: 50 MB")
    print("   - Allowed MIME types: (leave empty)\n")
    print("4. Click 'Create bucket'\n")
    
    print("="*70)
    print("✅ NEXT STEPS")
    print("="*70 + "\n")
    
    print("After setup is complete:\n")
    print("1. Test connection:")
    print("   python test_supabase_connection.py\n")
    print("2. Start backend server:")
    print("   uvicorn main:app --reload\n")
    print("3. Test API endpoints:")
    print("   http://localhost:8000/docs\n")
    
    # Save SQL to file
    with open("setup_supabase.sql", "w") as f:
        f.write(sql)
    
    print("💾 SQL saved to: setup_supabase.sql\n")
    print("   You can also run this file directly in Supabase SQL Editor\n")

if __name__ == "__main__":
    main()
