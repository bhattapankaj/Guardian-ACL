"""
Supabase client configuration for ACL Guardian.
Handles connection to Supabase PostgreSQL and Storage.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Supabase credentials from environment
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

# Initialize Supabase client
supabase: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance.
    Returns singleton client for database and storage operations.
    """
    global supabase
    
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "Missing Supabase credentials. "
                "Please set SUPABASE_URL and SUPABASE_KEY in .env file"
            )
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
    
    return supabase


def init_supabase_tables():
    """
    Initialize Supabase tables if they don't exist.
    Creates feedback table with proper schema.
    """
    client = get_supabase_client()
    
    # Note: In production, you should create tables through Supabase dashboard
    # or SQL migrations. This is just for reference.
    
    print("""
    📋 Supabase Table Setup Instructions:
    
    Run this SQL in your Supabase SQL editor to create the feedback table:
    
    CREATE TABLE IF NOT EXISTS feedback (
        id BIGSERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        date DATE NOT NULL,
        steps INT,
        active_minutes INT,
        resting_hr FLOAT,
        peak_hr_minutes INT,
        sleep_efficiency FLOAT,
        minutes_asleep INT,
        weight FLOAT,
        sport_type TEXT,
        acl_history BOOLEAN DEFAULT FALSE,
        knee_pain INT,
        formula_risk FLOAT,
        feedback BOOLEAN NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create index for faster user queries
    CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);
    CREATE INDEX IF NOT EXISTS idx_feedback_date ON feedback(date);
    CREATE INDEX IF NOT EXISTS idx_feedback_positive ON feedback(feedback) WHERE feedback = true;
    
    -- Create storage bucket for ML models
    INSERT INTO storage.buckets (id, name, public)
    VALUES ('models', 'models', false)
    ON CONFLICT (id) DO NOTHING;
    
    -- Set up storage policies (adjust as needed for your security requirements)
    CREATE POLICY "Allow authenticated users to read models"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'models' AND auth.role() = 'authenticated');
    
    CREATE POLICY "Allow service role to upload models"
    ON storage.objects FOR INSERT
    WITH CHECK (bucket_id = 'models' AND auth.role() = 'service_role');
    """)
    
    return client


# Helper functions for common operations
def store_feedback(feedback_data: dict) -> dict:
    """Store feedback record in Supabase."""
    client = get_supabase_client()
    
    try:
        result = client.table('feedback').insert(feedback_data).execute()
        print(f"✅ New feedback stored for user: {feedback_data.get('user_id')}")
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"❌ Error storing feedback: {e}")
        raise


def get_user_feedback(user_id: str, limit: int = 100) -> list:
    """Get feedback history for a specific user."""
    client = get_supabase_client()
    
    try:
        result = client.table('feedback')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('date', desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        print(f"❌ Error fetching feedback: {e}")
        raise


def get_positive_feedback(min_count: int = 100) -> list:
    """Get all positive feedback entries for model training."""
    client = get_supabase_client()
    
    try:
        result = client.table('feedback')\
            .select('*')\
            .eq('feedback', True)\
            .execute()
        
        data = result.data if result.data else []
        print(f"📊 Found {len(data)} positive feedback entries (need {min_count} minimum)")
        return data
    except Exception as e:
        print(f"❌ Error fetching positive feedback: {e}")
        raise


def upload_model_to_storage(user_id: str, model_file_path: str) -> str:
    """
    Upload trained model to Supabase Storage.
    Returns the public URL of the uploaded model.
    """
    client = get_supabase_client()
    
    try:
        # Read model file
        with open(model_file_path, 'rb') as f:
            model_data = f.read()
        
        # Upload to storage
        storage_path = f"models/user_{user_id}.pkl"
        
        # Remove old model if exists
        try:
            client.storage.from_('models').remove([storage_path])
        except:
            pass  # File doesn't exist, that's fine
        
        # Upload new model
        result = client.storage.from_('models').upload(
            path=storage_path,
            file=model_data,
            file_options={"content-type": "application/octet-stream"}
        )
        
        print(f"✅ Model uploaded successfully to: {storage_path}")
        return storage_path
    except Exception as e:
        print(f"❌ Error uploading model: {e}")
        raise


def download_model_from_storage(user_id: str, local_path: str) -> bool:
    """
    Download trained model from Supabase Storage.
    Returns True if successful, False otherwise.
    """
    client = get_supabase_client()
    
    try:
        storage_path = f"models/user_{user_id}.pkl"
        
        # Download file
        result = client.storage.from_('models').download(storage_path)
        
        # Save to local path
        with open(local_path, 'wb') as f:
            f.write(result)
        
        print(f"✅ Model downloaded successfully from: {storage_path}")
        return True
    except Exception as e:
        print(f"⚠️ Model not found in storage: {e}")
        return False


def model_exists_in_storage(user_id: str) -> bool:
    """Check if a trained model exists for a user."""
    client = get_supabase_client()
    
    try:
        storage_path = f"models/user_{user_id}.pkl"
        files = client.storage.from_('models').list()
        
        # Check if our model file exists
        for file in files:
            if file.get('name') == f"user_{user_id}.pkl":
                return True
        return False
    except Exception as e:
        print(f"⚠️ Error checking model existence: {e}")
        return False
