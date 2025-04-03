#parts_routes.py
from flask import Blueprint, jsonify, request
import sqlite3
from database import DB_PATH

# Create a Blueprint for parts routes
parts_bp = Blueprint('parts', __name__)

# Dictionary of automotive parts (used as a fallback if database is not available)
AUTOMOTIVE_PARTS_DICT = {
    "ขากระจก": "Mirror Bracket",
    "ไฟหน้า": "Headlight",
    "ประตู": "Door",
    "กระจก": "Window/Glass",
    "ไฟท้าย": "Tail Light",
    "กระจังหน้า": "Front Grille",
    "กันชนหน้า": "Front Bumper",
    "ไฟเลี้ยว": "Turn Signal",
    "เบ้ามือโด": "Door Handle Housing",
    "ที่ปัดน้ำฝน": "Windshield Wiper",
    "แก้มไฟหรือหน้า": "Light Panel or Front Cover",
    "พลาสติกบังฝุ่นหลัง": "Rear Dust Cover (Plastic)",
    "พลาสติกมุมกันชน": "Bumper Corner Plastic",
    "พลาสติกปิดมุมกันชน": "Bumper Corner Cover",
    "ไฟในกันชน": "Bumper Light",
    "พลาสติกปิดกันชน": "Bumper Cover",
    "กระป๋องดีดน้ำ": "Washer Fluid Container",
    "แป้นจ่ายเบรคตรัซ": "Brake/Clutch Pedal",
    "มือจับแยงหน้า": "Front Handle",
    "กันสาดประตู": "Door Visor/Rain Guard",
    "ซองไฟหน้า": "Headlight Housing",
    "พลาสติกบนไฟเลี้ยว": "Plastic Above Turn Signal",
    "เพ้องยกกระจกประตู": "Window Lifter Cover",
    "สักหลาดกระจกประตู": "Door Window Felt/Seal",
    "ขากันชน": "Bumper Bracket",
    "ยางกระจกหน้า": "Front Windshield Rubber",
    "แผงหน้ากระจัง": "Front Grille Panel",
    "แผ่นรองแผงหน้า": "Front Panel Support Plate",
    "โล่ไก่": "Radiator Shield",
    "ไฟเลี้ยวข้างประตู": "Door Side Turn Signal",
    "ไฟหลังคา": "Roof Light",
    "มือเปิดประตู": "Door Handle",
    "บังโคลนหน้า": "Front Fender",
    "ไฟป้ายทะเบียน": "License Plate Light",
    "ยางรอบกระจก": "Window Rubber Seal"
}


@parts_bp.route('/parts', methods=['GET'])
def get_parts():
    """Endpoint to retrieve all parts or search for parts"""
    search_term = request.args.get('search', '')

    try:
        conn = sqlite3.connect('auto_parts.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if search_term:
            # Search for parts
            cursor.execute(
                'SELECT * FROM parts WHERE thai_name LIKE ? OR english_name LIKE ? ORDER BY thai_name',
                (f'%{search_term}%', f'%{search_term}%')
            )
        else:
            # Get all parts
            cursor.execute('SELECT * FROM parts ORDER BY thai_name')

        parts = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({"parts": parts})

    except Exception as e:
        # Fallback to using the dictionary if database access fails
        if search_term:
            filtered_parts = []
            for thai, english in AUTOMOTIVE_PARTS_DICT.items():
                if search_term.lower() in thai.lower() or search_term.lower() in english.lower():
                    filtered_parts.append({
                        "thai_name": thai,
                        "english_name": english,
                        "part_code": english[:3].upper() + str(len(english))
                    })
            return jsonify({"parts": filtered_parts})
        else:
            parts_list = []
            for thai, english in AUTOMOTIVE_PARTS_DICT.items():
                parts_list.append({
                    "thai_name": thai,
                    "english_name": english,
                    "part_code": english[:3].upper() + str(len(english))
                })
            return jsonify({"parts": parts_list})


@parts_bp.route('/parts/setup', methods=['GET'])
def setup_parts_db():
    """Endpoint to set up the parts database"""
    try:
        import parts_database
        parts_database.setup_parts_database()
        return jsonify({"message": "Parts database set up successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500