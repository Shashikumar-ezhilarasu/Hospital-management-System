#!/usr/bin/env python3
"""
Command Line Interface for Natural Language Database Queries
"""
import requests
import json
import sys
from colorama import Fore, Style, init

# Initialize colorama for colored output
init()

API_URL = "http://127.0.0.1:5002/api/query"

def print_banner():
    """Print a welcome banner"""
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}🏥 Hospital Management Database Query Interface")
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.YELLOW}Type your questions in natural language!")
    print(f"{Fore.YELLOW}")
    print(f"{Fore.GREEN}📊 REPORTING & ANALYTICS:")
    print(f"{Fore.WHITE}  • Daily appointment list filterable by doctor and session")
    print(f"{Fore.WHITE}  • Total revenue by service type (Consultation, Scan, IUI, Pharmacy)")
    print(f"{Fore.WHITE}  • Month-over-month trend of new patient registrations")
    print(f"{Fore.WHITE}  • Geographic distribution of patients by city/district")
    print(f"{Fore.WHITE}  • Patient breakdown by referral source")
    print(f"{Fore.WHITE}  • Success rate for IUI, OI, or IVF procedures")
    print(f"{Fore.WHITE}")
    print(f"{Fore.GREEN}💊 INVENTORY MANAGEMENT:")
    print(f"{Fore.WHITE}  • Medicines expiring in next X days (30, 60, 90)")
    print(f"{Fore.WHITE}  • Medicines below reorder level")
    print(f"{Fore.WHITE}")
    print(f"{Fore.GREEN}🩺 PATIENT MANAGEMENT:")
    print(f"{Fore.WHITE}  • Patients needing pregnancy result follow-up")
    print(f"{Fore.WHITE}  • Monthly list of IUI, OI, IVF procedures")
    print(f"{Fore.WHITE}")
    print(f"{Fore.GREEN}📝 CRUD OPERATIONS:")
    print(f"{Fore.WHITE}  CREATE: • Add appointment for doctor [name]")
    print(f"{Fore.WHITE}          • Add new patient [name]")
    print(f"{Fore.WHITE}          • Add medicine to inventory")
    print(f"{Fore.WHITE}  READ:   • Show all appointments")
    print(f"{Fore.WHITE}          • List all patients")
    print(f"{Fore.WHITE}  UPDATE: • Update appointment status")
    print(f"{Fore.WHITE}          • Update patient information")
    print(f"{Fore.WHITE}  DELETE: • Cancel appointment")
    print(f"{Fore.WHITE}          • Remove patient record")
    print(f"{Fore.WHITE}")
    print(f"{Fore.YELLOW}Type 'quit', 'exit', 'help', or press Ctrl+C to exit")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

def format_result(data):
    """Format and display the query result"""
    if "error" in data:
        print(f"{Fore.RED}❌ Error: {data['error']}{Style.RESET_ALL}")
        return
    
    sql = data.get("sql", "")
    result = data.get("result", [])
    
    print(f"\n{Fore.GREEN}🔍 Generated SQL:{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{sql}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}📊 Results:{Style.RESET_ALL}")
    
    if isinstance(result, list):
        if len(result) == 0:
            print(f"{Fore.YELLOW}No results found.{Style.RESET_ALL}")
        else:
            # Print results in a table format
            if len(result) > 0 and isinstance(result[0], dict):
                # Get column headers
                headers = list(result[0].keys())
                
                # Print headers
                header_str = " | ".join(f"{header:15}" for header in headers)
                print(f"{Fore.CYAN}{header_str}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'-' * len(header_str)}{Style.RESET_ALL}")
                
                # Print rows
                for row in result[:10]:  # Limit to 10 rows for readability
                    row_str = " | ".join(f"{str(row.get(header, 'N/A')):15}" for header in headers)
                    print(f"{Fore.WHITE}{row_str}{Style.RESET_ALL}")
                
                if len(result) > 10:
                    print(f"{Fore.YELLOW}... and {len(result) - 10} more rows{Style.RESET_ALL}")
                
                print(f"\n{Fore.GREEN}Total records: {len(result)}{Style.RESET_ALL}")
            else:
                # Simple list display
                for item in result:
                    print(f"{Fore.WHITE}- {item}{Style.RESET_ALL}")
    elif isinstance(result, dict):
        if "message" in result:
            print(f"{Fore.GREEN}✅ {result['message']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE}{json.dumps(result, indent=2)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.WHITE}{result}{Style.RESET_ALL}")

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

def enhance_query(query):
    """Enhance queries with specific context and examples"""
    query_lower = query.lower()
    
    # CREATE Operations
    if any(keyword in query_lower for keyword in ['add appointment', 'create appointment', 'book appointment', 'schedule appointment']):
        enhanced = f"""
        {query}
        
        Context: INSERT a new appointment into patient_app_appointment table.
        Required fields: patient_id_id, doctor_id_id, date, time, status
        Example: INSERT INTO patient_app_appointment (patient_id_id, doctor_id_id, date, time, status) 
        VALUES (1, 2, '2025-07-03', '10:00:00', 'Scheduled');
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['add patient', 'create patient', 'new patient', 'register patient']):
        enhanced = f"""
        {query}
        
        Context: INSERT a new patient into patient_app_patient_details table.
        Required fields: first_name, last_name, phone, email, date_of_birth
        Example: INSERT INTO patient_app_patient_details (first_name, last_name, phone, email, date_of_birth) 
        VALUES ('John', 'Doe', '1234567890', 'john@email.com', '1990-01-01');
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['add medicine', 'add drug', 'create inventory', 'add inventory']):
        enhanced = f"""
        {query}
        
        Context: INSERT a new medicine into inventory_app_druginventory table.
        Required fields: name, quantity, expiry_date, vendor_id_id
        Example: INSERT INTO inventory_app_druginventory (name, quantity, expiry_date, vendor_id_id) 
        VALUES ('Medicine Name', 100, '2025-12-31', 1);
        """
        return enhanced
    
    # UPDATE Operations
    elif any(keyword in query_lower for keyword in ['update appointment', 'change appointment', 'modify appointment']):
        enhanced = f"""
        {query}
        
        Context: UPDATE appointment in patient_app_appointment table.
        Common updates: status, date, time
        Example: UPDATE patient_app_appointment SET status = 'Completed' WHERE id = 1;
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['update patient', 'change patient', 'modify patient']):
        enhanced = f"""
        {query}
        
        Context: UPDATE patient information in patient_app_patient_details table.
        Common updates: phone, email, address
        Example: UPDATE patient_app_patient_details SET phone = '9876543210' WHERE id = 1;
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['update medicine', 'update inventory', 'change stock']):
        enhanced = f"""
        {query}
        
        Context: UPDATE medicine inventory in inventory_app_druginventory table.
        Common updates: quantity, expiry_date, reorder_level
        Example: UPDATE inventory_app_druginventory SET quantity = 50 WHERE name = 'Medicine Name';
        """
        return enhanced
    
    # DELETE Operations
    elif any(keyword in query_lower for keyword in ['delete appointment', 'cancel appointment', 'remove appointment']):
        enhanced = f"""
        {query}
        
        Context: DELETE appointment from patient_app_appointment table.
        Use WHERE clause to specify which appointment to delete.
        Example: DELETE FROM patient_app_appointment WHERE id = 1;
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['delete patient', 'remove patient']):
        enhanced = f"""
        {query}
        
        Context: DELETE patient from patient_app_patient_details table.
        Use WHERE clause to specify which patient to delete.
        Example: DELETE FROM patient_app_patient_details WHERE id = 1;
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['delete medicine', 'remove medicine', 'delete inventory']):
        enhanced = f"""
        {query}
        
        Context: DELETE medicine from inventory_app_druginventory table.
        Use WHERE clause to specify which medicine to delete.
        Example: DELETE FROM inventory_app_druginventory WHERE name = 'Medicine Name';
        """
        return enhanced
    
    # Priority 1: Daily appointments and revenue
    elif any(keyword in query_lower for keyword in ['daily appointment', 'appointment list', 'appointments today', 'appointments for doctor', 'show appointments', 'list appointments']):
        enhanced = f"""
        {query}
        
        Context: SELECT appointment data from patient_app_appointment table. 
        Include doctor names, patient details, appointment dates, and session information.
        Filter by doctor name if specified and show today's appointments if requested.
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['total revenue', 'revenue by service', 'revenue collected', 'consultation scan iui pharmacy']):
        enhanced = f"""
        {query}
        
        Context: Calculate revenue from patient_app_billreports table.
        Break down by service types like Consultation, Scan, IUI, Pharmacy.
        Sum the amounts and group by service type.
        """
        return enhanced
    
    # Priority 2: Patient management and procedures
    elif any(keyword in query_lower for keyword in ['pregnancy result', 'pregnancy follow', 'follow up']):
        enhanced = f"""
        {query}
        
        Context: Find patients who need pregnancy result follow-up from patient_app_patient_details 
        and patient_app_patientreports tables. Look for pending pregnancy tests or results.
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['iui', 'oi', 'ivf', 'procedures', 'monthly list']):
        enhanced = f"""
        {query}
        
        Context: Find patients who underwent IUI, OI, or IVF procedures from inpatient_app_procedure 
        and patient_app_patient_details tables. Include procedure dates and outcomes.
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['success rate', 'procedure success']):
        enhanced = f"""
        {query}
        
        Context: Calculate success rates for IUI, OI, or IVF procedures from inpatient_app_procedure
        and patient reports. Compare successful vs total procedures.
        """
        return enhanced
    
    # Priority 3: Analytics and inventory
    elif any(keyword in query_lower for keyword in ['month-over-month', 'monthly trend', 'new patient registrations']):
        enhanced = f"""
        {query}
        
        Context: Analyze patient registration trends from patient_app_patient_details table.
        Group by month and compare registration counts over time.
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['geographic distribution', 'patients by city', 'district', 'locality']):
        enhanced = f"""
        {query}
        
        Context: Analyze patient distribution from patient_app_patient_details table.
        Group by city, district, and locality_name fields.
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['referral source', 'patients by referral']):
        enhanced = f"""
        {query}
        
        Context: Analyze patient referral sources from patient_app_patient_details table.
        Group by referral_source field and count patients.
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['medicines expiring', 'expiry', 'expire in']):
        enhanced = f"""
        {query}
        
        Context: Find expiring medicines from inventory_app_druginventory table.
        Compare expiry_date with current date plus specified days (30, 60, 90).
        Include medicine names, quantities, and exact expiry dates.
        """
        return enhanced
    
    elif any(keyword in query_lower for keyword in ['reorder level', 'below reorder', 'low stock']):
        enhanced = f"""
        {query}
        
        Context: Find medicines below reorder level from inventory_app_druginventory table.
        Compare current_stock with reorder_level field.
        """
        return enhanced
    
    return query

def show_help():
    """Show detailed help with examples"""
    print(f"\n{Fore.CYAN}📖 HELP - Natural Language Query Examples:{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}📝 CRUD OPERATIONS:{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}  ➕ CREATE (Add New Records):{Style.RESET_ALL}")
    print(f"{Fore.WHITE}    • 'Add appointment for doctor Shyam tomorrow at 10 AM'")
    print(f"{Fore.WHITE}    • 'Create new patient John Doe with phone 1234567890'")
    print(f"{Fore.WHITE}    • 'Add medicine Paracetamol 500mg to inventory'")
    print(f"{Fore.WHITE}    • 'Schedule appointment for patient ID 5 with doctor ID 2'")
    
    print(f"\n{Fore.BLUE}  📖 READ (Query/View Records):{Style.RESET_ALL}")
    print(f"{Fore.WHITE}    • 'Show all appointments'")
    print(f"{Fore.WHITE}    • 'List all patients'")
    print(f"{Fore.WHITE}    • 'Display appointments for doctor Shyam'")
    print(f"{Fore.WHITE}    • 'Show medicine inventory'")
    
    print(f"\n{Fore.YELLOW}  ✏️ UPDATE (Modify Records):{Style.RESET_ALL}")
    print(f"{Fore.WHITE}    • 'Update appointment status to Completed for appointment ID 1'")
    print(f"{Fore.WHITE}    • 'Change patient phone number to 9876543210 for patient ID 5'")
    print(f"{Fore.WHITE}    • 'Update medicine quantity to 100 for Paracetamol'")
    print(f"{Fore.WHITE}    • 'Modify appointment time to 2 PM for appointment ID 3'")
    
    print(f"\n{Fore.RED}  🗑️ DELETE (Remove Records):{Style.RESET_ALL}")
    print(f"{Fore.WHITE}    • 'Cancel appointment ID 1'")
    print(f"{Fore.WHITE}    • 'Delete patient record for patient ID 10'")
    print(f"{Fore.WHITE}    • 'Remove medicine Aspirin from inventory'")
    print(f"{Fore.WHITE}    • 'Delete appointment for doctor Shyam on July 5th'")
    
    print(f"\n{Fore.GREEN}🔥 PRIORITY 1 - Daily Operations:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • 'Daily appointment list for today'")
    print(f"{Fore.WHITE}  • 'Show appointments for doctor Shyam'")
    print(f"{Fore.WHITE}  • 'Total revenue by service type'")
    print(f"{Fore.WHITE}  • 'Revenue collected from consultations and scans'")
    
    print(f"\n{Fore.YELLOW}⚡ PRIORITY 2 - Patient Management:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • 'Patients needing pregnancy result follow-up'")
    print(f"{Fore.WHITE}  • 'Monthly list of IUI procedures'")
    print(f"{Fore.WHITE}  • 'Success rate for IVF procedures'")
    
    print(f"\n{Fore.BLUE}📊 PRIORITY 3 - Analytics & Inventory:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • 'Month-over-month trend of new patient registrations'")
    print(f"{Fore.WHITE}  • 'Geographic distribution of patients by city'")
    print(f"{Fore.WHITE}  • 'Patient breakdown by referral source'")
    print(f"{Fore.WHITE}  • 'Medicines expiring in next 30 days'")
    print(f"{Fore.WHITE}  • 'Medicines below reorder level'")
    
    print(f"\n{Fore.MAGENTA}💡 CRUD Tips:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • For CREATE: Be specific about what data to add")
    print(f"{Fore.WHITE}  • For READ: Use clear filters and conditions")
    print(f"{Fore.WHITE}  • For UPDATE: Specify what to change and the condition")
    print(f"{Fore.WHITE}  • For DELETE: Always specify clear conditions to avoid accidents")
    print(f"{Fore.WHITE}  • Use IDs when possible for precise operations")
    print(f"{Fore.WHITE}  • Type 'help' anytime to see this guide{Style.RESET_ALL}")

def main():
    """Main CLI loop"""
    print_banner()
    
    while True:
        try:
            # Get user input
            query = input(f"\n{Fore.MAGENTA}🤔 Your question: {Style.RESET_ALL}").strip()
            
            # Check for exit commands
            if query.lower() in ['quit', 'exit', 'q']:
                print(f"{Fore.CYAN}👋 Goodbye!{Style.RESET_ALL}")
                break
            
            # Show help
            if query.lower() in ['help', 'h', '?']:
                show_help()
                continue
            
            # Skip empty queries
            if not query:
                continue
            
            # Show processing message
            print(f"{Fore.YELLOW}🔄 Processing your query...{Style.RESET_ALL}")
            
            # Enhance query with context
            enhanced_query = enhance_query(query)
            
            # Send query and display result
            result = send_query(enhanced_query)
            format_result(result)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}👋 Goodbye!{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
