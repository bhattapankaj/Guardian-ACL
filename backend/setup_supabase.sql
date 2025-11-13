
-- ============================================
-- ACL GUARDIAN DATABASE SETUP
-- ============================================
-- Run this SQL in Supabase Dashboard SQL Editor
-- URL: https://app.supabase.com/project/aatfljhlyyrgkjbegbvf/sql/new
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
