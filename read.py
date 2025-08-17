#!/usr/bin/env python3
"""
Hospital Management System - READ-ONLY Natural Language Query Interface
This script focuses exclusively on READ operations to fetch and display data from the database.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from datetime import datetime, date

# --- Flask Setup ---
app = Flask(__name__)
CORS(app)
load_dotenv()

# --- Gemini Setup ---
genai.configure(api_key=os.getenv("AIzaSyCJ5B2zwFUaK6ncdgtLQzpwshtIIwVjPCo", ""))

# --- PostgreSQL Connection ---
conn = psycopg2.connect(
    host="localhost",
    database="Hospital Mgmt",
    user="postgres",
    password="300812"
)

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

# --- Load Schema from PostgreSQL ---
def load_schema():
    try:
        with conn.cursor() as cur:
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
            rows = cur.fetchall()
            
            # Build schema dictionary
            schema = {}
            for row in rows:
                table_name, column_name, data_type, is_nullable, column_default = row
                if table_name not in schema:
                    schema[table_name] = []
                schema[table_name].append({
                    'column': column_name,
                    'type': data_type,
                    'nullable': is_nullable,
                    'default': column_default
                })
            
            return schema
    except Exception as e:
        print(f"Error loading schema: {e}")
        return {}

# Load schema at startup
DATABASE_SCHEMA = load_schema()

def create_read_only_prompt(query, schema):
    """Create a focused prompt for READ-ONLY operations"""
    prompt = f"""
You are a PostgreSQL query generator for a Hospital Management System. 
Generate ONLY SELECT queries for READ operations. Do NOT generate INSERT, UPDATE, DELETE, or DDL statements.

Database Schema:
{json.dumps(schema, indent=2)}

Key Tables and Their Purpose:
- patient_app_patient_details: Patient information (name, contact, demographics)
- patient_app_appointment: Appointments between patients and doctors
- user_app_user: Users including doctors and staff
- inventory_app_druginventory: Medicine/drug inventory
- patient_app_billreports: Billing and revenue information
- inpatient_app_procedure: Medical procedures performed
- patient_app_patientreports: Patient medical reports

User Query: {query}

IMPORTANT RULES:
1. Generate ONLY SELECT statements
2. Use proper table joins when relating data
3. Include meaningful column aliases for better readability
4. Use LIMIT clauses when appropriate to avoid large result sets
5. Handle case-insensitive searches with ILIKE
6. Return only valid PostgreSQL SELECT syntax
7. If the query seems to ask for CREATE/UPDATE/DELETE, convert it to a READ operation instead

Examples:
- "Show all patients" → SELECT * FROM patient_app_patient_details LIMIT 100;
- "Find Dr. Smith" → SELECT * FROM user_app_user WHERE first_name ILIKE '%Smith%' AND role = 'doctor';
- "Appointments today" → SELECT * FROM patient_app_appointment WHERE date = CURRENT_DATE;

Generate only the SQL query without explanations:
"""
    return prompt

def generate_sql_query(user_query):
    """Generate SQL query using Gemini AI - READ ONLY"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = create_read_only_prompt(user_query, DATABASE_SCHEMA)
        
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        
        # Clean up the SQL query
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        # Security check: Ensure it's a SELECT query only
        sql_upper = sql_query.upper().strip()
        if not sql_upper.startswith('SELECT'):
            return "SELECT 1 as message, 'Only SELECT queries are allowed for read operations' as note;"
        
        # Block dangerous keywords
        dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return "SELECT 1 as message, 'Only SELECT queries are allowed for read operations' as note;"
        
        return sql_query
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return f"-- Gemini Error: {error_msg}"
        return f"-- Error generating query: {error_msg}"

def execute_sql_query(sql_query):
    """Execute SQL query and return results"""
    try:
        with conn.cursor() as cur:
            # Use a fresh connection to avoid transaction issues
            conn.rollback()
            
            cur.execute(sql_query)
            
            # Get column names
            columns = [desc[0] for desc in cur.description] if cur.description else []
            
            # Fetch results
            rows = cur.fetchall()
            
            # Convert to list of dictionaries
            result = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    if i < len(columns):
                        row_dict[columns[i]] = value
                result.append(row_dict)
            
            return result
            
    except Exception as e:
        return {"error": str(e)}

@app.route('/api/read', methods=['POST'])
def handle_read_query():
    """Handle natural language read queries"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        print(f"📖 User Query: {user_query}")
        
        # Generate SQL query
        sql_query = generate_sql_query(user_query)
        print(f"🔍 Generated SQL: {sql_query}")
        
        # Check for errors in SQL generation
        if sql_query.startswith('--'):
            return jsonify({"error": sql_query}), 500
        
        # Execute query
        result = execute_sql_query(sql_query)
        
        # Return results
        response = {
            "query": user_query,
            "sql": sql_query,
            "result": result
        }
        
        # Convert datetime objects to strings manually
        response_json = json.dumps(response, cls=DateTimeEncoder)
        return app.response_class(response_json, mimetype='application/json')
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/schema', methods=['GET'])
def get_schema():
    """Get database schema information"""
    return jsonify(DATABASE_SCHEMA)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    print("🏥 Hospital Management System - READ-ONLY Query Interface")
    print("=" * 60)
    print("🔍 Only SELECT queries will be executed")
    print("🚫 CREATE, UPDATE, DELETE operations are blocked")
    print("📊 Server starting on http://127.0.0.1:5003")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5003)
