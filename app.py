import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    # Updated table to include 'date'
    cursor.execute('''CREATE TABLE IF NOT EXISTS shifts 
                      (id INTEGER PRIMARY KEY, user TEXT, date TEXT, clock_in TEXT, clock_out TEXT, total REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    fmt = '%H:%M'
    tdelta = datetime.strptime(data['out'], fmt) - datetime.strptime(data['in'], fmt)
    hours = round(tdelta.seconds / 3600, 2)
    
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO shifts (user, date, clock_in, clock_out, total) VALUES (?, ?, ?, ?, ?)", 
                   (data['name'], data['date'], data['in'], data['out'], hours))
    conn.commit()
    conn.close()
    return jsonify({"total_hours": hours})

@app.route('/boss')
def boss_dashboard():
    filter_type = request.args.get('filter', 'all')
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()

    if filter_type == 'month':
        # Filters for the current month
        month_start = datetime.now().strftime('%Y-%m-01')
        cursor.execute("SELECT * FROM shifts WHERE date >= ?", (month_start,))
    elif filter_type == 'week':
        # Filters for the last 7 days
        week_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute("SELECT * FROM shifts WHERE date >= ?", (week_start,))
    else:
        cursor.execute("SELECT * FROM shifts")

    all_shifts = cursor.fetchall()
    conn.close()
    return render_template('boss.html', shifts=all_shifts)