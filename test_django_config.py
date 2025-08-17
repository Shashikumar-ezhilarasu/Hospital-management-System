#!/usr/bin/env python3
import os
import psycopg2
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from the Django project
os.chdir('/Users/shashikumarezhil/Documents/JOB/hospital_chatbot')
load_dotenv()

print("🧪 Testing Django Chatbot Configuration")
print("=" * 50)

# Test API Key
api_key = os.getenv("GOOGLE_API_KEY", "")
print(f"📋 API Key: {'✅ Found' if api_key else '❌ Missing'}")
if api_key:
    print(f"   Key starts with: {api_key[:10]}...")

# Test Database Connection
try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "Hospital Mgmt"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "300812")
    )
    print("🗄️  Database: ✅ Connected")
    
    # Test a simple query
    with conn.cursor() as cur:
        cur.execute("SELECT 1 as test")
        result = cur.fetchone()
        print(f"   Test query result: {result}")
    
    conn.close()
    
except Exception as e:
    print(f"🗄️  Database: ❌ Failed - {e}")

# Test Gemini AI
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Generate a simple SQL query: SELECT 1")
    print("🤖 Gemini AI: ✅ Working")
    print(f"   Sample response: {response.text.strip()[:50]}...")
except Exception as e:
    print(f"🤖 Gemini AI: ❌ Failed - {e}")

print("\n🎯 Configuration test complete!")
