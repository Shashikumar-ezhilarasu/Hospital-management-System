from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# --- SETUP GEMINI ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

# --- SETUP POSTGRES CONNECTION ---
conn = psycopg2.connect(
    host="localhost",
    database="Hospital Mgmt",
    user="postgres",
    password="****"
)

# --- GEMINI SQL GENERATOR ---
def ask_gemini_for_sql(nl_query):
    schema = """ ... (your schema text here) ... """  # Keep your schema as is

    prompt = f"""
You are a PostgreSQL SQL query generator.
Given this PostgreSQL database schema:
{schema}

Convert the following natural language instruction into a valid PostgreSQL SQL query:
"{nl_query}"

Only return the SQL query. Do not include markdown formatting, explanations, or extra characters.
"""
    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        # Clean accidental markdown
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
Select an insight to run:
1️⃣ Daily appointment list (filterable by doctor)
2️⃣ Total revenue by service type
3️⃣ Monthly IUI/OI/IVF list
4️⃣ Success rate IUI/OI/IVF
5️⃣ Patients needing pregnancy follow-up
6️⃣ Medicines expiring in X days
7️⃣ Medicines below reorder level
8️⃣ Month-over-month new registrations
9️⃣ Geographic distribution
🔟 Referral source breakdown
💬 Free text natural language query
""")
    return input("Enter your choice (1-10 / 💬): ")

def build_sql(choice):
    if choice == "1":
        doctor = input("Doctor name: ")
        date = input("Date (YYYY-MM-DD, default today): ") or datetime.today().strftime('%Y-%m-%d')
        return f"""
SELECT * FROM patient_app_appointment
WHERE doctor_name = '{doctor}'
AND appointment_date = '{date}'
ORDER BY appointment_date;
"""
    elif choice == "2":
        return """
SELECT service_type, SUM(total_amount) AS total_revenue
FROM patient_app_billreports
GROUP BY service_type;
"""
    elif choice == "3":
        month = input("Month (YYYY-MM): ")
        return f"""
SELECT * FROM inpatient_app_procedure
WHERE procedure_name IN ('IUI', 'IVF', 'OI')
AND TO_CHAR(procedure_date, 'YYYY-MM') = '{month}';
"""
    elif choice == "4":
        return """
SELECT procedure_name, 
COUNT(*) FILTER (WHERE outcome='success')::FLOAT / NULLIF(COUNT(*),0) AS success_rate
FROM inpatient_app_procedure
WHERE procedure_name IN ('IUI', 'IVF', 'OI')
GROUP BY procedure_name;
"""
    elif choice == "5":
        return """
SELECT * FROM inpatient_app_procedure
WHERE procedure_name IN ('IUI', 'IVF', 'OI')
AND outcome IS NULL;
"""
    elif choice == "6":
        days = int(input("Enter number of days (e.g. 30, 60, 90): "))
        target_date = (datetime.today() + timedelta(days=days)).strftime('%Y-%m-%d')
        return f"""
SELECT * FROM inventory_app_druginventory
WHERE expiry_date <= '{target_date}';
"""
    elif choice == "7":
        return """
SELECT * FROM inventory_app_druginventory
WHERE stock_count < reorder_level;
"""
    elif choice == "8":
        return """
SELECT TO_CHAR(admission_date, 'YYYY-MM') AS month, COUNT(*) AS registrations
FROM inpatient_app_inpatient
GROUP BY month
ORDER BY month;
"""
    elif choice == "9":
        return """
SELECT location, COUNT(*) AS patients
FROM inpatient_app_hospital h
JOIN inpatient_app_inpatient i ON h.id = i.hospital_id
GROUP BY location;
"""
    elif choice == "10":
        return """
SELECT referral_source, COUNT(*) AS patients
FROM patient_app_patient_details
GROUP BY referral_source;
"""
    elif choice.strip() == "💬":
        query = input("Enter your natural language question: ")
        return ask_gemini_for_sql(query)
    else:
        print("Invalid choice.")
        return ""

# --- MAIN LOOP ---
def main():
    print("📊 Hospital DB AI Assistant")
    while True:
        choice = predefined_queries()
        if choice.lower() == "exit":
            break
        sql = build_sql(choice)
        if sql:
            print(f"\n🔍 Generated SQL:\n{sql}")
            execute_sql(sql)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="Hospital Mgmt",
        user="postgres",
        password="300812"
    )

@app.route('/api/daily-appointments', methods=['GET'])
def get_daily_appointments():
    doctor = request.args.get('doctor', '')
    date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT name, date, time, service_type, phonenumber
            FROM patient_app_appointment
            WHERE date = %s
            AND doctor_id_id IN (
                SELECT id FROM user_app_user
                WHERE first_name ILIKE %s OR user_name ILIKE %s
            )
            ORDER BY time;
        """, (date, f'%{doctor}%', f'%{doctor}%'))
        
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/revenue-by-service', methods=['GET'])
def get_revenue_by_service():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT a.service_type, SUM(b.bill_price) AS total_revenue
            FROM patient_app_billreports b
            JOIN patient_app_appointment a 
              ON a.patient_id_id = b.patient_id_id
            GROUP BY a.service_type
            ORDER BY total_revenue DESC;
        """)
        
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/follow-up-required', methods=['GET'])
def get_follow_up_required():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT p.id, p.first_name, p.last_name, pr.name AS procedure_name
            FROM patient_app_patient_details p
            JOIN inpatient_app_inpatient i ON p.id = i.patient_id
            JOIN inpatient_app_procedure pr ON i.procedure_id = pr.id
            WHERE pr.name IN ('IUI', 'IVF', 'OI')
            AND (i.status IS NULL OR i.status != 'success');
        """)
        
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/procedures-by-month', methods=['GET'])
def get_procedures_by_month():
    month = request.args.get('month')
    if not month:
        return jsonify({"error": "Month parameter is required"}), 400
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT p.first_name, p.last_name, pr.name AS procedure_name, i.admission_date
            FROM patient_app_patient_details p
            JOIN inpatient_app_inpatient i ON p.id = i.patient_id
            JOIN inpatient_app_procedure pr ON i.procedure_id = pr.id
            WHERE pr.name IN ('IUI', 'IVF', 'OI')
            AND TO_CHAR(i.admission_date, 'YYYY-MM') = %s;
        """, (month,))
        
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/procedure-success-rate', methods=['GET'])
def get_procedure_success_rate():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT pr.name AS procedure_name,
            ROUND(100 * COUNT(*) FILTER (WHERE i.status = 'success')::NUMERIC / NULLIF(COUNT(*), 0), 2) AS success_rate_percent
            FROM inpatient_app_inpatient i
            JOIN inpatient_app_procedure pr ON i.procedure_id = pr.id
            WHERE pr.name IN ('IUI', 'IVF', 'OI')
            GROUP BY pr.name;
        """)
        
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/patient-registrations', methods=['GET'])
def get_patient_registrations():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT TO_CHAR(created_date, 'YYYY-MM') AS month, COUNT(*) AS registrations
            FROM patient_app_patient_details
            GROUP BY month
            ORDER BY month;
        """)
        
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/geographic-distribution', methods=['GET'])
def get_geographic_distribution():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT city, district, locality_name, COUNT(*) AS patient_count
            FROM patient_app_patient_details
            GROUP BY city, district, locality_name
            ORDER BY patient_count DESC;
        """)
        
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/referral-sources', methods=['GET'])
def get_referral_sources():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT referred_by, COUNT(*) AS patient_count
            FROM patient_app_patient_details
            GROUP BY referred_by
            ORDER BY patient_count DESC;
        """)
        
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/expiring-medicines', methods=['GET'])
def get_expiring_medicines():
    days = int(request.args.get('days', 30))
    target_date = (datetime.today() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT name, expiry_date, quantity
            FROM inventory_app_druginventory
            WHERE expiry_date <= %s
            ORDER BY expiry_date;
        """, (target_date,))
        
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/low-stock-medicines', methods=['GET'])
def get_low_stock_medicines():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT name, quantity
            FROM inventory_app_druginventory
            WHERE quantity < 10
            ORDER BY quantity;
        """)
        
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
    conn.close()
    print("\n🔒 Connection closed.")
    app.run(debug=True, port=5000)
