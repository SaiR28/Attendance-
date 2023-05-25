from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)
DATABASE = 'attendance.db'

# Database connection helper function
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Create the database table if it doesn't exist
def create_table():
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS students')  # Drop existing table
        cursor.execute('''CREATE TABLE students
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           subject TEXT NOT NULL,
                           attendance_date DATE NOT NULL,
                           attendance INTEGER NOT NULL)''')
        conn.commit()

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Attendance form submission
@app.route('/attendance', methods=['POST'])
def record_attendance():
    name = request.form['name']
    subject = request.form['subject']
    date = request.form['date']
    attendance = int(request.form['attendance'])

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO students (name, subject, attendance_date, attendance) VALUES (?, ?, ?, ?)',
                   (name, subject, date, attendance))
    conn.commit()

    return 'Attendance recorded successfully.'

# View attendance records
@app.route('/view')
def view_attendance():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name, subject, SUM(attendance) AS total_attendance, COUNT(*) AS total_days FROM students GROUP BY name, subject')
    rows = cursor.fetchall()

    attendance_data = []
    for row in rows:
        name = row[0]
        subject = row[1]
        total_attendance = row[2]
        total_days = row[3]
        percentage = round((total_attendance / total_days) * 100, 2)
        attendance_data.append((name, subject, total_attendance, total_days, percentage))

    return render_template('view.html', attendance_data=attendance_data)

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
