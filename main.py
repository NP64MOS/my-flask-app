from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # อนุญาต CORS สำหรับ React

DB_NAME = "daily_journal.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/journals', methods=['GET'])
def get_journals():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title, content, date FROM journal ORDER BY date DESC, id DESC")
    rows = c.fetchall()
    journals = [{"id": r[0], "title": r[1], "content": r[2], "date": r[3]} for r in rows]
    conn.close()
    return jsonify(journals)

@app.route('/api/journals/<int:id>', methods=['GET'])
def get_journal(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title, content, date FROM journal WHERE id = ?", (id,))
    row = c.fetchone()
    conn.close()
    if row:
        journal = {"id": row[0], "title": row[1], "content": row[2], "date": row[3]}
        return jsonify(journal)
    return jsonify({"error": "Not found"}), 404

@app.route('/api/journals', methods=['POST'])
def add_journal():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    date = data.get('date')

    if not title or not content or not date:
        return jsonify({"error": "Missing fields"}), 400

    try:
        # ตรวจสอบรูปแบบวันที่ YYYY-MM-DD
        datetime.strptime(date, '%Y-%m-%d')
    except:
        return jsonify({"error": "Invalid date format, should be YYYY-MM-DD"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO journal (title, content, date) VALUES (?, ?, ?)", (title, content, date))
    conn.commit()
    new_id = c.lastrowid
    conn.close()

    return jsonify({"id": new_id, "message": "Journal added successfully"}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True)