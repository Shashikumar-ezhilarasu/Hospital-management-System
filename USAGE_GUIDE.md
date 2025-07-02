# Hospital Management System - Natural Language Query Interface

## 🚀 Quick Start

### Method 1: Use the Startup Script (Recommended)

```bash
python3 start_system.py
```

This will automatically start both the Flask server and CLI interface.

### Method 2: Manual Start

1. Start Flask server in one terminal:

```bash
python3 new.py
```

2. Start CLI in another terminal:

```bash
python3 query_cli.py
```

## 📋 Supported Operations

### 🔥 PRIORITY 1 - Daily Operations

- **Daily appointment list**: "Daily appointment list for today"
- **Doctor-specific appointments**: "Show appointments for doctor Shyam"
- **Appointment count**: "How many appointments are there for doctor Shyam"
- **Revenue analysis**: "Total revenue by service type"
- **Revenue breakdown**: "Revenue collected from consultations and scans"

### ⚡ PRIORITY 2 - Patient Management

- **Pregnancy follow-up**: "Patients needing pregnancy result follow-up"
- **Procedure tracking**: "Monthly list of IUI procedures"
- **Success rates**: "Success rate for IVF procedures"
- **Add appointments**: "Add appointment for doctor Shyam tomorrow 10 AM"

### 📊 PRIORITY 3 - Analytics & Inventory

- **Patient trends**: "Month-over-month trend of new patient registrations"
- **Geographic analysis**: "Geographic distribution of patients by city"
- **Referral analysis**: "Patient breakdown by referral source"
- **Expiry tracking**: "Medicines expiring in next 30 days"
- **Stock levels**: "Medicines below reorder level"

## 💡 Usage Tips

### Natural Language Examples

```
✅ Good queries:
- "How many appointments are there for doctor Shyam?"
- "Medicines expiring in next 30 days"
- "Daily appointment list"
- "Add appointment for doctor John tomorrow at 10 AM"
- "Total revenue from consultations"

❌ Avoid overly complex sentences:
- "I want to know about the appointments that are scheduled for doctor Shyam in the coming days and also want to see the revenue"
```

### Available Commands

- `help` or `h` - Show detailed help
- `quit` or `exit` - Exit the program
- `Ctrl+C` - Force exit

## 🔧 System Requirements

- Python 3.7+
- PostgreSQL database running
- Required packages (automatically installed):
  - flask
  - flask-cors
  - psycopg2-binary
  - google-generativeai
  - python-dotenv
  - colorama
  - requests

## 📁 File Structure

```
/
├── new.py              # Flask API server
├── query_cli.py        # Command-line interface
├── start_system.py     # Startup script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🚨 Troubleshooting

### Common Issues:

1. **"Cannot connect to server"**

   - Make sure Flask server is running on port 5002
   - Run: `python3 new.py`

2. **"Port already in use"**

   - Kill existing processes: `pkill -f "python.*new.py"`
   - Or use different port in new.py

3. **Database connection errors**

   - Check PostgreSQL is running
   - Verify connection details in new.py

4. **No results found**
   - Your database might be empty
   - Try: "Show all tables" to verify connection

## 🎯 Example Session

```
🤔 Your question: How many appointments are there for doctor Shyam?

🔍 Generated SQL:
SELECT COUNT(*) FROM patient_app_appointment WHERE doctor_id_id IN
(SELECT id FROM user_app_user WHERE first_name || ' ' || last_name ILIKE '%shyam%')

📊 Results:
count
-----
5

🤔 Your question: Medicines expiring in next 30 days

🔍 Generated SQL:
SELECT name, quantity, expiry_date FROM inventory_app_druginventory
WHERE expiry_date <= CURRENT_DATE + INTERVAL '30 days'

📊 Results:
name           | quantity       | expiry_date
---------------|----------------|-------------
Paracetamol    | 50            | 2025-07-15
Insulin        | 20            | 2025-07-20
```

## 🛠️ Advanced Usage

### Custom Queries

The system understands context, so you can ask complex questions:

- "Which doctors have the most appointments this month?"
- "Patients who haven't paid their bills"
- "Medicines that need to be reordered urgently"

### Adding Records

- "Add appointment for doctor Smith on July 5th at 2 PM"
- "Create new patient record for John Doe"
- "Add medicine inventory for Aspirin"

---

**Need help?** Type `help` in the CLI or contact system administrator.
