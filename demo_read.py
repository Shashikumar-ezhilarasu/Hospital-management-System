#!/usr/bin/env python3
"""
Demo script for the read-only Hospital Management System
"""
import requests
import time
from colorama import Fore, Style, init

init()

def demo_read_system():
    """Demonstrate the read-only system functionality"""
    API_URL = "http://127.0.0.1:5003/api/read"
    
    print(f"{Fore.MAGENTA}{'='*70}")
    print(f"{Fore.MAGENTA}🏥 HOSPITAL MANAGEMENT SYSTEM - READ-ONLY DEMO")
    print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}This demo shows how the read-only system works:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}✅ Safe - Only SELECT queries are allowed{Style.RESET_ALL}")
    print(f"{Fore.WHITE}✅ Intelligent - Converts natural language to SQL{Style.RESET_ALL}")
    print(f"{Fore.WHITE}✅ Secure - Blocks dangerous operations{Style.RESET_ALL}")
    
    demo_queries = [
        {
            "query": "show all patients",
            "description": "Basic patient listing"
        },
        {
            "query": "list all doctors",
            "description": "Doctor information"
        },
        {
            "query": "show appointments",
            "description": "Appointment data with joins"
        },
        {
            "query": "count patients",
            "description": "Analytics query"
        },
        {
            "query": "delete all patients",
            "description": "🚫 Dangerous query (will be blocked)"
        }
    ]
    
    print(f"\n{Fore.YELLOW}🎯 Running demo queries...{Style.RESET_ALL}")
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n{Fore.CYAN}{'-'*50}")
        print(f"{Fore.CYAN}{i}. {demo['description']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Natural Language: \"{demo['query']}\"{Style.RESET_ALL}")
        
        try:
            response = requests.post(
                API_URL,
                json={"query": demo['query']},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                sql = result.get("sql", "")
                data = result.get("result", [])
                
                print(f"{Fore.GREEN}Generated SQL:{Style.RESET_ALL}")
                print(f"{Fore.BLUE}{sql}{Style.RESET_ALL}")
                
                if "Only SELECT queries are allowed" in sql:
                    print(f"{Fore.RED}🚫 Query blocked - security working!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}📊 Result: {len(data)} records returned{Style.RESET_ALL}")
                    
            else:
                print(f"{Fore.RED}❌ HTTP Error: {response.status_code}{Style.RESET_ALL}")
                
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}❌ Server not running. Please start with: python read.py{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        
        time.sleep(1)  # Brief pause between queries
    
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"{Fore.MAGENTA}🎉 DEMO COMPLETE!")
    print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}✅ What we demonstrated:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Natural language queries are converted to SQL{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Complex joins and analytics are supported{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Dangerous operations are automatically blocked{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Results are returned in structured JSON format{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}🚀 To use the interactive CLI:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}python read_cli.py{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}💡 Example queries you can try:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• \"Show patients from Chennai\"{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• \"List appointments for today\"{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• \"Find medicines expiring soon\"{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• \"Count patients by gender\"{Style.RESET_ALL}")

if __name__ == "__main__":
    demo_read_system()
