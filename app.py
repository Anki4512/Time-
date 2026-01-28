from datetime import datetime, timedelta

@app.route('/boss')
def boss_dashboard():
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    
    # Get the start and end of the current week (Mon-Sun)
    today = datetime.now()
    start_week = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
    end_week = (today + timedelta(days=6 - today.weekday())).strftime('%Y-%m-%d')

    # Fetch all shifts for this week
    cursor.execute("SELECT user, date, total FROM shifts WHERE date BETWEEN ? AND ?", (start_week, end_week))
    data = cursor.fetchall()
    
    # Organize data for the table: { 'Name': { 'Date': hours } }
    report = {}
    employees = set()
    dates = []
    for i in range(7):
        dates.append((today - timedelta(days=today.weekday() - i)).strftime('%Y-%m-%d'))

    for user, date, total in data:
        employees.add(user)
        if user not in report: report[user] = {}
        report[user][date] = total

    conn.close()
    return render_template('boss.html', report=report, employees=sorted(list(employees)), dates=dates)