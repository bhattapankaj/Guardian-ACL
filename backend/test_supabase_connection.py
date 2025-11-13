"""
Test Supabase Connection
Quick script to verify your Supabase setup is working
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def test_connection():
    print("\n" + "="*60)
    print("🧪 TESTING SUPABASE CONNECTION")
    print("="*60 + "\n")
    
    try:
        # Test credentials
        print("🔑 Checking credentials...")
        if not SUPABASE_URL:
            print("❌ SUPABASE_URL not found in .env")
            return False
        if not SUPABASE_KEY:
            print("❌ SUPABASE_KEY not found in .env")
            return False
        
        print(f"✅ URL: {SUPABASE_URL}")
        print(f"✅ Key: {SUPABASE_KEY[:20]}...\n")
        
        # Initialize client
        print("📡 Connecting to Supabase...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Client initialized\n")
        
        # Test database - check if feedback table exists
        print("📊 Testing database (feedback table)...")
        try:
            result = supabase.table('feedback').select('*').limit(1).execute()
            print(f"✅ Table exists! Found {len(result.data)} rows\n")
        except Exception as e:
            if 'does not exist' in str(e).lower():
                print("⚠️  Table 'feedback' doesn't exist yet")
                print("   Run: python generate_supabase_sql.py")
                print("   Then execute the SQL in Supabase Dashboard\n")
                return False
            else:
                raise
        
        # Test storage - list buckets
        print("💾 Testing storage...")
        try:
            buckets = supabase.storage.list_buckets()
            print(f"✅ Storage accessible! Found {len(buckets)} bucket(s)")
            
            bucket_names = [b['name'] for b in buckets]
            if 'ml-models' in bucket_names:
                print("   ✅ 'ml-models' bucket exists\n")
            else:
                print("   ⚠️  'ml-models' bucket not found")
                print("   Create it in: Storage > New bucket > 'ml-models'\n")
        except Exception as e:
            print(f"⚠️  Storage test failed: {e}\n")
        
        # Test insert (optional)
        print("✍️  Testing insert...")
        try:
            test_data = {
                'user_id': 'test_connection',
                'date': '2025-11-13',
                'steps': 10000,
                'active_minutes': 60,
                'resting_hr': 65,
                'peak_hr_minutes': 30,
                'sleep_efficiency': 85.0,
                'minutes_asleep': 420,
                'weight': 75.0,
                'acl_history': False,
                'knee_pain': 2,
                'formula_risk': 0.35,
                'feedback': True
            }
            
            result = supabase.table('feedback').insert(test_data).execute()
            print("✅ Insert successful!")
            print(f"   Inserted record ID: {result.data[0]['id']}\n")
            
            # Clean up test data
            supabase.table('feedback').delete().eq('user_id', 'test_connection').execute()
            print("✅ Test data cleaned up\n")
            
        except Exception as e:
            print(f"⚠️  Insert test failed: {e}\n")
        
        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
        print("🎉 Your Supabase setup is working!\n")
        print("Next steps:")
        print("1. Start backend: uvicorn main:app --reload")
        print("2. Test API: http://localhost:8000/docs")
        print("3. Submit feedback: POST /api/feedback")
        print("4. Train model: POST /api/train\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED!")
        print(f"   Error: {str(e)}\n")
        print("Troubleshooting:")
        print("1. Check .env file has correct SUPABASE_URL and SUPABASE_KEY")
        print("2. Verify Supabase project is active")
        print("3. Run SQL setup: python generate_supabase_sql.py")
        print("4. Check network connection\n")
        return False

if __name__ == "__main__":
    test_connection()
