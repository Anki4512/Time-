import os
import json
import base64
import gspread
from flask import Flask, render_template, request, jsonify
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# 1. Initialize Flask
# This MUST be at the top level so Gunicorn can find it
app = Flask(__name__)

# 2. Configuration
SHEET_ID = "1Njd1Wq9AvQF1okWN09psOd9oHQAmCKOKKQKL9DOc_hU"

def get_sheet():
    """
    Decodes the Base64 Google JSON from Render Environment Variables
    and connects to the Google Sheet.
    """
    try:
        # Get the Base64 string from Render Environment
        encoded_json = os.environ.get('GOOGLE_JSON')
        
        if not encoded_json:
            print("LOG ERROR: GOOGLE_JSON Environment Variable not found in Render!")
            return None
        
        # Decode the Base64 string back into a JSON dictionary
        try:
            decoded_bytes = base64.b64decode(encoded_json)
            info = json.loads(decoded_bytes)
        except Exception as e:
            print(f"LOG ERROR: Failed to decode Base64 or parse JSON: {e}")
            return None
        
        # Authenticate with Google
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Return the first worksheet
        return client.open_by_key(SHEET_ID).get_worksheet(0)
        
    except Exception as e:
        print(f"LOG ERROR: Critical connection failure: {e}")
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
            return "Database Error: Could not connect to Google Sheets. Check Render Logs.", 500
            
        records = sheet.get_all_records()
        
        # Setup current week dates (Monday to Sunday)
        today = datetime.now()
        dates = [(today - timedelta(days=today.weekday() - i)).strftime('%Y-%m-%d') for i in range(7)]
        
        report = {}
        employees = set()
        
        for row in records:
            user = row.get('Name')
            date = str(row.get('Date'))
            # Ensure Total is a float for grand total calculations
            try:
                total = float(row.get('Total', 0))
            except (ValueError, TypeError):
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
        return f"Dashboard Logic Error: {e}", 500

@app.route('/calculate', methods=['POST'])
def calculate():
    """Calculates hours and appends to Google Sheet"""
    try:
        data = request.json
        fmt = '%H:%M'
        
        # Logic to calculate time difference
        tdelta = datetime.strptime(data['out'], fmt) - datetime.strptime(data['in'], fmt)
        hours = round(tdelta.seconds / 3600, 2)
        
        sheet = get_sheet()
        if not sheet:
            return jsonify({"error": "Sheet connection failed"}), 500
            
        # Append the row to Google Sheets: [Name, Date, In, Out, Total]
        sheet.append_row([data['name'], data['date'], data['in'], data['out'], hours])
        
        return jsonify({"total_hours": hours})
    except Exception as e:
        print(f"LOG ERROR: Calculation failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Local development settings
    app.run(debug=True)