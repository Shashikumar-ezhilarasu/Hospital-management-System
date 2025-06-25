import psycopg2
from datetime import datetime, timedelta

# Connect to your PostgreSQL DB
conn = psycopg2.connect(
    host="localhost",
    database="Hospital Mgmt",
    user="postgres",
    password="300812"
)

def show_menu():
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
    return input("Pick an option (0-10): ").strip()

def execute_and_print(sql):
    with conn.cursor() as cur:
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            print(f"\n🔹 Results ({len(rows)} rows):")
            print("-" * 60)
            print("\t".join(columns))
            for row in rows:
                print("\t".join(str(col) if col is not None else '' for col in row))
            print("-" * 60)
        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()

def get_query(choice):
    if choice == "1":
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
        return """
SELECT a.service_type, SUM(b.bill_price) AS total_revenue
FROM patient_app_billreports b
JOIN patient_app_appointment a 
  ON a.patient_id_id = b.patient_id_id
GROUP BY a.service_type
ORDER BY total_revenue DESC; 
"""
    elif choice == "3":
        return """
SELECT p.id, p.first_name, p.last_name, pr.name AS procedure_name
FROM patient_app_patient_details p
JOIN inpatient_app_inpatient i ON p.id = i.patient_id
JOIN inpatient_app_procedure pr ON i.procedure_id = pr.id
WHERE pr.name IN ('IUI', 'IVF', 'OI')
AND (i.status IS NULL OR i.status != 'success');
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
ROUND(100 * COUNT(*) FILTER (WHERE i.status = 'success')::NUMERIC / NULLIF(COUNT(*), 0), 2) AS success_rate_percent
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
SELECT referred_by, COUNT(*) AS patient_count
FROM patient_app_patient_details
GROUP BY referred_by
ORDER BY patient_count DESC;
"""
    elif choice == "9":
        days = int(input("Days until expiry (e.g. 30, 60, 90): "))
        target_date = (datetime.today() + timedelta(days=days)).strftime('%Y-%m-%d')
        return f"""
SELECT name, expiry_date, quantity
FROM inventory_app_druginventory
WHERE expiry_date <= '{target_date}'
ORDER BY expiry_date;
"""
    elif choice == "10":
        return """
SELECT name, quantity
FROM inventory_app_druginventory
WHERE quantity < 10
ORDER BY quantity;
"""
    elif choice == "0":
        return None
    else:
        print("❌ Invalid option.")
        return "INVALID"

def main():
    print("🩺 Hospital Insights Tool")
    while True:
        choice = show_menu()
        query = get_query(choice)
        if query is None:
            break
        if query != "INVALID":
            execute_and_print(query)
    conn.close()
    print("🔒 Database connection closed.")

if __name__ == "__main__":
    main()
# This code is designed to provide insights into hospital management data.
# It connects to a PostgreSQL database and allows users to query various insights related to patient appointments