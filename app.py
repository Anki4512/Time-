import os
import json
import gspread
from google.oauth2.service_account import Credentials

# 1. Setup Path correctly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Check if your file is in 'templates' or the main folder
creds_path = os.path.join(BASE_DIR, 'templates', 'credientials.json')

# 2. Scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # We load the JSON manually to ensure it's parsed correctly
    with open(creds_path, 'r') as f:
        info = json.load(f)
    
    creds = Credentials.from_service_account_info(info, scopes=scope)
    client = gspread.authorize(creds)
    
    # Open your sheet
    SHEET_ID = "1Njd1Wq9AvQF1okWN09psOd9oHQAmCKOKKQKL9DOc_hU"
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet = spreadsheet.get_worksheet(0)
    print("Successfully connected to Google Sheets!")
except Exception as e:
    print(f"Connection Error: {e}")