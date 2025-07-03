# Hospital Management System - Read-Only Query Interface

## Overview
This is a secure, read-only natural language interface for the Hospital Management System database. It allows users to query the database using plain English, which is converted to SQL using Google's Gemini AI.

## Key Features

### 🔒 Security First
- **Read-Only Operations**: Only SELECT queries are allowed
- **Query Validation**: Automatically blocks INSERT, UPDATE, DELETE, and DDL operations
- **SQL Injection Protection**: Uses parameterized queries and validation

### 🧠 AI-Powered
- **Natural Language Processing**: Converts plain English to SQL using Gemini AI
- **Context-Aware**: Understands hospital management terminology and relationships
- **Smart Joins**: Automatically creates proper table joins when needed

### 🎨 User-Friendly Interface
- **Colorized CLI**: Beautiful colored output using colorama
- **Table Formatting**: Results displayed in readable table format
- **Help System**: Built-in examples and query suggestions
- **Error Handling**: Clear error messages and guidance

## Files Created

### Core Components
1. **`read.py`** - Flask API server (port 5003)
   - Handles natural language queries
   - Connects to PostgreSQL database
   - Generates SQL using Gemini AI
   - Returns structured JSON responses

2. **`read_cli.py`** - Interactive CLI interface
   - Colorized terminal interface
   - Table formatting for results
   - Help system with examples
   - Error handling and user guidance

### Supporting Files
3. **`demo_read.py`** - Demonstration script
4. **`test_read.py`** - Test script for validation

## Usage Instructions

### 1. Start the Server
```bash
python read.py
```
The server will start on `http://127.0.0.1:5003`

### 2. Use the CLI Interface
In another terminal:
```bash
python read_cli.py
```

### 3. Or Use the API Directly
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "show all patients"}' \
  http://127.0.0.1:5003/api/read
```

## Example Queries

### Patient Information
- "Show all patients"
- "List patients from Chennai"
- "Find patients named John"
- "Show male patients over age 30"

### Doctor Information
- "List all doctors"
- "Show doctors in cardiology"
- "Find Dr. Smith"

### Appointments
- "Show today's appointments"
- "List appointments for Dr. Rajesh"
- "Show upcoming appointments"
- "Find appointments for patient John"

### Inventory
- "Show all medicines"
- "List medicines expiring soon"
- "Find Paracetamol in inventory"
- "Show medicines with low stock"

### Analytics
- "Count patients by gender"
- "Show patient distribution by city"
- "Count appointments by doctor"
- "Show revenue by service type"

## Database Schema Support

The system automatically loads the PostgreSQL schema and supports queries across all tables:

- `patient_app_patient_details` - Patient information
- `patient_app_appointment` - Appointments
- `user_app_user` - Users (doctors/staff)
- `inventory_app_druginventory` - Medicine inventory
- `patient_app_billreports` - Billing information
- `inpatient_app_procedure` - Medical procedures
- `patient_app_patientreports` - Patient reports

## API Endpoints

### POST /api/read
Main query endpoint that accepts natural language queries.

**Request:**
```json
{
  "query": "show all patients"
}
```

**Response:**
```json
{
  "query": "show all patients",
  "sql": "SELECT * FROM patient_app_patient_details LIMIT 100;",
  "result": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "phone": "1234567890"
    }
  ]
}
```

### GET /api/schema
Returns the database schema information.

### GET /api/health
Health check endpoint.

## Security Features

1. **Query Validation**: Only SELECT statements are allowed
2. **Keyword Blocking**: Dangerous keywords are automatically blocked
3. **Result Limiting**: Large result sets are automatically limited
4. **Input Sanitization**: All inputs are sanitized before processing

## Error Handling

- **Connection Errors**: Clear messages when server is not running
- **API Quota**: Handles Gemini API rate limits gracefully
- **Database Errors**: Proper error messages for SQL issues
- **Invalid Queries**: Helpful suggestions for malformed queries

## Benefits

1. **Safe Exploration**: Users can explore data without risk of modification
2. **Easy to Use**: No SQL knowledge required
3. **Comprehensive**: Supports complex queries and analytics
4. **Fast**: Direct database queries with minimal overhead
5. **Scalable**: Can handle multiple concurrent users

## Requirements

- Python 3.7+
- PostgreSQL database
- Google Gemini API key
- Required Python packages (see requirements.txt)

## Future Enhancements

- Query history and bookmarking
- Export results to CSV/Excel
- Scheduled queries and reports
- Dashboard visualization
- Multi-language support
- Voice input capability
