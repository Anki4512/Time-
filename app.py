import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

def init_db():
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    # Stores registered users
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    # Stores shift data
    cursor.execute('''CREATE TABLE IF NOT EXISTS shifts 
                      (id INTEGER PRIMARY KEY, user TEXT, date TEXT, clock_in TEXT, clock_out TEXT, total REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session.get('role') == 'boss':
        return redirect(url_for('boss_dashboard'))
    return render_template('index.html', user=session['user'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Keep your existing /calculate and /boss routes below this...