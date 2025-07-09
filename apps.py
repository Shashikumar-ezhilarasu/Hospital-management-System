#!/usr/bin/env python3
import os
import psycopg2
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

# PostgreSQL connection
conn = psycopg2.connect(
    host="localhost",
    database="testing2",
    user="postgres",
    password="300812"
)

# Define your database schema as a string here
SCHEMA = """
-- Example schema (replace with your real one)
Tables:
1. patient_app_appointment (id, date, time, doctor_id_id, patient_id_id, service_type)
2. patient_app_patient_details (id, first_name, last_name, phone, referred_by, city, district, locality_name)
3. inventory_app_druginventory (id, name, quantity, expiry_date, reorder_level)
4. inpatient_app_procedure (id, name, outcome, procedure_date)
5. patient_app_billreports (id, bill_price, patient_id_id, service_type)
-- Add more as needed
"""

def generate_sql(nl_query):
    prompt = f"""
You are an expert PostgreSQL query generator.

Given this schema:
{SCHEMA}

Convert this natural language question to a valid SQL query:
\"{nl_query}\"

Only return the SQL query. No explanations, markdown, or extra output.
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        sql = response.text.strip().replace("```sql", "").replace("```", "")
        return sql
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None

def run_sql(sql):
    if not sql:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            if cur.description:
                # SELECT query
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                print("\n📊 Results:")
                print(" | ".join(columns))
                print("-" * 50)
                for row in rows:
                    print(" | ".join(str(col) for col in row))
                print(f"\n✅ {len(rows)} rows returned.")
            else:
                # INSERT/UPDATE/DELETE
                conn.commit()
                print("✅ Query executed successfully.")
    except Exception as e:
        print(f"❌ SQL Execution Error: {e}")
        conn.rollback()

def main():
    print("🩺 Hospital Management CLI (Type 'exit' to quit)\n")
    while True:
        try:
            question = input("❓> ").strip()
            if question.lower() in ['exit', 'quit']:
                break
            if not question:
                continue
            sql = generate_sql(question)
            print(f"\n🧠 Gemini SQL:\n{sql}")
            run_sql(sql)
        except KeyboardInterrupt:
            break
    conn.close()
    print("👋 Goodbye. Connection closed.")

if __name__ == "__main__":
    main()
