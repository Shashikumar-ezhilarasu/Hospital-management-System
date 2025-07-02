#!/usr/bin/env python3
"""
Simple Command Line Interface for Natural Language Database Queries
"""
import requests
import json
import sys

API_URL = "http://127.0.0.1:5002/api/query"

def print_banner():
    """Print a welcome banner"""
    print("=" * 60)
    print("🏥 Hospital Management Database Query Interface")
    print("=" * 60)
    print("Type your questions in natural language!")
    print("Examples:")
    print("  • How many appointments for doctor Shyam?")
    print("  • Show me all patients")
    print("  • List all appointments today")
    print("  • How many patients are there?")
    print("Type 'quit', 'exit', or press Ctrl+C to exit")
    print("=" * 60)

def format_result(data):
    """Format and display the query result"""
    if "error" in data:
        print(f"❌ Error: {data['error']}")
        return
    
    sql = data.get("sql", "")
    result = data.get("result", [])
    
    print(f"\n🔍 Generated SQL:")
    print(f"{sql}")
    
    print(f"\n📊 Results:")
    
    if isinstance(result, list):
        if len(result) == 0:
            print("No results found.")
        else:
            # Print results in a table format
            if len(result) > 0 and isinstance(result[0], dict):
                # Get column headers
                headers = list(result[0].keys())
                
                # Print headers
                header_str = " | ".join(f"{header:15}" for header in headers)
                print(header_str)
                print("-" * len(header_str))
                
                # Print rows
                for row in result[:10]:  # Limit to 10 rows for readability
                    row_str = " | ".join(f"{str(row.get(header, 'N/A')):15}" for header in headers)
                    print(row_str)
                
                if len(result) > 10:
                    print(f"... and {len(result) - 10} more rows")
                
                print(f"\nTotal records: {len(result)}")
            else:
                # Simple list display
                for item in result:
                    print(f"- {item}")
    elif isinstance(result, dict):
        if "message" in result:
            print(f"✅ {result['message']}")
        else:
            print(json.dumps(result, indent=2))
    else:
        print(result)

def send_query(query):
    """Send query to the Flask API"""
    try:
        response = requests.post(
            API_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to the server. Make sure the Flask app is running on port 5002."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The query might be taking too long."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    """Main CLI loop"""
    print_banner()
    
    while True:
        try:
            # Get user input
            query = input("\n🤔 Your question: ").strip()
            
            # Check for exit commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            # Skip empty queries
            if not query:
                continue
            
            # Show processing message
            print("🔄 Processing your query...")
            
            # Send query and display result
            result = send_query(query)
            format_result(result)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
