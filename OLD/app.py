from flask import Flask, render_template, request, g, redirect, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management
DATABASE = 'attendance.db'


# Database connection helper function
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def create_tables():
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS students
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           subject1 TEXT NOT NULL,
                           subject2 TEXT NOT NULL,
                           subject3 TEXT NOT NULL,
                           subject4 TEXT NOT NULL,
                           subject5 TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS attendance
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           student_id INTEGER,
                           date TEXT NOT NULL,
                           subject TEXT NOT NULL,
                           attendance INTEGER,
                           FOREIGN KEY (student_id) REFERENCES students(id))''')
        conn.commit()


# Home page
@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM students')
    rows = cursor.fetchall()
    students = [row[0] for row in rows]
    return render_template('index.html', students=students)


# Add Student page
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO students (name)
                          VALUES (?)''',
                       (name,))
        conn.commit()

        flash('Student added successfully', 'success')
        return redirect('/add_student')

    return render_template('add_student.html')



# Mark Attendance page
@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        subject = request.form['subject']
        attendance = int(request.form['attendance'])

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM students WHERE name=?', (name,))
        student_id = cursor.fetchone()[0]
        cursor.execute('''INSERT INTO attendance (student_id, date, subject, attendance)
                          VALUES (?, ?, ?, ?)''',
                       (student_id, date, subject, attendance))
        conn.commit()

        flash('Attendance marked successfully', 'success')
        return redirect('/mark_attendance')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM students')
    rows = cursor.fetchall()
    students = [row[0] for row in rows]

    return render_template('mark_attendance.html', students=students)


# Summary page
@app.route('/summary')
def summary():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name, subject1, subject2, subject3, subject4, subject5 FROM students')
    rows = cursor.fetchall()
    attendance_summary = []

    for row in rows:
        name = row[0]
        subjects = row[1:]
        total_days = 0
        present_days = 0

        for subject in subjects:
            cursor.execute('''SELECT attendance FROM attendance
                              WHERE student_id IN (SELECT id FROM students WHERE name=?) AND subject=?''',
                           (name, subject))
            attendance_records = cursor.fetchall()
            total_days += len(attendance_records)
            present_days += sum([record[0] for record in attendance_records])

        if total_days > 0:
            monthly_attendance = (present_days / total_days) * 100
        else:
            monthly_attendance = 0

        attendance_summary.append({
            'name': name,
            'monthly_attendance': monthly_attendance,
            'total_days': total_days,
            'present_days': present_days
        })

    return render_template('summary.html', attendance_summary=attendance_summary)


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
