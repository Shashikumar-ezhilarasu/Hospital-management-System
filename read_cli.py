#!/usr/bin/env python3
"""
Read-Only CLI for Hospital Management System
This CLI focuses exclusively on reading/displaying data from the database.
"""
import requests
import json
import sys
from colorama import Fore, Style, init
from datetime import datetime, date

# Initialize colorama for colored output
init()

API_URL = "http://127.0.0.1:5003/api/read"

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def print_banner():
    """Print a welcome banner for read-only operations"""
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}🏥 Hospital Management - READ-ONLY Query Interface")
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.GREEN}📖 READ OPERATIONS ONLY - Safe Data Exploration")
    print(f"{Fore.YELLOW}Type your questions in natural language to view data!")
    print(f"{Fore.WHITE}")
    
    print(f"{Fore.GREEN}🔍 EXAMPLE QUERIES:")
    print(f"{Fore.WHITE}  📋 Patient Information:")
    print(f"{Fore.WHITE}    • 'Show all patients'")
    print(f"{Fore.WHITE}    • 'List patients from Chennai'")
    print(f"{Fore.WHITE}    • 'Find patients named John'")
    print(f"{Fore.WHITE}    • 'Show male patients over age 30'")
    print(f"{Fore.WHITE}")
    
    print(f"{Fore.WHITE}  👨‍⚕️ Doctor Information:")
    print(f"{Fore.WHITE}    • 'List all doctors'")
    print(f"{Fore.WHITE}    • 'Show doctors in cardiology'")
    print(f"{Fore.WHITE}    • 'Find Dr. Smith'")
    print(f"{Fore.WHITE}")
    
    print(f"{Fore.WHITE}  📅 Appointments:")
    print(f"{Fore.WHITE}    • 'Show today's appointments'")
    print(f"{Fore.WHITE}    • 'List appointments for Dr. Rajesh'")
    print(f"{Fore.WHITE}    • 'Show upcoming appointments'")
    print(f"{Fore.WHITE}    • 'Find appointments for patient John'")
    print(f"{Fore.WHITE}")
    
    print(f"{Fore.WHITE}  💊 Inventory:")
    print(f"{Fore.WHITE}    • 'Show all medicines'")
    print(f"{Fore.WHITE}    • 'List medicines expiring soon'")
    print(f"{Fore.WHITE}    • 'Find Paracetamol in inventory'")
    print(f"{Fore.WHITE}    • 'Show medicines with low stock'")
    print(f"{Fore.WHITE}")
    
    print(f"{Fore.WHITE}  📊 Analytics:")
    print(f"{Fore.WHITE}    • 'Count patients by gender'")
    print(f"{Fore.WHITE}    • 'Show patient distribution by city'")
    print(f"{Fore.WHITE}    • 'Count appointments by doctor'")
    print(f"{Fore.WHITE}    • 'Show revenue by service type'")
    print(f"{Fore.WHITE}")
    
    print(f"{Fore.YELLOW}Commands: 'help' for examples, 'quit' to exit")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

def format_result(data):
    """Format and display the query result in a readable table"""
    if "error" in data:
        print(f"{Fore.RED}❌ Error: {data['error']}{Style.RESET_ALL}")
        return
    
    query = data.get("query", "")
    sql = data.get("sql", "")
    result = data.get("result", [])
    
    print(f"\n{Fore.BLUE}📝 Your Query: {query}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🔍 Generated SQL:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{sql}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}📊 Results:{Style.RESET_ALL}")
    
    if isinstance(result, list):
        if len(result) == 0:
            print(f"{Fore.YELLOW}📂 No data found for your query.{Style.RESET_ALL}")
            print(f"{Fore.WHITE}💡 Try rephrasing your question or check if the data exists.{Style.RESET_ALL}")
        else:
            # Display results in a nice table format
            if len(result) > 0 and isinstance(result[0], dict):
                headers = list(result[0].keys())
                
                # Calculate column widths
                col_widths = {}
                for header in headers:
                    max_width = len(str(header))
                    for row in result:
                        value_len = len(str(row.get(header, 'N/A')))
                        max_width = max(max_width, value_len)
                    col_widths[header] = min(max_width, 20)  # Cap at 20 chars
                
                # Print table header
                header_line = " | ".join(f"{header[:col_widths[header]]:<{col_widths[header]}}" for header in headers)
                print(f"{Fore.CYAN}{header_line}{Style.RESET_ALL}")
                
                # Print separator
                separator = "-+-".join("-" * col_widths[header] for header in headers)
                print(f"{Fore.CYAN}{separator}{Style.RESET_ALL}")
                
                # Print data rows (limit to first 20 for readability)
                display_rows = result[:20]
                for i, row in enumerate(display_rows):
                    row_data = []
                    for header in headers:
                        value = str(row.get(header, 'N/A'))
                        # Truncate long values
                        if len(value) > col_widths[header]:
                            value = value[:col_widths[header]-3] + "..."
                        row_data.append(f"{value:<{col_widths[header]}}")
                    
                    # Alternate row colors
                    color = Fore.WHITE if i % 2 == 0 else Fore.LIGHTBLACK_EX
                    row_line = " | ".join(row_data)
                    print(f"{color}{row_line}{Style.RESET_ALL}")
                
                # Summary
                print(f"\n{Fore.GREEN}📈 Summary:{Style.RESET_ALL}")
                print(f"{Fore.WHITE}  • Total records found: {len(result)}{Style.RESET_ALL}")
                if len(result) > 20:
                    print(f"{Fore.WHITE}  • Showing first 20 records{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}  • {len(result) - 20} more records available{Style.RESET_ALL}")
                
            else:
                # Simple list display for non-dictionary results
                for i, item in enumerate(result[:10]):
                    print(f"{Fore.WHITE}{i+1:2}. {item}{Style.RESET_ALL}")
                if len(result) > 10:
                    print(f"{Fore.YELLOW}   ... and {len(result) - 10} more items{Style.RESET_ALL}")
    
    elif isinstance(result, dict):
        print(f"{Fore.WHITE}{json.dumps(result, indent=2, cls=DateTimeEncoder)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.WHITE}{result}{Style.RESET_ALL}")

def send_query(query):
    """Send query to the read-only Flask API"""
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
        return {"error": "Cannot connect to the server. Make sure the read.py server is running on port 5003."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The query might be taking too long."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def show_examples():
    """Show detailed query examples"""
    print(f"\n{Fore.CYAN}📖 DETAILED QUERY EXAMPLES:{Style.RESET_ALL}")
    
    examples = [
        {
            "category": "🧑‍🤝‍🧑 Patient Queries",
            "examples": [
                "Show all patients",
                "List female patients",
                "Find patients from Mumbai",
                "Show patients over age 40",
                "Find patient with phone number 1234567890"
            ]
        },
        {
            "category": "👨‍⚕️ Doctor Queries", 
            "examples": [
                "List all doctors",
                "Show doctors with 'card' in specialization",
                "Find doctors named 'Sharma'",
                "Show doctor information"
            ]
        },
        {
            "category": "📅 Appointment Queries",
            "examples": [
                "Show today's appointments",
                "List all appointments",
                "Show appointments for next week",
                "Find completed appointments",
                "Show appointments for Dr. Rajesh"
            ]
        },
        {
            "category": "💊 Medicine/Inventory Queries",
            "examples": [
                "Show all medicines",
                "List medicines expiring in 30 days",
                "Find medicines with quantity less than 50",
                "Show Paracetamol details",
                "List medicines sorted by expiry date"
            ]
        },
        {
            "category": "📊 Analytics Queries",
            "examples": [
                "Count total patients",
                "Show patient count by gender",
                "Count appointments per doctor",
                "Show revenue by service type",
                "Calculate average patient age"
            ]
        }
    ]
    
    for category_info in examples:
        print(f"\n{Fore.GREEN}{category_info['category']}:{Style.RESET_ALL}")
        for example in category_info['examples']:
            print(f"{Fore.WHITE}  • \"{example}\"{Style.RESET_ALL}")

def main():
    """Main CLI loop for read-only operations"""
    print_banner()
    
    # Test server connection
    print(f"\n{Fore.YELLOW}🔗 Testing server connection...{Style.RESET_ALL}")
    test_result = send_query("SELECT 1 as test")
    if "error" in test_result:
        print(f"{Fore.RED}❌ Server connection failed: {test_result['error']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Make sure to run 'python read.py' in another terminal first!{Style.RESET_ALL}")
        return
    print(f"{Fore.GREEN}✅ Connected to read-only server{Style.RESET_ALL}")
    
    while True:
        try:
            # Get user input
            query = input(f"\n{Fore.MAGENTA}🔍 Enter your query (or 'help', 'quit'): {Style.RESET_ALL}").strip()
            
            # Handle commands
            if query.lower() in ['quit', 'exit', 'q']:
                print(f"{Fore.CYAN}👋 Thank you for using the Hospital Management Query System!{Style.RESET_ALL}")
                break
            
            if query.lower() in ['help', 'h', '?', 'examples']:
                show_examples()
                continue
            
            if not query:
                print(f"{Fore.YELLOW}💭 Please enter a query or type 'help' for examples.{Style.RESET_ALL}")
                continue
            
            # Show processing message
            print(f"{Fore.YELLOW}⏳ Processing your query...{Style.RESET_ALL}")
            
            # Send query and display result
            result = send_query(query)
            format_result(result)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}👋 Goodbye!{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
