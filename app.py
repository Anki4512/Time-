import os
import json
import gspread
from flask import Flask, render_template, request, jsonify
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# 1. Initialize Flask (Gunicorn needs this 'app' variable at the top level)
app = Flask(__name__)

# 2. Setup Google Sheets Connection
SHEET_ID = "1Njd1Wq9AvQF1okWN09psOd9oHQAmCKOKKQKL9DOc_hU"

def get_sheet():
    # Read the JSON from the Environment Variable we set in Render
    google_json_str = os.environ.get('GOOGLE_JSON')
    if not google_json_str:
        print("ERROR: GOOGLE_JSON Environment Variable not found!")
        return None
    
    info = json.loads(google_json_str)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).get_worksheet(0)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/boss')
def boss_dashboard():
    try:
        sheet = get_sheet()
        records = sheet.get_all_records()
        today = datetime.now()
        dates = [(today - timedelta(days=today.weekday() - i)).strftime('%Y-%m-%d') for i in range(7)]
        
        report = {}
        employees = set()
        for row in records:
            user = row.get('Name')
            date = str(row.get('Date'))
            total = row.get('Total', 0)
            if user:
                employees.add(user)
                if user not in report: report[user] = {}
                report[user][date] = total
        return render_template('boss.html', report=report, employees=sorted(list(employees)), dates=dates)
    except Exception as e:
        return f"Database Error: {e}", 500

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        fmt = '%H:%M'
        tdelta = datetime.strptime(data['out'], fmt) - datetime.strptime(data['in'], fmt)
        hours = round(tdelta.seconds / 3600, 2)
        
        sheet = get_sheet()
        sheet.append_row([data['name'], data['date'], data['in'], data['out'], hours])
        return jsonify({"total_hours": hours})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)