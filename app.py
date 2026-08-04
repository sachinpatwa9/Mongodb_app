import json
import os
from datetime import datetime, timezone
from urllib.parse import quote_plus, unquote
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, redirect, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

load_dotenv()

app = Flask(__name__)

# Configuration
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')
DEFAULT_MONGO_URI = 'mongodb+srv://<username>:<password>@cluster0.mongodb.net/test?retryWrites=true&w=majority'
MONGO_URI = os.getenv('MONGODB_URI') or os.getenv('MONGO_URI') or DEFAULT_MONGO_URI
DB_NAME = os.getenv('DB_NAME', 'app_db')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'submissions')

def sanitize_mongo_uri(uri: str) -> str:
    if not uri:
        return uri
    if '://' in uri and '@' in uri:
        scheme, rest = uri.split('://', 1)
        last_at = rest.rfind('@')
        if last_at != -1 and ':' in rest[:last_at]:
            userinfo = rest[:last_at]
            host_and_beyond = rest[last_at + 1:]
            user, password = userinfo.split(':', 1)
            password_quoted = quote_plus(unquote(password))
            user_quoted = quote_plus(unquote(user))
            return f"{scheme}://{user_quoted}:{password_quoted}@{host_and_beyond}"
    return uri

def get_db_collection():
    uri = MONGO_URI or os.getenv('MONGODB_URI') or os.getenv('MONGO_URI')
    if not uri:
        raise ValueError("MongoDB URI is not configured. Please set MONGO_URI in environment variables.")
    if '<db_password>' in uri or '<password>' in uri:
        raise ValueError("MongoDB URI still contains a placeholder password. Replace <db_password> with your real Atlas password before submitting.")
    
    clean_uri = sanitize_mongo_uri(uri)
    client = MongoClient(clean_uri, serverSelectionTimeoutMS=4000)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    category = request.form.get('category', '').strip()
    message = request.form.get('message', '').strip()

    form_data = {
        'name': name,
        'email': email,
        'category': category,
        'message': message
    }

    # Basic Validation
    if not name or not email or not message:
        return render_template('index.html', error="Please fill in all required fields (Name, Email, Message).", form_data=form_data), 400

    document = {
        'name': name,
        'email': email,
        'category': category,
        'message': message,
        'created_at': datetime.now(timezone.utc)
    }

    try:
        collection = get_db_collection()
        collection.insert_one(document)
        return redirect(url_for('success'))
    except (ValueError, ServerSelectionTimeoutError, PyMongoError) as e:
        error_msg = str(e)
        if isinstance(e, ServerSelectionTimeoutError):
            if 'TLSV1_ALERT_INTERNAL_ERROR' in error_msg or 'SSL handshake failed' in error_msg:
                error_msg = "Could not connect to MongoDB Atlas due to IP Whitelist restriction. Please add your IP address (or 0.0.0.0/0) in MongoDB Atlas under 'Security' -> 'Network Access'."
            else:
                error_msg = "Could not connect to MongoDB Atlas. Please verify your connection URI and network/IP access."
        elif isinstance(e, ValueError):
            error_msg = str(e)
        elif 'bad auth' in str(e).lower() or 'authentication failed' in str(e).lower() or '8000' in str(e):
            error_msg = "MongoDB authentication failed. Please verify the username and password in the Atlas connection string."
        return render_template('index.html', error=error_msg, form_data=form_data), 500
    except Exception as e:
        return render_template('index.html', error=f"An unexpected error occurred: {str(e)}", form_data=form_data), 500

@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html')

@app.route('/api', methods=['GET'])
def get_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON data"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)