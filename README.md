# Hospital Management Dashboard

A modern web application for viewing hospital management insights and analytics.

## Features

- Daily appointment list (filterable by doctor)
- Total revenue by service type
- Follow-up required for pregnancy results
- Monthly list of IUI/OI/IVF procedures
- Success rate of IUI/OI/IVF procedures
- Month-over-month new patient registrations
- Geographic distribution (city, district, locality)
- Referral source breakdown
- Medicines expiring in next X days
- Medicines below reorder level

## Prerequisites

- Python 3.7+
- Node.js 14+
- PostgreSQL database

## Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the database connection in `app.py`:
```python
conn = psycopg2.connect(
    host="localhost",
    database="Hospital Mgmt",
    user="postgres",
    password="your_password"
)
```

4. Run the Flask backend:
```bash
python app.py
```

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd hospital-dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Usage

1. Open your browser and navigate to http://localhost:3000
2. Click on any of the insight cards to view detailed information
3. Use the filters provided in the dialog to customize your view
4. Data will be displayed in either table or chart format depending on the type of insight

## Technologies Used

- Backend:
  - Flask
  - PostgreSQL
  - psycopg2
  - Flask-CORS

- Frontend:
  - React
  - TypeScript
  - Material-UI
  - Recharts
  - Axios 