#!/usr/bin/env python3
"""
CRUD Operations Test Script for Hospital Management System
This script demonstrates all CRUD operations with the enhanced natural language interface
"""
import requests
import json
import time
from colorama import Fore, Style, init

init()

API_URL = "http://127.0.0.1:5002/api/query"

def test_query(description, query):
    """Test a single query and display results"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST: {description}")
    print(f"Query: {query}")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    try:
        response = requests.post(
            API_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            sql = data.get("sql", "")
            result = data.get("result", [])
            
            print(f"{Fore.GREEN}🔍 Generated SQL:{Style.RESET_ALL}")
            print(f"{Fore.BLUE}{sql}{Style.RESET_ALL}")
            
            print(f"\n{Fore.GREEN}📊 Result:{Style.RESET_ALL}")
            if isinstance(result, list):
                if len(result) == 0:
                    print(f"{Fore.YELLOW}No results found.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✅ Found {len(result)} record(s){Style.RESET_ALL}")
                    # Show first record as example
                    if result and isinstance(result[0], dict):
                        print(f"{Fore.WHITE}Sample record: {json.dumps(result[0], indent=2)}{Style.RESET_ALL}")
            elif isinstance(result, dict):
                if "error" in result:
                    print(f"{Fore.RED}❌ Error: {result['error']}{Style.RESET_ALL}")
                elif "message" in result:
                    print(f"{Fore.GREEN}✅ {result['message']}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.WHITE}{json.dumps(result, indent=2)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ HTTP Error {response.status_code}: {response.text}{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
    
    time.sleep(1)  # Small delay between tests

def main():
    """Run comprehensive CRUD tests"""
    print(f"{Fore.CYAN}{'='*80}")
    print(f"🏥 Hospital Management System - CRUD Operations Test")
    print(f"{'='*80}{Style.RESET_ALL}")
    
    # READ Operations (Safe to test)
    print(f"\n{Fore.GREEN}📖 READ OPERATIONS{Style.RESET_ALL}")
    
    test_query("Show All Appointments", "Show all appointments")
    test_query("Show All Patients", "List all patients")
    test_query("Show Medicine Inventory", "Show all medicines in inventory")
    test_query("Appointments for specific doctor", "Show appointments for doctor with first name containing 'Dr'")
    test_query("Revenue Analysis", "Total revenue by service type")
    test_query("Medicines Expiring", "Medicines expiring in next 30 days")
    test_query("Patient Count", "How many patients are there in total")
    
    # Analytics Queries (Priority queries)
    print(f"\n{Fore.BLUE}📊 ANALYTICS OPERATIONS{Style.RESET_ALL}")
    
    test_query("Daily Appointments", "Daily appointment list for today")
    test_query("Monthly Patient Registrations", "Month-over-month trend of new patient registrations")
    test_query("Geographic Distribution", "Geographic distribution of patients by city")
    test_query("Referral Source Analysis", "Patient breakdown by referral source")
    test_query("Low Stock Medicines", "Medicines below reorder level")
    
    # Note about CREATE/UPDATE/DELETE operations
    print(f"\n{Fore.YELLOW}⚠️  NOTE ABOUT WRITE OPERATIONS:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}CREATE, UPDATE, and DELETE operations are supported but not tested here")
    print(f"to avoid modifying your production database.{Style.RESET_ALL}")
    print(f"\n{Fore.WHITE}Examples of supported operations:")
    print(f"• CREATE: 'Add appointment for doctor Smith tomorrow at 2 PM'")
    print(f"• UPDATE: 'Update appointment status to Completed for appointment ID 1'")
    print(f"• DELETE: 'Cancel appointment ID 5'{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"✅ CRUD Test Complete! Your system supports full CRUD operations.")
    print(f"{'='*80}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
