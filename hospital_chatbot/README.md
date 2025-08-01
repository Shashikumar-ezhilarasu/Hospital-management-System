# 🏥 Hospital Management Django Chatbot

A Django-based web interface for natural language database queries using Google's Gemini AI.

## 🚀 Setup & Installation

### 1. Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv django_env

# Activate virtual environment
source django_env/bin/activate  # On macOS/Linux
# or
django_env\Scripts\activate     # On Windows
```

### 2. Install Dependencies
```bash
pip install django psycopg2-binary google-generativeai python-dotenv
```

### 3. Environment Configuration
Create a `.env` file in the project root:
```env
# Database Configuration
DB_HOST=localhost
DB_NAME=testing2
DB_USER=postgres
DB_PASSWORD=pass

# Google API Key
GOOGLE_API_KEY=your_actual_api_key_here
```

### 4. Run the Application
```bash
# Navigate to project directory
cd hospital_chatbot

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### 5. Access the Application
Open your browser and go to: `http://127.0.0.1:8000`

## 🎯 Features

### ✨ Web Interface
- **Modern Design**: Beautiful, responsive single-page application
- **Real-time Chat**: Interactive chat interface with the AI
- **SQL Display**: Shows generated SQL queries for transparency
- **Results Table**: Formatted table display for query results
- **Example Queries**: Click-to-use example queries
- **Connection Status**: Live database connection indicator

### 🧠 AI Capabilities
- **Natural Language Processing**: Convert plain English to SQL
- **Schema Awareness**: Automatically understands your database structure
- **Query Optimization**: Adds LIMIT clauses and proper formatting
- **Error Handling**: Clear error messages and suggestions

### 🔒 Security Features
- **CSRF Protection**: Django's built-in CSRF protection
- **SQL Injection Prevention**: Parameterized queries
- **Error Containment**: Proper exception handling
- **Connection Management**: Automatic connection cleanup

## 💬 Example Queries

### Patient Management
- "Show all patients"
- "List patients from New York"
- "Find patients over age 65"
- "Count total patients"

### Doctor Information
- "List all doctors"
- "Show doctors in cardiology department"
- "Find Dr. Smith's information"

### Appointments
- "Show today's appointments"
- "List upcoming appointments"
- "Count appointments by doctor"

### Analytics
- "Patient count by gender"
- "Average patient age"
- "Monthly registration trends"

## 🏗️ Project Structure

```
hospital_chatbot/
├── hospital_chatbot/          # Django project settings
│   ├── settings.py           # Main configuration
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── chatbot/                  # Django app
│   ├── views.py             # Backend logic
│   ├── urls.py              # App URLs
│   └── templates/           # HTML templates
│       └── chatbot/
│           └── index.html   # Main interface
├── manage.py                # Django management script
└── .env                     # Environment variables
```

## 🔧 API Endpoints

### Main Chat Endpoint
- **URL**: `/chat/`
- **Method**: POST
- **Content-Type**: application/json
- **Request**: `{"query": "your natural language question"}`
- **Response**: 
```json
{
  "user_query": "show all patients",
  "generated_sql": "SELECT * FROM patients LIMIT 100;",
  "result": {
    "success": true,
    "type": "select",
    "columns": ["id", "name", "age"],
    "data": [...],
    "row_count": 25
  }
}
```

### Connection Test
- **URL**: `/test-connection/`
- **Method**: GET
- **Response**: `{"status": "connected", "message": "Database connection successful"}`

## 🛠️ Customization

### Database Configuration
Update the `.env` file with your database credentials:
```env
DB_HOST=your_host
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

### Styling
The CSS is embedded in `templates/chatbot/index.html`. You can:
- Modify colors and themes
- Adjust responsive breakpoints
- Customize animations and transitions

### AI Prompts
Edit the `generate_sql()` function in `views.py` to:
- Modify AI instructions
- Add domain-specific rules
- Enhance query generation logic

## 🚀 Production Deployment

### 1. Environment Setup
```bash
# Set DEBUG to False in settings.py
DEBUG = False

# Add your domain to ALLOWED_HOSTS
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

### 2. Static Files
```bash
python manage.py collectstatic
```

### 3. Database Migration
```bash
python manage.py migrate
```

### 4. Web Server
Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn hospital_chatbot.wsgi:application
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database credentials in `.env`
   - Ensure PostgreSQL is running
   - Verify database exists

2. **Gemini API Errors**
   - Check API key in `.env`
   - Verify API quota limits
   - Check internet connection

3. **Module Import Errors**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **Template Not Found**
   - Check `INSTALLED_APPS` includes `'chatbot'`
   - Verify template directory structure

### Debug Mode
Enable detailed error messages by setting `DEBUG = True` in `settings.py`.

## 📊 Performance Tips

1. **Database Optimization**
   - Add indexes to frequently queried columns
   - Use connection pooling for high traffic
   - Monitor query performance

2. **Caching**
   - Cache database schema to reduce load
   - Use Redis for session storage
   - Implement query result caching

3. **Rate Limiting**
   - Implement rate limiting for API calls
   - Add user authentication
   - Monitor Gemini API usage

## 🔐 Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Database Access**: Use read-only database users when possible
3. **Input Validation**: Implement additional query validation
4. **HTTPS**: Use HTTPS in production
5. **Monitoring**: Log and monitor all database queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and development purposes.

---

**Happy Querying! 🎉**
