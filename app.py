#app.py
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Import from database module
from database import DB_PATH, init_db

# Import routes blueprint
from forms_routes import forms_bp

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Initialize database on startup
init_db()

# Register blueprints
app.register_blueprint(forms_bp)

@app.route('/', methods=['GET'])
def index():
    """Root endpoint that provides API information"""
    return jsonify({
        "name": "Mobile-Friendly API",
        "version": "1.0",
        "endpoints": [
            {"path": "/", "methods": ["GET"], "description": "This information page"},
            {"path": "/ui", "methods": ["GET"], "description": "Web interface for material forms"},
            {"path": "/items", "methods": ["GET", "POST"], "description": "Get all items or create a new item"},
            {"path": "/items/<id>", "methods": ["GET", "DELETE"], "description": "Get or delete a specific item"},
            {"path": "/forms", "methods": ["GET", "POST"], "description": "Get all forms or create a new form"},
            {"path": "/forms/<id>", "methods": ["GET", "PUT", "DELETE"], "description": "Get, update or delete a specific form"}
        ]
    })

@app.route('/ui', methods=['GET'])
def ui():
    """Serve the HTML UI for forms"""
    # Print the current working directory and check if the file exists
    print(f"Current directory: {os.getcwd()}")
    print(f"Static folder exists: {os.path.exists('static')}")
    print(f"Index file exists: {os.path.exists('static/index.html')}")
    return send_from_directory('static', 'index.html')

@app.route('/items', methods=['GET'])
def get_items():
    """Endpoint to retrieve all items from the database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM items ORDER BY created_at DESC')
    items = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify({"items": items})

@app.route('/items', methods=['POST'])
def add_item():
    """Endpoint to add a new item to the database"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Validate required fields
    if 'title' not in data:
        return jsonify({"error": "Title is required"}), 400

    # Connect to database and insert data
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO items (title, description) VALUES (?, ?)',
            (data['title'], data.get('description', ''))
        )

        conn.commit()
        item_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "message": "Item added successfully",
            "id": item_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Endpoint to retrieve a specific item by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = cursor.fetchone()

    conn.close()

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(dict(item))

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Endpoint to delete a specific item by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Item not found"}), 404

    conn.close()
    return jsonify({"message": "Item deleted successfully"})


if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5007))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'

    # Use host='0.0.0.0' to make the app accessible from other devices on the network
    # For production, you should use a proper WSGI server like Gunicorn
    app.run(host=host, port=port, debug=debug)