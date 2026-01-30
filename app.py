import os
import gspread
from google.oauth2.service_account import Credentials
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# 1. Setup Google Sheets Connection
# We use the path 'templates/credientials.json' based on your GitHub error logs
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_path = os.path.join(os.getcwd(), 'templates', 'credientials.json')
creds = Credentials.from_service_account_file(creds_path, scopes=scope)
client = gspread.authorize(creds)

# 2. Open your specific sheet
SHEET_ID = "1Njd1Wq9AvQF1okWN09psOd9oHQAmCKOKKQKL9DOc_hU"
spreadsheet = client.open_by_key(SHEET_ID)
sheet = spreadsheet.get_worksheet(0) # Uses the first tab (Sheet1)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/boss')
def boss_dashboard():
    # Pull data from Google Sheets instead of a local database
    records = sheet.get_all_records()
    
    today = datetime.now()
    dates = [(today - timedelta(days=today.weekday() - i)).strftime('%Y-%m-%d') for i in range(7)]
    
    report = {}
    employees = set()
    
    for row in records:
        user = row.get('Name')
        date = str(row.get('Date'))
        total = row.get('Total')
        
        if user:
            employees.add(user)
            if user not in report: report[user] = {}
            report[user][date] = total
            
    return render_template('boss.html', report=report, employees=sorted(list(employees)), dates=dates)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    fmt = '%H:%M'
    
    # Logic to calculate hours worked
    tdelta = datetime.strptime(data['out'], fmt) - datetime.strptime(data['in'], fmt)
    hours = round(tdelta.seconds / 3600, 2)
    
    # Append the row to Google Sheets: [Name, Date, In, Out, Total]
    sheet.append_row([data['name'], data['date'], data['in'], data['out'], hours])
    
    return jsonify({"total_hours": hours})