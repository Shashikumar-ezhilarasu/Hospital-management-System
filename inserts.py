import psycopg2
from datetime import datetime, timedelta

# DB connection
conn = psycopg2.connect(
    host="localhost",
    database="testing",
    user="postgres",
    password="300812"
)
cur = conn.cursor()

# DROP tables if exist (for rerun convenience)
cur.execute("""
DROP TABLE IF EXISTS patient_app_appointment;
DROP TABLE IF EXISTS patient_app_patient_details;
DROP TABLE IF EXISTS inventory_app_druginventory;
DROP TABLE IF EXISTS inpatient_app_procedure;
DROP TABLE IF EXISTS inpatient_app_inpatient;
DROP TABLE IF EXISTS patient_app_billreports;
""")

# CREATE tables
cur.execute("""
CREATE TABLE patient_app_patient_details (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(15),
    referred_by VARCHAR(100),
    city VARCHAR(100),
    district VARCHAR(100),
    locality_name VARCHAR(100),
    created_date DATE
);
""")

cur.execute("""
CREATE TABLE patient_app_appointment (
    id SERIAL PRIMARY KEY,
    patient_id_id INT REFERENCES patient_app_patient_details(id),
    date DATE,
    time TIME,
    doctor_id_id INT,
    doctor_name VARCHAR(100),
    session VARCHAR(50),
    service_type VARCHAR(100)
);
""")

cur.execute("""
CREATE TABLE inventory_app_druginventory (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    quantity INT,
    expiry_date DATE,
    reorder_level INT
);
""")

cur.execute("""
CREATE TABLE inpatient_app_procedure (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    outcome VARCHAR(50),
    procedure_date DATE
);
""")

cur.execute("""
CREATE TABLE inpatient_app_inpatient (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patient_app_patient_details(id),
    procedure_id INT REFERENCES inpatient_app_procedure(id),
    admission_date DATE,
    status VARCHAR(50)
);
""")

cur.execute("""
CREATE TABLE patient_app_billreports (
    id SERIAL PRIMARY KEY,
    patient_id_id INT REFERENCES patient_app_patient_details(id),
    service_type VARCHAR(100),
    bill_price NUMERIC
);
""")

conn.commit()

# INSERT MOCK DATA

# --- Patients
patients = [
    ("Priya", "Sharma", "9876543210", "Dr. Mehta", "Chennai", "TN", "Adyar", "2024-11-10"),
    ("Rahul", "Verma", "9123456789", "Google Ads", "Bangalore", "KA", "Indiranagar", "2024-12-15"),
    ("Sneha", "Iyer", "9988776655", "Existing Patient", "Mumbai", "MH", "Andheri", "2025-01-05"),
    ("Anil", "Kumar", "9876543211", "Facebook", "Hyderabad", "TG", "Banjara Hills", "2025-01-15"),
    ("Geeta", "Menon", "9345678923", "Walk-In", "Chennai", "TN", "Velachery", "2025-02-01"),
]
for p in patients:
    cur.execute("""
    INSERT INTO patient_app_patient_details (first_name, last_name, phone, referred_by, city, district, locality_name, created_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, p)

# --- Appointments
appointments = [
    (1, "2025-07-03", "10:00", 101, "Dr. Mehta", "Morning", "Consultation"),
    (2, "2025-07-03", "11:30", 102, "Dr. Reddy", "Morning", "Scan"),
    (3, "2025-07-03", "17:00", 101, "Dr. Mehta", "Evening", "IUI"),
]
for a in appointments:
    cur.execute("""
    INSERT INTO patient_app_appointment (patient_id_id, date, time, doctor_id_id, doctor_name, session, service_type)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, a)

# --- Medicines
meds = [
    ("Paracetamol", 100, datetime.today() + timedelta(days=25), 50),
    ("Ibuprofen", 20, datetime.today() + timedelta(days=60), 30),
    ("Folic Acid", 5, datetime.today() + timedelta(days=10), 10),
]
for m in meds:
    cur.execute("""
    INSERT INTO inventory_app_druginventory (name, quantity, expiry_date, reorder_level)
    VALUES (%s, %s, %s, %s)
    """, m)

# --- Procedures
procedures = [
    ("IUI", "success", "2025-06-10"),
    ("IVF", "failure", "2025-06-12"),
    ("OI", None, "2025-06-18"),
]
for proc in procedures:
    cur.execute("""
    INSERT INTO inpatient_app_procedure (name, outcome, procedure_date)
    VALUES (%s, %s, %s)
    """, proc)

# --- Inpatients
inpatients = [
    (1, 1, "2025-06-10", "success"),
    (2, 2, "2025-06-12", "failure"),
    (3, 3, "2025-06-18", None),
]
for ip in inpatients:
    cur.execute("""
    INSERT INTO inpatient_app_inpatient (patient_id, procedure_id, admission_date, status)
    VALUES (%s, %s, %s, %s)
    """, ip)

# --- Billing
bills = [
    (1, "Consultation", 500),
    (2, "Scan", 1200),
    (3, "IUI", 3500),
    (3, "Pharmacy", 300),
]
for b in bills:
    cur.execute("""
    INSERT INTO patient_app_billreports (patient_id_id, service_type, bill_price)
    VALUES (%s, %s, %s)
    """, b)

conn.commit()
cur.close()
conn.close()
print("✅ Mock hospital data inserted successfully.")
