from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- Flask Setup ---
app = Flask(__name__)
CORS(app)
load_dotenv()

# --- Gemini Setup ---
genai.configure(api_key=os.getenv("AIzaSyCJ5B2zwFUaK6ncdgtLQzpwshtIIwVjPCo", ""))

# --- PostgreSQL Connection (your version) ---
conn = psycopg2.connect(
    host="localhost",
    database="Hospital Mgmt",
    user="postgres",
    password="300812"
)

# --- Load Schema from PostgreSQL ---
def load_schema():
    try:
        with conn.cursor() as cur:
            # Query to get table and column information from PostgreSQL information schema
            schema_query = """
            SELECT 
                t.table_name,
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default
            FROM 
                information_schema.tables t
            JOIN 
                information_schema.columns c ON t.table_name = c.table_name
            WHERE 
                t.table_schema = 'public'
                AND t.table_type = 'BASE TABLE'
            ORDER BY 
                t.table_name, c.ordinal_position;
            """
            
            cur.execute(schema_query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            
            # Build schema text
            schema_text = ""
            current_table = None
            
            for row in rows:
                row_dict = dict(zip(columns, row))
                table_name = row_dict['table_name']
                column_name = row_dict['column_name']
                data_type = row_dict['data_type']
                is_nullable = row_dict['is_nullable']
                column_default = row_dict['column_default']
                
                if current_table != table_name:
                    if current_table is not None:
                        schema_text += "\n"
                    schema_text += f"Table: {table_name}\n"
                    current_table = table_name
                
                nullable_info = "NOT NULL" if is_nullable == "NO" else "NULL"
                default_info = f" DEFAULT {column_default}" if column_default else ""
                schema_text += f"- {column_name}: {data_type} ({nullable_info}){default_info}\n"
            
            return schema_text.strip()
    except Exception as e:
        print(f"Error loading schema: {e}")
        return "-- Error loading schema from database"

SCHEMA_TEXT = load_schema()

# --- Generate SQL from Gemini ---
def generate_sql_from_nl(nl_query):
    prompt = f"""
You are a PostgreSQL SQL query generator for a Hospital Management System.

Given the following database schema:
{SCHEMA_TEXT}

Convert the following natural language instruction into a valid SQL query:
\"{nl_query}\"

IMPORTANT GUIDELINES:

**CRUD OPERATIONS:**
1. CREATE (INSERT):
   - For appointments: INSERT INTO patient_app_appointment (patient_id_id, doctor_id_id, date, time, status) VALUES (...)
   - For patients: INSERT INTO patient_app_patient_details (first_name, last_name, phone, email, date_of_birth) VALUES (...)
   - For medicines: INSERT INTO inventory_app_druginventory (name, quantity, expiry_date, vendor_id_id) VALUES (...)

2. READ (SELECT):
   - For appointments: SELECT * FROM patient_app_appointment WHERE ...
   - For patients: SELECT * FROM patient_app_patient_details WHERE ...
   - For medicines: SELECT * FROM inventory_app_druginventory WHERE ...

3. UPDATE:
   - For appointments: UPDATE patient_app_appointment SET status = 'value' WHERE id = X
   - For patients: UPDATE patient_app_patient_details SET phone = 'value' WHERE id = X
   - For medicines: UPDATE inventory_app_druginventory SET quantity = X WHERE name = 'value'

4. DELETE:
   - For appointments: DELETE FROM patient_app_appointment WHERE id = X
   - For patients: DELETE FROM patient_app_patient_details WHERE id = X
   - For medicines: DELETE FROM inventory_app_druginventory WHERE name = 'value'

**TABLE USAGE:**
- Appointments: patient_app_appointment
- Patients: patient_app_patient_details
- Revenue/Billing: patient_app_billreports
- Procedures: inpatient_app_procedure
- Inventory/Medicines: inventory_app_druginventory
- Users/Doctors: user_app_user

**COMMON PATTERNS:**
- Date functions: CURRENT_DATE, DATE_TRUNC('month', date_column)
- String matching: ILIKE '%value%' for case-insensitive search
- Joins: Use proper JOIN syntax when relating tables
- Aggregations: COUNT(*), SUM(amount), GROUP BY

**EXAMPLES:**
- "add appointment for doctor X" → INSERT INTO patient_app_appointment (doctor_id_id, date, status) VALUES ((SELECT id FROM user_app_user WHERE first_name ILIKE '%X%'), CURRENT_DATE, 'Scheduled')
- "update appointment status to completed" → UPDATE patient_app_appointment SET status = 'Completed' WHERE id = ?
- "delete appointment for patient John" → DELETE FROM patient_app_appointment WHERE patient_id_id = (SELECT id FROM patient_app_patient_details WHERE first_name ILIKE '%John%')
- "medicines expiring in 30 days" → SELECT * FROM inventory_app_druginventory WHERE expiry_date <= CURRENT_DATE + INTERVAL '30 days'

Return only the SQL query without any markdown formatting, comments, or explanations.
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        return response.text.strip().replace("```sql", "").replace("```", "")
    except Exception as e:
        return f"-- Gemini Error: {e}"

# --- Execute SQL on DB ---
def execute_sql(sql):
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                
                # Convert rows to dictionaries and handle date/time serialization
                result = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        column_name = columns[i]
                        # Handle date and time objects for JSON serialization
                        if hasattr(value, 'isoformat'):
                            row_dict[column_name] = value.isoformat()
                        elif value is None:
                            row_dict[column_name] = None
                        else:
                            row_dict[column_name] = str(value)
                    result.append(row_dict)
                
                return result
            else:
                conn.commit()
                return {"message": "Query executed successfully."}
    except Exception as e:
        return {"error": str(e)}

# --- Endpoint to handle NLP query ---
@app.route("/api/query", methods=["POST"])
def handle_query():
    data = request.get_json()
    nl_query = data.get("query", "")

    if not nl_query:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    sql = generate_sql_from_nl(nl_query)
    if sql.startswith("-- Gemini Error"):
        return jsonify({"error": sql}), 500

    print(f"🔍 Generated SQL: {sql}")
    result = execute_sql(sql)
    return jsonify({"sql": sql, "result": result})

# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True, port=5002)
