# Flask & MongoDB Atlas Submission App

A modern, responsive Flask web application that accepts user form submissions and saves them directly to a **MongoDB Atlas** cluster. It includes input validation, connection error handling (with specific guidance for Atlas IP whitelist restrictions), a sample JSON API endpoint, and an automated test suite.

---

## 🚀 Features

- **Interactive Form Submission**: Collects Name, Email, Category, and Message with full client and server validation.
- **MongoDB Atlas Integration**: Automatically sanitizes connection strings and inserts form submissions with ISO timestamps.
- **Robust Error Handling**: Captures missing fields, authentication failures, and MongoDB Atlas IP whitelist restrictions, rendering clear context to the user.
- **REST API Endpoint (`/api`)**: Serves structured data from `data.json`.
- **Automated Test Suite**: Unit and integration tests covering routes, validation, and database mocking without requiring live database credentials.

---

## 📁 Project Structure

```
Mongodb-app/
├── app.py              # Main Flask application logic & MongoDB client setup
├── test_app.py         # Automated test suite (Flask test client & mocks)
├── data.json           # Local JSON dataset served by /api
├── requirements.txt    # Python dependencies
├── static/
│   └── style.css       # Application styling and layout rules
└── templates/
    ├── index.html      # Submission form & dynamic error alert page
    └── success.html    # Submission confirmation page
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.9+ installed on your machine.
- A MongoDB Atlas account and cluster (or local MongoDB instance).

### 2. Clone / Navigate to the Directory
```bash
cd d:\Mongodb-app
```

### 3. Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory (same folder as `app.py`) to store your database credentials securely:

```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.oysibhp.mongodb.net/
DB_NAME=app_db
COLLECTION_NAME=submissions
```

> **Note**: If `MONGO_URI` is not provided in `.env`, the application will use the fallback connection string configured in `app.py`.

---

## 🏃 Running the Application

Start the Flask development server:

```bash
python app.py
```

Open your browser and navigate to:
- **Web Form**: `http://127.0.0.1:5000/`
- **JSON API**: `http://127.0.0.1:5000/api`

---

## 🧪 Running the Tests

Execute the automated test suite to verify routes, validation rules, and error handling:

```bash
python test_app.py
```

or with `pytest`:

```bash
pytest test_app.py
```

---

## ⚠️ Troubleshooting & Common Issues

### 1. MongoDB Atlas IP Whitelist Restriction (`ServerSelectionTimeoutError`)
If you see an error stating `Could not connect to MongoDB Atlas due to IP Whitelist restriction`:
1. Log in to [MongoDB Atlas](https://cloud.mongodb.com/).
2. Navigate to **Security** -> **Network Access**.
3. Click **+ Add IP Address**.
4. Select **Add Current IP Address** or **Allow Access from Anywhere** (`0.0.0.0/0`).
5. Click **Confirm** and wait 1–2 minutes for the rule to become active.

### 2. Placeholder Password Error
If you receive a `ValueError` indicating `<db_password>` is present, update your connection string in `.env` with your actual Atlas database user password.
