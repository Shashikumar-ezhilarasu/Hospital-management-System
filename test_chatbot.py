#!/usr/bin/env python3
"""
Test Django chatbot functionality
"""
import requests
import json
import time

API_URL = "http://127.0.0.1:8001"

def test_chatbot():
    print("🧪 Testing Django Chatbot")
    print("=" * 50)
    
    # Test connection
    try:
        response = requests.get(f"{API_URL}/test-connection/", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Connection test: {result.get('message', 'Success')}")
        else:
            print(f"❌ Connection test failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return
    
    # Test chat queries
    test_queries = [
        "show all patients",
        "list all doctors", 
        "show appointments",
        "count total patients",
        "show medicines in inventory"
    ]
    
    print(f"\n🤖 Testing {len(test_queries)} queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        
        try:
            response = requests.post(
                f"{API_URL}/chat/",
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "error" in result:
                    print(f"   ❌ Error: {result['error']}")
                else:
                    sql = result.get("generated_sql", "")
                    data = result.get("result", {})
                    
                    print(f"   ✅ SQL: {sql[:60]}...")
                    
                    if data.get("success"):
                        if data.get("type") == "select":
                            count = data.get("row_count", 0)
                            print(f"   📊 Results: {count} records")
                        else:
                            print(f"   📊 Results: {data.get('message', 'Success')}")
                    elif "error" in data:
                        print(f"   ❌ SQL Error: {data['error']}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request Error: {e}")
        
        time.sleep(0.5)  # Brief pause between requests
    
    print(f"\n🎉 Chatbot testing complete!")
    print(f"🌐 Access the web interface at: {API_URL}")

if __name__ == "__main__":
    test_chatbot()
