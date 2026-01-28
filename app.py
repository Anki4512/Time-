import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
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
    # Automatic Calculation Logic
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
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    
    # Calculate current week dates (Monday to Sunday)
    today = datetime.now()
    start_week = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
    end_week = (today + timedelta(days=6 - today.weekday())).strftime('%Y-%m-%d')

    cursor.execute("SELECT user, date, total FROM shifts WHERE date BETWEEN ? AND ?", (start_week, end_week))
    data = cursor.fetchall()
    
    report = {}
    employees = set()
    dates = [(today - timedelta(days=today.weekday() - i)).strftime('%Y-%m-%d') for i in range(7)]

    for user, date, total in data:
        employees.add(user)
        if user not in report: report[user] = {}
        report[user][date] = total

    conn.close()
    return render_template('boss.html', report=report, employees=sorted(list(employees)), dates=dates)