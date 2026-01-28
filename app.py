@app.route('/boss')
def boss_dashboard():
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    
    # This query groups by name and sums the hours for the current week
    cursor.execute('''SELECT user, SUM(total), COUNT(id) 
                      FROM shifts 
                      WHERE date >= date('now', '-7 days')
                      GROUP BY user''')
    summary = cursor.fetchall()
    conn.close()
    return render_template('boss.html', summary=summary)

@app.route('/boss/details/<name>')
def employee_details(name):
    conn = sqlite3.connect('work_data.db')
    cursor = conn.cursor()
    # This gets every specific log for just one person
    cursor.execute("SELECT * FROM shifts WHERE user = ? ORDER BY date DESC", (name,))
    details = cursor.fetchall()
    conn.close()
    return render_template('details.html', name=name, details=details)