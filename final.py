import psycopg2
import os
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# --- SETUP GEMINI ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

# --- SETUP POSTGRES CONNECTION ---
conn = psycopg2.connect(
    host="localhost",
    database="intern",
    user="postgres",
    password="300812"
)

# --- GEMINI SQL GENERATOR ---
def ask_gemini_for_sql(nl_query):
    schema = """ 
    Tables:
    - patient_app_appointment(appointment_date, doctor_name, session, ...)
    - patient_app_billreports(service_type, total_amount, bill_date, ...)
    - inpatient_app_procedure(procedure_name, procedure_date, outcome, ...)
    - inventory_app_druginventory(expiry_date, stock_count, reorder_level, ...)
    - patient_app_patient_details(referral_source, city, district, locality_name, registration_date, ...)
    - inpatient_app_inpatient(admission_date, hospital_id, ...)
    - inpatient_app_hospital(id, location, ...)
    """  

    prompt = f"""
You are a highly accurate SQL generator for PostgreSQL.
Given this database schema:
{schema}

Generate a syntactically correct SQL query for the instruction below. 
The instruction might not match exact database field names or table names. You must understand the human intent, map it to the schema, and produce the right SQL.

Instruction: "{nl_query}"

Only return the SQL query. Do not include explanations, formatting, or extra characters.
"""

    model = genai.GenerativeModel('gemini-2.0-pro')  # Use pro model for better understanding of complex language
    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        return sql_query
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return ""

# --- EXECUTE SQL ---
def execute_sql(sql):
    if not sql:
        print("No SQL to execute.")
        return
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql)
            if cursor.description:  # SELECT
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        print(row)
                else:
                    print("✅ No records found.")
            else:  # INSERT/UPDATE/DELETE
                conn.commit()
                print("✅ Query executed successfully.")
        except Exception as e:
            print(f"❌ SQL Execution error: {e}")
            conn.rollback()

# --- PREDEFINED QUERIES ---
def predefined_queries():
    print("""
📊 Insights Menu
🔹 1️⃣ Daily appointment list (filterable by doctor/session) [1st priority]
🔹 2️⃣ Total revenue by service type [1st priority]
🔹 3️⃣ Patients needing pregnancy follow-up [2nd priority]
🔹 4️⃣ Monthly IUI/OI/IVF list [2nd priority]
🔹 5️⃣ Success rate IUI/OI/IVF [2nd priority]
🔹 6️⃣ Month-over-month new registrations [3rd priority]
🔹 7️⃣ Geographic distribution of patients [3rd priority]
🔹 8️⃣ Referral source breakdown [3rd priority]
🔹 9️⃣ Medicines expiring in X days [3rd priority]
🔹 🔟 Medicines below reorder level [3rd priority]
💬 Free text natural language query
""")
    return input("Enter your choice (1-10 / 💬): ")

def build_sql(choice):
    if choice == "1":
        doctor = input("Doctor name (leave blank for all): ")
        session = input("Session (leave blank for all): ")
        date = input("Date (YYYY-MM-DD, default today): ") or datetime.today().strftime('%Y-%m-%d')
        conditions = [f"appointment_date = '{date}'"]
        if doctor:
            conditions.append(f"doctor_name = '{doctor}'")
        if session:
            conditions.append(f"session = '{session}'")
        where_clause = " AND ".join(conditions)
        return f"""
SELECT * FROM patient_app_appointment
WHERE {where_clause}
ORDER BY appointment_date;
"""
    elif choice == "2":
        return """
SELECT service_type, SUM(total_amount) AS total_revenue
FROM patient_app_billreports
GROUP BY service_type;
"""
    elif choice == "3":
        return """
SELECT * FROM inpatient_app_procedure
WHERE procedure_name IN ('IUI', 'IVF', 'OI')
AND outcome IS NULL;
"""
    elif choice == "4":
        month = input("Month (YYYY-MM, default current month): ") or datetime.today().strftime('%Y-%m')
        return f"""
SELECT * FROM inpatient_app_procedure
WHERE procedure_name IN ('IUI', 'IVF', 'OI')
AND TO_CHAR(procedure_date, 'YYYY-MM') = '{month}';
"""
    elif choice == "5":
        return """
SELECT procedure_name, 
COUNT(*) AS total_cases,
COUNT(*) FILTER (WHERE outcome = 'success') AS success_count,
ROUND(
    COUNT(*) FILTER (WHERE outcome = 'success')::FLOAT / NULLIF(COUNT(*),0) * 100, 2
) AS success_rate
FROM inpatient_app_procedure
WHERE procedure_name IN ('IUI', 'IVF', 'OI')
GROUP BY procedure_name;
"""
    elif choice == "6":
        return """
SELECT TO_CHAR(registration_date, 'YYYY-MM') AS month, COUNT(*) AS registrations
FROM patient_app_patient_details
GROUP BY month
ORDER BY month;
"""
    elif choice == "7":
        return """
SELECT city, district, locality_name, COUNT(*) AS total
FROM patient_app_patient_details
GROUP BY city, district, locality_name
ORDER BY total DESC;
"""
    elif choice == "8":
        return """
SELECT referral_source, COUNT(*) AS total
FROM patient_app_patient_details
GROUP BY referral_source;
"""
    elif choice == "9":
        days = int(input("Enter number of days (e.g. 30, 60, 90): "))
        target_date = (datetime.today() + timedelta(days=days)).strftime('%Y-%m-%d')
        return f"""
SELECT * FROM inventory_app_druginventory
WHERE expiry_date <= '{target_date}';
"""
    elif choice == "10":
        return """
SELECT * FROM inventory_app_druginventory
WHERE stock_count < reorder_level;
"""
    elif choice.strip() == "💬":
        query = input("Enter your natural language question: ")
        return ask_gemini_for_sql(query)
    else:
        print("Invalid choice.")
        return ""

# --- MAIN LOOP ---
def main():
    print("🏥 Hospital AI SQL Assistant (supports human-like queries)")
    while True:
        choice = predefined_queries()
        if choice.lower() == "exit":
            break
        sql = build_sql(choice)
        if sql:
            print(f"\n🔍 Generated SQL:\n{sql}")
            execute_sql(sql)

if __name__ == "__main__":
    main()
    conn.close()
    print("\n🔒 Connection closed.")
