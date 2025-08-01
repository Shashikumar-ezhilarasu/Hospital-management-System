import os
import json
import psycopg2
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "testing2"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "pass")
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def fetch_schema():
    """Fetch database schema"""
    conn = get_db_connection()
    if not conn:
        return ""
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            schema_lines = []
            
            for table in tables:
                cur.execute(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                schema_lines.append(f"{table} (")
                for col, dtype in columns:
                    schema_lines.append(f"    {col} ({dtype})")
                schema_lines.append(")")
                schema_lines.append("")
            
            return "\n".join(schema_lines)
    except Exception as e:
        print(f"Schema fetch error: {e}")
        return ""
    finally:
        conn.close()

def generate_sql(nl_query, schema):
    """Generate SQL query using Gemini AI"""
    prompt = f"""
You are an expert PostgreSQL query generator for a Hospital Management System.

Here is the database schema:
{schema}

Key Tables Available:
- patient_app_patient_details: Patient information (id, first_name, last_name, birthdate, gender, phonenumber, email, city, etc.)
- doctors: Doctor information (id, name, specialty)
- patient_app_appointment: Appointments (id, patient_id, doctor_id, date, time, status)
- inventory_app_druginventory: Medicine inventory (id, name, generic_name, dosage, quantity, price_per_unit, expiry_date)
- patient_app_billreports: Billing information (id, patient_id, service_id, amount, date)
- inpatient_app_procedure: Medical procedures (id, patient_id, procedure_name, date)
- followup_app_pregnancy: Pregnancy follow-ups (id, patient_id, followup_due_date, followup_status)
- services: Available services (id, service_name, price)

Convert this natural language question to a valid SQL query:
"{nl_query}"

Important rules:
1. Only return the SQL query, no explanations or markdown
2. Use proper PostgreSQL syntax
3. Include LIMIT clauses for SELECT queries (LIMIT 100 max)
4. Use ILIKE for case-insensitive text searches
5. Use proper JOIN syntax when connecting tables
6. For patient queries, use patient_app_patient_details table
7. For doctor queries, use doctors table
8. For appointment queries, use patient_app_appointment with JOINs as needed
9. Return only valid, executable SQL

Examples:
- "show all patients" → SELECT * FROM patient_app_patient_details LIMIT 100;
- "list doctors" → SELECT * FROM doctors LIMIT 100;
- "show appointments" → SELECT a.*, p.first_name, p.last_name, d.name as doctor_name FROM patient_app_appointment a JOIN patient_app_patient_details p ON a.patient_id = p.id JOIN doctors d ON a.doctor_id = d.id LIMIT 100;

Query:
"""
    
    try:
        # Check if API key is available
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key or api_key == "your_api_key_here":
            print("❌ No valid API key found!")
            return None
            
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        sql = response.text.strip().replace("```sql", "").replace("```", "").strip()
        print(f"✅ Generated SQL: {sql}")
        return sql
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        print(f"API Key status: {'Set' if os.getenv('GOOGLE_API_KEY') else 'Not set'}")
        return None

def execute_sql(sql):
    """Execute SQL query and return results"""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            
            if cur.description:
                # SELECT query - fetch results
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                
                # Convert to list of dictionaries
                results = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[columns[i]] = str(value) if value is not None else None
                    results.append(row_dict)
                
                return {
                    "success": True,
                    "type": "select",
                    "columns": columns,
                    "data": results,
                    "row_count": len(results)
                }
            else:
                # Non-SELECT query
                conn.commit()
                return {
                    "success": True,
                    "type": "modify",
                    "message": "Query executed successfully"
                }
                
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        conn.close()

def index(request):
    """Render the main chatbot page"""
    return render(request, 'chatbot/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """Handle chat requests via AJAX"""
    try:
        data = json.loads(request.body)
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return JsonResponse({"error": "Query cannot be empty"})
        
        # Fetch schema
        schema = fetch_schema()
        if not schema:
            return JsonResponse({"error": "Could not fetch database schema"})
        
        # Generate SQL
        sql = generate_sql(user_query, schema)
        if not sql:
            # Check specific reasons for failure
            api_key = os.getenv("GOOGLE_API_KEY", "")
            if not api_key or api_key == "your_api_key_here":
                return JsonResponse({"error": "API key not configured. Please check your .env file."})
            else:
                return JsonResponse({"error": "Could not generate SQL query. Please check your API key and try again."})
        
        # Execute SQL
        result = execute_sql(sql)
        
        response = {
            "user_query": user_query,
            "generated_sql": sql,
            "result": result
        }
        
        return JsonResponse(response)
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"})
    except Exception as e:
        return JsonResponse({"error": f"Server error: {str(e)}"})

@require_http_methods(["GET"])
def test_connection(request):
    """Test database connection"""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                conn.close()
                return JsonResponse({"status": "connected", "message": "Database connection successful"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Could not connect to database"})
