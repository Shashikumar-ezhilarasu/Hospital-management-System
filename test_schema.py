#!/usr/bin/env python3
"""
Test schema fetching for Django chatbot
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from Django project
os.chdir('/Users/shashikumarezhil/Documents/JOB/hospital_chatbot')
load_dotenv()

def test_schema_fetch():
    """Test fetching database schema"""
    print("🔍 Testing Schema Fetching")
    print("=" * 50)
    
    # Database connection
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "testing2"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "300812")
        )
        print("✅ Database connected successfully")
        
        with conn.cursor() as cur:
            # Get all tables
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cur.fetchall()]
            print(f"📋 Found {len(tables)} tables:")
            for table in tables:
                print(f"   • {table}")
            
            print("\n🏗️ Building complete schema...")
            schema_lines = []
            
            for table in tables:
                cur.execute(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                
                schema_lines.append(f"{table} (")
                for col, dtype, nullable, default in columns:
                    nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                    default_str = f" DEFAULT {default}" if default else ""
                    schema_lines.append(f"    {col} {dtype} {nullable_str}{default_str}")
                schema_lines.append(")")
                schema_lines.append("")
            
            full_schema = "\n".join(schema_lines)
            print(f"\n📝 Complete Schema ({len(full_schema)} characters):")
            print("-" * 50)
            print(full_schema[:500] + "..." if len(full_schema) > 500 else full_schema)
            
            # Test specific tables that should exist
            expected_tables = ['patient_app_patient_details', 'user_app_user', 'inventory_app_druginventory']
            found_tables = [t for t in expected_tables if t in tables]
            missing_tables = [t for t in expected_tables if t not in tables]
            
            print(f"\n🎯 Key Tables Check:")
            print(f"   ✅ Found: {found_tables}")
            if missing_tables:
                print(f"   ❌ Missing: {missing_tables}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Schema fetch failed: {e}")
        return False

if __name__ == "__main__":
    test_schema_fetch()
