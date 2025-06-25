import psycopg2
import os
import google.generativeai as genai
from dotenv import load_dotenv

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

# --- GEMINI NATURAL LANGUAGE TO SQL ---
def ask_gemini_for_sql(nl_query):
    schema = """
This is a PostgreSQL database with the following tables:

- auth_group(id, name)
- auth_group_permissions(id, group_id, permission_id)
- auth_permission(id, name, content_type_id, codename)
- auth_user(id, username, email, is_staff)
- auth_user_groups(id, user_id, group_id)
- auth_user_user_permissions(id, user_id, permission_id)
- django_admin_log(id, object_repr, action_flag)
- django_content_type(id, app_label, model)
- django_migrations(id, app, name)
- django_session(session_key, session_data)
- inpatient_app_hospital(id, name, location)
- inpatient_app_inpatient(id, patient_id, hospital_id, admission_date)
- inpatient_app_procedure(id, inpatient_id, procedure_name, procedure_date)
- inventory_app_drugcategory(id, name)
- inventory_app_druginventory(id, category_id, drug_name, stock_count)
- inventory_app_vendor(id, name, contact)
- patient_app_appointment(id, patient_id, doctor_name, appointment_date)
- patient_app_billreports(id, patient_id, total_amount, bill_date)
- patient_app_patient_details(id, name, age, gender)
- patient_app_patientmedia(id, patient_id, file_path)
- patient_app_patientprescription(id, patient_id, drug_id, dosage)
- patient_app_patientreports(id, patient_id, report_type, report_date)
- user_app_user(id, full_name, role)
"""

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
        if sql_query.startswith("```sql"):
            sql_query = sql_query[len("```sql"):].strip()
        if sql_query.endswith("```"):
            sql_query = sql_query[:-len("```")].strip()

        return sql_query
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        return ""

# --- EXECUTE SQL ---
def execute_sql(sql):
    if not sql:
        print("No SQL query to execute.")
        return

    with conn.cursor() as cursor:
        try:
            cursor.execute(sql)
            if cursor.description:  # SELECT query
                rows = cursor.fetchall()
                if rows:
                    print("\n📊 Query Results:")
                    for row in rows:
                        print(row)
                else:
                    print("✅ Query executed successfully. No data returned.")
            else:
                conn.commit()
                print("✅ Query executed successfully.")
        except Exception as e:
            print(f"❌ Error executing SQL:\n{e}")
            conn.rollback()

# --- MAIN LOOP ---
def main():
    print("📊 Hospital DB Natural Language to SQL Interface")
    while True:
        nl_query = input("\nAsk about the hospital database (type 'exit' to quit): ")
        if nl_query.lower() == "exit":
            break
        print("Generating SQL query...")
        sql = ask_gemini_for_sql(nl_query)
        print(f"\n🔍 Generated SQL:\n{sql}")
        execute_sql(sql)

if __name__ == "__main__":
    main()
    if conn:
        conn.close()
        print("\n🔒 Database connection closed.")
