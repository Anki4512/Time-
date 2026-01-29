import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # Needed for sessions

# Simple user database for this example
USERS = {
    "boss": {"password": "admin123", "role": "boss"},
    "employee": {"password": "user123", "role": "employee"}
}

def init_db():
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS shifts 
                      (id INTEGER PRIMARY KEY, user TEXT, date TEXT, clock_in TEXT, clock_out TEXT, total REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['role'] = USERS[username]['role']
            return redirect(url_for('home'))
        return "Invalid credentials", 401
    return '''
        <form method="post">
            <input name="username" placeholder="Username"><br>
            <input name="password" type="password" placeholder="Password"><br>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('login'))
    if session['role'] == 'boss': return redirect(url_for('boss_dashboard'))
    return render_template('index.html', user=session['user'])

@app.route('/calculate', methods=['POST'])
def calculate():
    if session.get('role') != 'employee': return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    fmt = '%H:%M'
    tdelta = datetime.strptime(data['out'], fmt) - datetime.strptime(data['in'], fmt)
    hours = round(tdelta.seconds / 3600, 2)
    
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO shifts (user, date, clock_in, clock_out, total) VALUES (?, ?, ?, ?, ?)", 
                   (session['user'], data['date'], data['in'], data['out'], hours))
    conn.commit()
    conn.close()
    return jsonify({"total_hours": hours})

@app.route('/boss')
def boss_dashboard():
    if session.get('role') != 'boss': return redirect(url_for('login'))
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    today = datetime.now()
    dates = [(today - timedelta(days=today.weekday() - i)).strftime('%Y-%m-%d') for i in range(7)]
    cursor.execute("SELECT user, date, total FROM shifts")
    data = cursor.fetchall()
    
    report = {}
    employees = set()
    for user, date, total in data:
        employees.add(user)
        if user not in report: report[user] = {}
        report[user][date] = total

    conn.close()
    return render_template('boss.html', report=report, employees=sorted(list(employees)), dates=dates)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
    # Update your init_db() function in app.py
def init_db():
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    # Table for users: stores credentials and roles
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    # Table for shifts: stores work hours
    cursor.execute('''CREATE TABLE IF NOT EXISTS shifts 
                      (id INTEGER PRIMARY KEY, user TEXT, date TEXT, clock_in TEXT, clock_out TEXT, total REAL)''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role') # 'employee' or 'boss'
        
        try:
            conn = sqlite3.connect('work_data.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                           (username, password, role))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return "Username already exists!", 400
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('work_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user'] = username
            session['role'] = user[0]
            return redirect(url_for('home'))
        return "Invalid credentials", 401
    return render_template('login.html')