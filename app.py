import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# This creates the database file when the app starts
def init_db():
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS shifts 
                      (id INTEGER PRIMARY KEY, user TEXT, clock_in TEXT, clock_out TEXT, total REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    # Logic: Calculate hours
    fmt = '%H:%M'
    tdelta = datetime.strptime(data['out'], fmt) - datetime.strptime(data['in'], fmt)
    hours = round(tdelta.seconds / 3600, 2)
    
    # NEW: Save to Database
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO shifts (user, clock_in, clock_out, total) VALUES (?, ?, ?, ?)", 
                   ("Employee_1", data['in'], data['out'], hours))
    conn.commit()
    conn.close()
    
    return jsonify({"total_hours": hours})

# NEW: The Boss Dashboard
@app.route('/boss')
def boss_dashboard():
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shifts")
    all_shifts = cursor.fetchall()
    conn.close()
    return render_template('boss.html', shifts=all_shifts)