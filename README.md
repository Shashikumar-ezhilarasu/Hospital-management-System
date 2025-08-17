

A full-stack Django web application that enables natural language querying of your hospital database using AI (Google Gemini) and displays results in a modern, responsive chat interface.

https://github.com/user-attachments/assets/c9bacf88-6606-42e8-8648-83b68019edbb



---

##  Features

### 1. **Natural Language Querying**
- Ask questions in plain English (e.g., "Show all patients", "List appointments for today")
- AI-powered SQL generation using Google Gemini
- Handles complex queries and medical terminology

### 2. **Database Integration**
- Connects to PostgreSQL hospital database
- Supports tables like patient details, doctors, appointments, inventory, and more
- Real-time data fetching and display

### 3. **Full-Stack Web Application**
- Built with Django 5.2.4 (Python 3.12)
- RESTful API endpoints for chat and connection testing
- Secure environment variable management (.env)

### 4. **Modern Chat Interface**
- Responsive, full-screen design (desktop & mobile)
- Auto-scrolling chat history with custom scrollbar
- Example queries for quick start
- Real-time feedback and loading indicators
- Error handling with user-friendly messages

### 5. **User Experience Enhancements**
- Example queries auto-minimize when user starts typing
- Connection status indicator (database health)
- Table formatting for query results
- Pagination for large result sets

### 6. **Security & Reliability**
- CSRF protection (Django default)
- Input validation and error handling
- Secure credential storage via .env

### 7. **Easy Deployment & Development**
- Simple setup with requirements.txt
- Virtual environment support
- GitHub integration for version control

---

## 📁 Project Structure

```
/Users/shashikumarezhil/Documents/JOB/
├── hospital_chatbot/          # Main Django web application
│   ├── .env                  # Environment variables
│   ├── manage.py             # Django management utility
│   ├── hospital_chatbot/     # Project config (settings, urls, wsgi)
│   └── chatbot/              # Main app (views, urls, models, templates)
│       └── templates/chatbot/index.html # Chatbot UI
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── ...                       # Other utility files
```

---

## 📝 How to Use

1. Clone the repository
2. Set up your Python virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Configure your `.env` file with database and API credentials
5. Run the Django server: `python manage.py runserver`
6. Access the chatbot at `http://127.0.0.1:8001/`

---

## Example Queries
- Show all patients
- List all doctors
- Show appointments for today
- Count total patients
- Show medicines in inventory

---

##  Tech Stack
- Django
- PostgreSQL
- Google Gemini AI
- HTML/CSS/JavaScript
- Python

---

## License
MIT
