#!/usr/bin/env python3
"""
Test script for the read-only functionality
"""
import requests
import time
from colorama import Fore, Style, init

init()

def test_read_functionality():
    """Test the read-only system"""
    API_URL = "http://127.0.0.1:5003/api/read"
    
    print(f"{Fore.CYAN}🧪 Testing Read-Only Hospital Management System{Style.RESET_ALL}")
    print("=" * 60)
    
    # Test queries that should work without hitting database constraints
    test_queries = [
        "Show database connection",
        "List all table names", 
        "Show all patients",
        "Count total patients",
        "List all doctors",
        "Show appointments", 
        "Display medicines in inventory",
        "Show patient count by gender"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{Fore.YELLOW}{i}. Testing: {query}{Style.RESET_ALL}")
        
        try:
            response = requests.post(
                API_URL,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "error" in result:
                    if "429" in result["error"]:
                        print(f"{Fore.YELLOW}   ⚠️  API quota reached - system working but rate limited{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}   ❌ Error: {result['error']}{Style.RESET_ALL}")
                else:
                    sql = result.get("sql", "")
                    data = result.get("result", [])
                    print(f"{Fore.GREEN}   ✅ Success{Style.RESET_ALL}")
                    print(f"   📝 SQL: {sql[:50]}...")
                    print(f"   📊 Records: {len(data) if isinstance(data, list) else 'N/A'}")
            else:
                print(f"{Fore.RED}   ❌ HTTP Error: {response.status_code}{Style.RESET_ALL}")
                
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}   ❌ Connection failed - server not running?{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}   ❌ Error: {e}{Style.RESET_ALL}")
        
        time.sleep(0.5)  # Avoid hitting rate limits too quickly
    
    print(f"\n{Fore.CYAN}Test completed! Start the servers to try interactive queries:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}1. python read.py     # Start the read-only server{Style.RESET_ALL}")
    print(f"{Fore.WHITE}2. python read_cli.py # Start the CLI interface{Style.RESET_ALL}")

if __name__ == "__main__":
    test_read_functionality()
