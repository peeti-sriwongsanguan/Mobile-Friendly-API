#part_database.py
import sqlite3
import os

# Dictionary of automotive parts with Thai and English translations
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


def setup_parts_database(db_path='auto_parts.db'):
    """Create a database with parts information"""
    # Check if database already exists
    if os.path.exists(db_path):
        print(f"Database '{db_path}' already exists.")
        return

    # Connect to database (this will create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thai_name TEXT NOT NULL,
        english_name TEXT NOT NULL,
        part_code TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Insert parts data
    for thai_name, english_name in AUTOMOTIVE_PARTS_DICT.items():
        # Generate a simple part code (first 3 letters of English name + sequential number)
        part_code = english_name[:3].upper() + str(len(english_name))

        cursor.execute(
            'INSERT INTO parts (thai_name, english_name, part_code) VALUES (?, ?, ?)',
            (thai_name, english_name, part_code)
        )

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"Database '{db_path}' created successfully with {len(AUTOMOTIVE_PARTS_DICT)} parts.")


def get_all_parts(db_path='auto_parts.db'):
    """Get all parts from the database"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM parts ORDER BY thai_name')
    parts = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return parts


def search_parts(search_term, db_path='auto_parts.db'):
    """Search for parts matching the search term in Thai or English"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Use LIKE for partial matching in both Thai and English names
    cursor.execute(
        'SELECT * FROM parts WHERE thai_name LIKE ? OR english_name LIKE ? ORDER BY thai_name',
        (f'%{search_term}%', f'%{search_term}%')
    )
    parts = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return parts


# Run this script directly to create the database
if __name__ == "__main__":
    setup_parts_database()
    print("Parts database setup complete.")