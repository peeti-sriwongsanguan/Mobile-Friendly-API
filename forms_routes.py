#forms_routes.py
from flask import Blueprint, request, jsonify
import sqlite3
import os

# Import from database module instead of app
from database import DB_PATH

# Create a Blueprint for forms routes
forms_bp = Blueprint('forms', __name__)


@forms_bp.route('/forms', methods=['GET'])
def get_forms():
    """Endpoint to retrieve all forms"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM forms ORDER BY created_at DESC')
    forms = [dict(row) for row in cursor.fetchall()]

    # For each form, get its items
    for form in forms:
        cursor.execute('SELECT * FROM form_items WHERE form_id = ? ORDER BY item_number', (form['id'],))
        form['items'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify({"forms": forms})


@forms_bp.route('/forms/<int:form_id>', methods=['GET'])
def get_form(form_id):
    """Endpoint to retrieve a specific form by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM forms WHERE id = ?', (form_id,))
    form = cursor.fetchone()

    if form is None:
        conn.close()
        return jsonify({"error": "Form not found"}), 404

    form_dict = dict(form)

    # Get form items
    cursor.execute('SELECT * FROM form_items WHERE form_id = ? ORDER BY item_number', (form_id,))
    form_dict['items'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify(form_dict)


@forms_bp.route('/forms', methods=['POST'])
def add_form():
    """Endpoint to add a new form with items"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Validate required fields
    if 'requester_name' not in data:
        return jsonify({"error": "Requester name is required"}), 400

    # Connect to database and insert data
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Insert form header
        cursor.execute(
            'INSERT INTO forms (vehicle_registration, date, requester_name, recipient_name) VALUES (?, ?, ?, ?)',
            (
                data.get('vehicle_registration', ''),
                data.get('date', ''),
                data['requester_name'],
                data.get('recipient_name', '')
            )
        )

        form_id = cursor.lastrowid

        # Insert form items if present
        if 'items' in data and isinstance(data['items'], list):
            for i, item in enumerate(data['items']):
                if not item.get('material_description'):
                    continue  # Skip empty items

                cursor.execute(
                    '''INSERT INTO form_items 
                       (form_id, item_number, material_description, material_code, quantity, unit) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (
                        form_id,
                        item.get('item_number', i + 1),
                        item['material_description'],
                        item.get('material_code', ''),
                        int(item.get('quantity', 0)),
                        item.get('unit', '')
                    )
                )

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Form added successfully",
            "id": form_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@forms_bp.route('/forms/<int:form_id>', methods=['PUT'])
def update_form(form_id):
    """Endpoint to update an existing form"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if form exists
        cursor.execute('SELECT id FROM forms WHERE id = ?', (form_id,))
        if cursor.fetchone() is None:
            conn.close()
            return jsonify({"error": "Form not found"}), 404

        # Update form header
        cursor.execute(
            '''UPDATE forms SET 
               vehicle_registration = ?, 
               date = ?, 
               requester_name = ?, 
               recipient_name = ? 
               WHERE id = ?''',
            (
                data.get('vehicle_registration', ''),
                data.get('date', ''),
                data.get('requester_name', ''),
                data.get('recipient_name', ''),
                form_id
            )
        )

        # Handle form items if present
        if 'items' in data and isinstance(data['items'], list):
            # Delete existing items
            cursor.execute('DELETE FROM form_items WHERE form_id = ?', (form_id,))

            # Insert new items
            for i, item in enumerate(data['items']):
                if not item.get('material_description'):
                    continue  # Skip empty items

                cursor.execute(
                    '''INSERT INTO form_items 
                       (form_id, item_number, material_description, material_code, quantity, unit) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (
                        form_id,
                        item.get('item_number', i + 1),
                        item['material_description'],
                        item.get('material_code', ''),
                        item.get('quantity', 0),
                        item.get('unit', '')
                    )
                )

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Form updated successfully",
            "id": form_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@forms_bp.route('/forms/<int:form_id>', methods=['DELETE'])
def delete_form(form_id):
    """Endpoint to delete a form and its items"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if form exists
    cursor.execute('SELECT id FROM forms WHERE id = ?', (form_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "Form not found"}), 404

    # Delete form items first (foreign key cascade should handle this, but to be safe)
    cursor.execute('DELETE FROM form_items WHERE form_id = ?', (form_id,))

    # Delete form
    cursor.execute('DELETE FROM forms WHERE id = ?', (form_id,))
    conn.commit()

    conn.close()
    return jsonify({"message": "Form deleted successfully"})