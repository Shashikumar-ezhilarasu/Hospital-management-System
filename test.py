import psycopg2

# --- SETUP POSTGRES CONNECTION ---
conn = psycopg2.connect(
    host="localhost",
    database="Hospital Mgmt",
    user="postgres",
    password="300812"
)

def get_database_schema():
    query = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        print("\n📋 Database Schema (Table | Column | Data Type):")
        current_table = ""
        for table_name, column_name, data_type in rows:
            if table_name != current_table:
                print(f"\n🟣 Table: {table_name}")
                current_table = table_name
            print(f"   - {column_name} ({data_type})")

def main():
    get_database_schema()
    conn.close()
    print("\n🔒 Connection closed.")

if __name__ == "__main__":
    main()
