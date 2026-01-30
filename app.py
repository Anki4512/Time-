import os
import json
import base64
import gspread
from flask import Flask, render_template, request, jsonify
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# 1. Initialize Flask
app = Flask(__name__)

# 2. Configuration
SHEET_ID = "1Njd1Wq9AvQF1okWN09psOd9oHQAmCKOKKQKL9DOc_hU"

def get_sheet():
    """
    Decodes the Base64 Google JSON from Render Environment Variables
    and connects to the Google Sheet.
    """
    try:
        encoded_json = os.environ.get('GOOGLE_JSON')
        if not encoded_json:
            print("ERROR: GOOGLE_JSON Environment Variable not found!")
            return None
        
        # Decode Base64 to clean JSON
        decoded_bytes = base64.b64decode(encoded_json)
        info = json.loads(decoded_bytes)
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key(SHEET_ID).get_worksheet(0)
    except Exception as e:
        print(f"Failed to connect to Google Sheets: {e}")
        return None

# --- ROUTES ---

@app.route('/')
def home():
    """Employee Clock-In Page"""
    return render_template('index.html')

@app.route('/boss')
def boss_dashboard():
    """Boss View with Weekly Totals and Native Sharing"""
    try:
        sheet = get_sheet()
        if not sheet:
            return "Error: Could not connect to Google Sheets. Check Render Environment Variables.", 500
            
        records = sheet.get_all_records()
        
        # Setup current week dates (Monday to Sunday)
        today = datetime.now()
        dates = [(today - timedelta(days=today.weekday() - i)).strftime('%Y-%m-%d') for i in range(7)]
        
        report = {}
        employees = set()
        
        for row in records:
            user = row.get('Name')
            date = str(row.get('Date'))
            # Ensure Total is a float for math
            try:
                total = float(row.get('Total', 0))
            except:
                total = 0.0
                
            if user:
                employees.add(user)
                if user not in report:
                    report[user] = {}
                report[user][date] = total
                
        return render_template('boss.html', 
                               report=report, 
                               employees=sorted(list(employees)), 
                               dates=dates)
    except Exception as e:
        return f"Dashboard Error: {e}", 500

@app.route('/calculate', methods=['POST'])
def calculate():
    """Calculates hours and appends to Google Sheet"""
    try:
        data = request.json
        fmt = '%H:%M'
        
        # Calculate time difference
        tdelta = datetime.strptime(data['out'], fmt) - datetime.strptime(data['in'], fmt)
        hours = round(tdelta.seconds / 3600, 2)
        
        sheet = get_sheet()
        if not sheet:
            return jsonify({"error": "Sheet connection failed"}), 500
            
        # Append to Google Sheet: Name, Date, In, Out, Total
        sheet.append_row([data['name'], data['date'], data['in'], data['out'], hours])
        
        return jsonify({"total_hours": hours})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Local testing
    app.run(debug=True)