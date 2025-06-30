import psycopg2  # PostgreSQL adapter for Python - used to connect and run queries on the PostgreSQL DB
from datetime import datetime, timedelta  # For handling date-related logic (like filtering upcoming expiry)

# --- DATABASE CONNECTION SETUP ---
# Connect to the PostgreSQL database where all hospital data is stored.
# Make sure to update password before deploying.
conn = psycopg2.connect(
    host="localhost",
    database="Hospital Mgmt",
    user="postgres",
    password="*****"  # Consider moving to environment variables or config file for production use
)

# --- MENU DISPLAY FUNCTION ---
def show_menu():
    # This function displays the available insights in a friendly menu format
    print("""
📊 Available Insights:
1️⃣ Daily appointment list (filterable by doctor)
2️⃣ Total revenue by service type
3️⃣ Follow-up required for pregnancy results
4️⃣ Monthly list of IUI/OI/IVF procedures
5️⃣ Success rate of IUI/OI/IVF procedures
6️⃣ Month-over-month new patient registrations
7️⃣ Geographic distribution (city, district, locality)
8️⃣ Referral source breakdown
9️⃣ Medicines expiring in next X days
🔟 Medicines below reorder level
0️⃣ Exit
""")
    return input("Pick an option (0-10): ").strip()  # Accepts user input and removes extra spaces

# --- FUNCTION TO EXECUTE SQL AND DISPLAY RESULTS ---
def execute_and_print(sql):
    # Accepts a SQL string, executes it, and prints results with headers
    with conn.cursor() as cur:
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]  # Get column names from result set

            print(f"\n🔹 Results ({len(rows)} rows):")
            print("-" * 60)
            print("\t".join(columns))  # Print headers
            for row in rows:
                # Print row-wise data with tab separation
                print("\t".join(str(col) if col is not None else '' for col in row))
            print("-" * 60)
        except Exception as e:
            # Rollback in case of error to prevent DB lock or inconsistencies
            print(f"❌ Error: {e}")
            conn.rollback()

# --- FUNCTION TO GENERATE SQL BASED ON MENU CHOICE ---
def get_query(choice):
    # Based on user's menu selection, generate the appropriate SQL query
    if choice == "1":
        # Filter appointments by doctor and date (default = today)
        doctor = input("Doctor name: ")
        date = input("Date (YYYY-MM-DD) [default today]: ") or datetime.today().strftime('%Y-%m-%d')
        return f"""
SELECT name, date, time, service_type, phonenumber
FROM patient_app_appointment
WHERE date = '{date}'
AND doctor_id_id IN (
    SELECT id FROM user_app_user
    WHERE first_name ILIKE '%{doctor}%' OR user_name ILIKE '%{doctor}%'
)
ORDER BY time;
"""

    elif choice == "2":
        # Calculate total revenue grouped by service type
        return """
SELECT a.service_type, SUM(b.bill_price) AS total_revenue
FROM patient_app_billreports b
JOIN patient_app_appointment a 
  ON a.patient_id_id = b.patient_id_id
GROUP BY a.service_type
ORDER BY total_revenue DESC; 
"""

    elif choice == "3":
        # List patients who underwent fertility procedures but did not mark status as success
        return """
SELECT p.id, p.first_name, p.last_name, pr.name AS procedure_name
FROM patient_app_patient_details p
JOIN inpatient_app_inpatient i ON p.id = i.patient_id
JOIN inpatient_app_procedure pr ON i.procedure_id = pr.id
WHERE pr.name IN ('IUI', 'IVF', 'OI')
AND (i.status IS NULL OR i.status != 'success');
"""

    elif choice == "4":
        # Get procedures (IUI/OI/IVF) performed in a specific month
        month = input("Month (YYYY-MM): ")
        return f"""
SELECT p.first_name, p.last_name, pr.name AS procedure_name, i.admission_date
FROM patient_app_patient_details p
JOIN inpatient_app_inpatient i ON p.id = i.patient_id
JOIN inpatient_app_procedure pr ON i.procedure_id = pr.id
WHERE pr.name IN ('IUI', 'IVF', 'OI')
AND TO_CHAR(i.admission_date, 'YYYY-MM') = '{month}';
"""

    elif choice == "5":
        # Calculate success rate percentage per fertility procedure type
        return """
SELECT pr.name AS procedure_name,
ROUND(100 * COUNT(*) FILTER (WHERE i.status = 'success')::NUMERIC / NULLIF(COUNT(*), 0), 2) AS success_rate_percent
FROM inpatient_app_inpatient i
JOIN inpatient_app_procedure pr ON i.procedure_id = pr.id
WHERE pr.name IN ('IUI', 'IVF', 'OI')
GROUP BY pr.name;
"""

    elif choice == "6":
        # Monthly new patient registrations grouped by year-month
        return """
SELECT TO_CHAR(created_date, 'YYYY-MM') AS month, COUNT(*) AS registrations
FROM patient_app_patient_details
GROUP BY month
ORDER BY month;
"""

    elif choice == "7":
        # Geographic distribution of patients (city, district, locality-wise)
        return """
SELECT city, district, locality_name, COUNT(*) AS patient_count
FROM patient_app_patient_details
GROUP BY city, district, locality_name
ORDER BY patient_count DESC;
"""

    elif choice == "8":
        # Breakdown of patients by referral source
        return """
SELECT referred_by, COUNT(*) AS patient_count
FROM patient_app_patient_details
GROUP BY referred_by
ORDER BY patient_count DESC;
"""

    elif choice == "9":
        # List of medicines expiring in the next X days (user-defined)
        days = int(input("Days until expiry (e.g. 30, 60, 90): "))
        target_date = (datetime.today() + timedelta(days=days)).strftime('%Y-%m-%d')
        return f"""
SELECT name, expiry_date, quantity
FROM inventory_app_druginventory
WHERE expiry_date <= '{target_date}'
ORDER BY expiry_date;
"""

    elif choice == "10":
        # List of medicines that are below a critical reorder level (hardcoded < 10)
        return """
SELECT name, quantity
FROM inventory_app_druginventory
WHERE quantity < 10
ORDER BY quantity;
"""

    elif choice == "0":
        # Exit condition
        return None

    else:
        # Handle invalid menu inputs
        print("❌ Invalid option.")
        return "INVALID"

# --- MAIN PROGRAM EXECUTION ---
def main():
    print("🩺 Hospital Insights Tool")
    while True:
        # Show options and take input
        choice = show_menu()
        query = get_query(choice)

        # Exit condition
        if query is None:
            break

        # Only execute valid queries
        if query != "INVALID":
            execute_and_print(query)

    # Always close DB connection before exit
    conn.close()
    print("🔒 Database connection closed.")

# Entry point check
if __name__ == "__main__":
    main()

# This script acts as a command-line analytics dashboard for hospital data.
# It connects to a PostgreSQL database and allows querying of various operational and clinical insights.
# To extend: Add authentication, export to CSV/PDF, or migrate to a web UI (e.g., using Streamlit or Flask).
# This code is designed to be run in a Python environment with access to the specified PostgreSQL database.
# Ensure psycopg2 is installed: pip install psycopg2-binary
# Update database credentials as needed.

#I have also tried creating a react based UI for this code, but it is working properly.i was thinking to add this feture as a component to it .
