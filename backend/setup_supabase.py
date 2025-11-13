"""
Supabase Database Setup Script
Automatically creates tables and storage buckets using Python SDK
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# SQL to create feedback table
CREATE_FEEDBACK_TABLE = """
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
    feedback BOOLEAN NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes for performance
    CONSTRAINT unique_user_date UNIQUE (user_id, date)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_date ON feedback(date);
CREATE INDEX IF NOT EXISTS idx_feedback_positive ON feedback(feedback) WHERE feedback = TRUE;
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at);
"""

# SQL to enable RLS and create policies
CREATE_RLS_POLICIES = """
-- Enable Row Level Security (RLS)
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if it exists
DROP POLICY IF EXISTS "Allow all operations on feedback" ON feedback;

-- Create policy to allow all operations (adjust for your security needs)
CREATE POLICY "Allow all operations on feedback" ON feedback
    FOR ALL
    USING (true)
    WITH CHECK (true);
"""

# SQL to grant permissions
GRANT_PERMISSIONS = """
-- Grant permissions
GRANT ALL ON TABLE feedback TO postgres;
GRANT ALL ON TABLE feedback TO service_role;
GRANT ALL ON TABLE feedback TO anon;
GRANT ALL ON TABLE feedback TO authenticated;
"""


def setup_database():
    """Create database tables and indexes"""
    print("\n" + "="*60)
    print("🗄️  SUPABASE DATABASE SETUP")
    print("="*60 + "\n")
    
    try:
        # Initialize Supabase client
        print(f"📡 Connecting to Supabase...")
        print(f"   URL: {SUPABASE_URL}")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected successfully!\n")
        
        # Create feedback table
        print("📊 Creating feedback table...")
        response = supabase.rpc('exec_sql', {'sql': CREATE_FEEDBACK_TABLE}).execute()
        print("✅ Feedback table created!\n")
        
        # Enable RLS and create policies
        print("🔒 Setting up Row Level Security...")
        response = supabase.rpc('exec_sql', {'sql': CREATE_RLS_POLICIES}).execute()
        print("✅ RLS policies created!\n")
        
        # Grant permissions
        print("🔑 Granting permissions...")
        response = supabase.rpc('exec_sql', {'sql': GRANT_PERMISSIONS}).execute()
        print("✅ Permissions granted!\n")
        
        # Verify table exists
        print("🔍 Verifying table creation...")
        result = supabase.table('feedback').select('*').limit(1).execute()
        print("✅ Table verified!\n")
        
        print("="*60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        print("💡 Running alternative setup method...\n")
        return setup_with_rest_api()


def setup_with_rest_api():
    """Alternative method using direct SQL execution"""
    import requests
    
    try:
        print("📡 Using Supabase REST API for setup...")
        
        # Execute SQL directly using Supabase API
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Note: Direct SQL execution requires admin access
        # For production, use Supabase Dashboard SQL Editor
        print("\n⚠️  Direct SQL execution via API may not be available.")
        print("📝 Please run the following SQL in Supabase Dashboard:\n")
        print("="*60)
        print(CREATE_FEEDBACK_TABLE)
        print(CREATE_RLS_POLICIES)
        print(GRANT_PERMISSIONS)
        print("="*60 + "\n")
        
        print("📋 Steps to complete setup:")
        print("1. Go to: https://app.supabase.com/project/aatfljhlyyrgkjbegbvf/sql/new")
        print("2. Copy and paste the SQL above")
        print("3. Click 'Run' to execute\n")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        return False


def setup_storage():
    """Create storage buckets for ML models"""
    print("\n" + "="*60)
    print("💾 SUPABASE STORAGE SETUP")
    print("="*60 + "\n")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("📦 Creating 'ml-models' storage bucket...")
        
        # Try to create bucket
        try:
            bucket = supabase.storage.create_bucket(
                'ml-models',
                options={
                    'public': False,
                    'fileSizeLimit': 52428800  # 50 MB
                }
            )
            print("✅ Storage bucket created!\n")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print("ℹ️  Bucket already exists (OK)\n")
            else:
                raise
        
        # Verify bucket exists
        buckets = supabase.storage.list_buckets()
        bucket_names = [b['name'] for b in buckets]
        
        if 'ml-models' in bucket_names:
            print("✅ Verified: 'ml-models' bucket exists\n")
            print("="*60)
            print("✅ STORAGE SETUP COMPLETE!")
            print("="*60 + "\n")
            return True
        else:
            print("⚠️  Warning: Could not verify bucket creation\n")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        print("📋 Please create storage bucket manually:")
        print("1. Go to: https://app.supabase.com/project/aatfljhlyyrgkjbegbvf/storage/buckets")
        print("2. Click 'Create bucket'")
        print("3. Name: 'ml-models'")
        print("4. Public: No (private)")
        print("5. File size limit: 50 MB\n")
        return False


def test_connection():
    """Test Supabase connection"""
    print("\n" + "="*60)
    print("🧪 TESTING SUPABASE CONNECTION")
    print("="*60 + "\n")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test database connection
        print("📊 Testing database connection...")
        result = supabase.table('feedback').select('count').execute()
        print("✅ Database connection successful!\n")
        
        # Test storage connection
        print("💾 Testing storage connection...")
        buckets = supabase.storage.list_buckets()
        print(f"✅ Storage connection successful!")
        print(f"   Found {len(buckets)} bucket(s)\n")
        
        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
        print("🎉 Your Supabase setup is complete and working!\n")
        print("Next steps:")
        print("1. Start the backend server: uvicorn main:app --reload")
        print("2. Test prediction endpoint: POST /api/predict")
        print("3. Submit feedback: POST /api/feedback")
        print("4. Trigger training: POST /api/train\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}\n")
        return False


if __name__ == "__main__":
    print("\n🚀 Starting Supabase setup...\n")
    
    # Check environment variables
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Missing environment variables!")
        print("   Please set SUPABASE_URL and SUPABASE_KEY in .env file\n")
        exit(1)
    
    # Setup database
    db_success = setup_database()
    
    # Setup storage
    storage_success = setup_storage()
    
    # Test connection
    if db_success and storage_success:
        test_connection()
    else:
        print("\n⚠️  Setup incomplete. Please complete manual steps above.\n")
