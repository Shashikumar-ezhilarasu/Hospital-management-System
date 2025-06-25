import psycopg2
from datetime import datetime, timedelta

# --- SETUP POSTGRES CONNECTION ---
conn = psycopg2.connect(
    host="localhost",
    database="Hospital Mgmt",
    user="postgres",
    password="300812"
)

def predefined_queries():
    print("""
📊 Available Insights:
1️⃣  Daily appointment list (filterable by doctor)
2️⃣  Total revenue by service type
3️⃣  Follow-up required for pregnancy results
4️⃣  Monthly list of IUI/OI/IVF procedures
5️⃣  Success rate of IUI/OI/IVF procedures
6️⃣  Month-over-month new patient registrations
7️⃣  Geographic distribution (city, district, locality)
8️⃣  Referral source breakdown
9️⃣  Medicines expiring in next X days
🔟  Medicines below reorder level
🔚  Exit
""")
    return input("Enter your choice (1-10 or 🔚 to exit): ").strip()

def build_sql(choice):
    if choice == "1":
        doctor = input("Doctor name: ")
        date = input("Date (YYYY-MM-DD, default today): ") or datetime.today().strftime('%Y-%m-%d')
        return f"""
SELECT name, date, time, service_type, phonenumber
FROM patient_app_appointment
WHERE doctor_id_id IN (
    SELECT id FROM user_app_user WHERE first_name = '{doctor}' OR user_name = '{doctor}'
)
AND date = '{date}'
ORDER BY time;
"""
    elif choice == "2":
        return """
SELECT service_type, SUM(bill_price) AS total_revenue
FROM patient_app_billreports
GROUP BY service_type
ORDER BY total_revenue DESC;
"""
    elif choice == "3":
        return """
SELECT p.id, p.first_name, p.last_name, pr.name AS procedure_name
FROM patient_app_patient_details p
JOIN inpatient_app_inpatient i ON p.id = i.patient_id
JOIN inpatient_app_procedure pr ON i.procedure_id = pr.id
WHERE pr.name IN ('IUI', 'IVF', 'OI')
AND i.status != 'success';
"""
    elif choice == "4":
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
        return """
SELECT pr.name AS procedure_name,
COUNT(*) FILTER (WHERE i.status = 'success')::FLOAT / NULLIF(COUNT(*), 0) AS success_rate
FROM inpatient_app_inpatient i
JOIN inpatient_app_procedure pr ON i.procedure_id = pr.id
WHERE pr.name IN ('IUI', 'IVF', 'OI')
GROUP BY pr.name;
"""
    elif choice == "6":
        return """
SELECT TO_CHAR(created_date, 'YYYY-MM') AS month, COUNT(*) AS registrations
FROM patient_app_patient_details
GROUP BY month
ORDER BY month;
"""
    elif choice == "7":
        return """
SELECT city, district, locality_name, COUNT(*) AS patient_count
FROM patient_app_patient_details
GROUP BY city, district, locality_name
ORDER BY patient_count DESC;
"""
    elif choice == "8":
        return """
SELECT referred_by AS referral_source, COUNT(*) AS patient_count
FROM patient_app_patient_details
GROUP BY referred_by
ORDER BY patient_count DESC;
"""
    elif choice == "9":
        days = int(input("Enter number of days (e.g., 30, 60, 90): "))
        target_date = (datetime.today() + timedelta(days=days)).strftime('%Y-%m-%d')
        return f"""
SELECT name, expiry_date, quantity
FROM inventory_app_druginventory
WHERE expiry_date <= '{target_date}'
ORDER BY expiry_date;
"""
    elif choice == "10":
        return """
SELECT name, quantity, category_id
FROM inventory_app_druginventory
WHERE quantity < 10
ORDER BY quantity;
"""
    else:
        return None

def execute_sql(sql):
    if not sql:
        print("No query to execute.")
        return
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql)
            if cursor.description:  # SELECT query
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                if rows:
                    print("\nResults:")
                    print("-" * 40)
                    print("\t".join(columns))
                    for row in rows:
                        print("\t".join([str(item) for item in row]))
                else:
                    print("✅ No records found.")
            else:
                conn.commit()
                print("✅ Query executed successfully.")
        except Exception as e:
            print(f"❌ Error executing SQL: {e}")
            conn.rollback()

def main():
    print("🩺 Hospital DB Insights Assistant")
    while True:
        choice = predefined_queries()
        if choice == "🔚":
            break
        sql = build_sql(choice)
        if sql:
            print(f"\nGenerated SQL:\n{sql}")
            execute_sql(sql)
    conn.close()
    print("\n🔒 Connection closed.")

if __name__ == "__main__":
    main()
