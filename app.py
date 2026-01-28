from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    # Logic: (Clock Out - Clock In)
    fmt = '%H:%M'
    tdelta = datetime.strptime(data['out'], fmt) - datetime.strptime(data['in'], fmt)
    hours = tdelta.seconds / 3600
    return jsonify({"total_hours": round(hours, 2)})

if __name__ == '__main__':
    app.run(debug=True)
