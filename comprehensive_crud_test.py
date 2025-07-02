#!/usr/bin/env python3
"""
Comprehensive CRUD Operations Test for Hospital Management System
This script tests all Create, Read, Update, Delete operations through the Flask API
"""
import requests
import json
import time
from datetime import datetime, date
from colorama import Fore, Style, init

# Initialize colorama
init()

API_URL = "http://127.0.0.1:5002/api/query"

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and date objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def make_query(query_text):
    """Make a query to the API and return the response"""
    try:
        response = requests.post(
            API_URL,
            json={"query": query_text},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {str(e)}"}

def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}🧪 {test_name}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

def print_result(query, result):
    """Print the query and its result"""
    print(f"\n{Fore.YELLOW}Query: {query}{Style.RESET_ALL}")
    
    if "error" in result:
        print(f"{Fore.RED}❌ Error: {result['error']}{Style.RESET_ALL}")
        return False
    
    sql = result.get("sql", "")
    data = result.get("result", [])
    
    print(f"{Fore.GREEN}🔍 Generated SQL: {sql}{Style.RESET_ALL}")
    
    if isinstance(data, list):
        if len(data) == 0:
            print(f"{Fore.YELLOW}📊 Result: No data returned{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}📊 Result: {len(data)} record(s) affected/returned{Style.RESET_ALL}")
            # Show first few records for verification
            for i, record in enumerate(data[:3]):
                print(f"  {i+1}: {json.dumps(record, cls=DateTimeEncoder, indent=2)}")
            if len(data) > 3:
                print(f"  ... and {len(data) - 3} more records")
    else:
        print(f"{Fore.GREEN}📊 Result: {json.dumps(data, cls=DateTimeEncoder, indent=2)}{Style.RESET_ALL}")
    
    return True

def test_create_operations():
    """Test CREATE operations"""
    print_test_header("CREATE OPERATIONS TEST")
    
    tests = [
        # Test creating a new patient
        "Add a new patient named John Smith, age 35, male, phone 9876543210, from Chennai",
        
        # Test creating an appointment
        "Create an appointment for patient John Smith with Dr. Rajesh on 2024-01-15 at 10:00 AM",
        
        # Test creating a medicine entry
        "Add medicine Paracetamol 500mg to inventory with quantity 100, expiry date 2025-12-31",
        
        # Test creating a doctor
        "Add a new doctor Dr. Sarah Wilson, specialization Cardiology, phone 9876543211"
    ]
    
    success_count = 0
    for query in tests:
        result = make_query(query)
        if print_result(query, result):
            success_count += 1
        time.sleep(1)  # Brief pause between operations
    
    print(f"\n{Fore.GREEN}✅ CREATE Tests: {success_count}/{len(tests)} successful{Style.RESET_ALL}")
    return success_count == len(tests)

def test_read_operations():
    """Test READ operations"""
    print_test_header("READ OPERATIONS TEST")
    
    tests = [
        # Basic read operations
        "Show all patients",
        "List all doctors",
        "Show all appointments",
        "Display all medicines in inventory",
        
        # Filtered reads
        "Show patients from Chennai",
        "List appointments for today",
        "Show medicines expiring in next 30 days",
        "Display male patients",
        
        # Analytics queries
        "Total number of patients by gender",
        "Count of appointments by doctor",
        "List of medicines below stock level 50"
    ]
    
    success_count = 0
    for query in tests:
        result = make_query(query)
        if print_result(query, result):
            success_count += 1
        time.sleep(1)
    
    print(f"\n{Fore.GREEN}✅ READ Tests: {success_count}/{len(tests)} successful{Style.RESET_ALL}")
    return success_count == len(tests)

def test_update_operations():
    """Test UPDATE operations"""
    print_test_header("UPDATE OPERATIONS TEST")
    
    tests = [
        # Update patient information
        "Update John Smith's phone number to 9876543299",
        
        # Update appointment status
        "Mark appointment for John Smith as completed",
        
        # Update medicine quantity
        "Update Paracetamol quantity to 150",
        
        # Update doctor information
        "Update Dr. Sarah Wilson's phone to 9876543222"
    ]
    
    success_count = 0
    for query in tests:
        result = make_query(query)
        if print_result(query, result):
            success_count += 1
        time.sleep(1)
    
    print(f"\n{Fore.GREEN}✅ UPDATE Tests: {success_count}/{len(tests)} successful{Style.RESET_ALL}")
    return success_count == len(tests)

def test_delete_operations():
    """Test DELETE operations"""
    print_test_header("DELETE OPERATIONS TEST")
    
    tests = [
        # Delete appointment
        "Cancel the appointment for John Smith",
        
        # Delete medicine (be careful with this)
        "Remove expired medicines from inventory",
        
        # Note: We'll be careful about deleting patients/doctors as they might have dependencies
        "Delete patients who have no appointments or medical history"
    ]
    
    success_count = 0
    for query in tests:
        result = make_query(query)
        if print_result(query, result):
            success_count += 1
        time.sleep(1)
    
    print(f"\n{Fore.GREEN}✅ DELETE Tests: {success_count}/{len(tests)} successful{Style.RESET_ALL}")
    return success_count == len(tests)

def test_complex_queries():
    """Test complex analytical queries"""
    print_test_header("COMPLEX ANALYTICS TEST")
    
    tests = [
        "Show monthly patient registration trends for last 6 months",
        "Calculate total revenue by service type",
        "Find doctors with highest patient count",
        "Show patient distribution by city",
        "List upcoming appointments for next week",
        "Find medicines that need reordering",
        "Show success rate of different procedures",
        "Calculate average patient age by gender"
    ]
    
    success_count = 0
    for query in tests:
        result = make_query(query)
        if print_result(query, result):
            success_count += 1
        time.sleep(1)
    
    print(f"\n{Fore.GREEN}✅ ANALYTICS Tests: {success_count}/{len(tests)} successful{Style.RESET_ALL}")
    return success_count == len(tests)

def main():
    """Run all CRUD tests"""
    print(f"{Fore.MAGENTA}{'='*80}")
    print(f"{Fore.MAGENTA}🏥 COMPREHENSIVE HOSPITAL MANAGEMENT SYSTEM CRUD TEST")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    
    # Test API connectivity first
    print(f"\n{Fore.YELLOW}🔗 Testing API connectivity...{Style.RESET_ALL}")
    test_result = make_query("SELECT 1 as test")
    if "error" in test_result:
        print(f"{Fore.RED}❌ API connection failed: {test_result['error']}{Style.RESET_ALL}")
        return
    print(f"{Fore.GREEN}✅ API connection successful{Style.RESET_ALL}")
    
    # Run all test suites
    results = {
        "CREATE": test_create_operations(),
        "READ": test_read_operations(), 
        "UPDATE": test_update_operations(),
        "DELETE": test_delete_operations(),
        "ANALYTICS": test_complex_queries()
    }
    
    # Print final summary
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"{Fore.MAGENTA}📊 FINAL TEST SUMMARY")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    for test_type, passed in results.items():
        status = f"{Fore.GREEN}✅ PASSED" if passed else f"{Fore.RED}❌ FAILED"
        print(f"{test_type:12} : {status}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Overall Score: {total_passed}/{total_tests} test suites passed{Style.RESET_ALL}")
    
    if total_passed == total_tests:
        print(f"{Fore.GREEN}🎉 ALL TESTS PASSED! Your hospital management system is working perfectly!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  Some tests failed. Please review the errors above.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
