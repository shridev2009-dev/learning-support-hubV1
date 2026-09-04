from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

from db import get_connection

app = Flask(__name__)
app.secret_key = "replace_with_any_random_string"


@app.errorhandler(mysql.connector.Error)
def handle_database_error(error):
    endpoint = request.endpoint or 'login'
    destination = 'teacher_register' if endpoint == 'teacher_register' else endpoint
    if destination not in {'register', 'teacher_register', 'login'}:
        destination = 'login'
    flash("Database connection failed. Copy .env.example to .env and enter your MySQL password.")
    app.logger.error("Database error: %s", error)
    return redirect(url_for(destination))

# Hardcoded teacher credentials
TEACHER_USERNAME = "teacher1"
TEACHER_PASSWORD = "teacher123"


# ---------- Home ----------
@app.route('/')
def home():
    return render_template('home.html')


# ---------- Student Registration ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        student_class = request.form['class']

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM student WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Email already registered. Please login.")
            cursor.close()
            conn.close()
            return redirect(url_for('login'))

        cursor.execute(
            "INSERT INTO student (name, email, password, class) VALUES (%s, %s, %s, %s)",
            (name, email, password, student_class)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Registration successful. Please login.")
        return redirect(url_for('login'))

    return render_template('register.html')


# ---------- Teacher Registration ----------
@app.route('/teacher_register', methods=['GET', 'POST'])
def teacher_register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT teacher_id FROM teachers WHERE username = %s", (username,))
        if cursor.fetchone():
            flash("Username already registered. Please login.")
            cursor.close()
            conn.close()
            return redirect(url_for('login'))

        cursor.execute(
            "INSERT INTO teachers (name, username, password) VALUES (%s, %s, %s)",
            (name, username, password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Teacher registration successful. Please login.")
        return redirect(url_for('login'))

    return render_template('teacher_register.html')


# ---------- Login (Student or Teacher) ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Keep the original demo account available for local setup checks.
        if email == TEACHER_USERNAME and password == TEACHER_PASSWORD:
            session['role'] = 'teacher'
            session['name'] = 'Teacher'
            return redirect(url_for('teacher_dashboard'))

        # Teacher login (database account)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teachers WHERE username = %s AND password = %s", (email, password))
        teacher = cursor.fetchone()
        cursor.close()
        conn.close()

        if teacher:
            session['role'] = 'teacher'
            session['teacher_id'] = teacher['teacher_id']
            session['name'] = teacher['name']
            return redirect(url_for('teacher_dashboard'))

        # Student login (from database)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student WHERE email = %s AND password = %s", (email, password))
        student = cursor.fetchone()
        cursor.close()
        conn.close()

        if student:
            session['role'] = 'student'
            session['student_id'] = student['student_id']
            session['name'] = student['name']
            return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('login'))

    return render_template('login.html')


# ---------- Logout ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ---------- Student Dashboard ----------
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('student_dashboard.html', name=session['name'])


# ---------- Teacher Dashboard ----------
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    return render_template('teacher_dashboard.html')


# ---------- Teacher: Upload Material ----------
@app.route('/upload_material', methods=['GET', 'POST'])
def upload_material():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        content = request.form['content']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO material (title, subject, content, uploaded_by) VALUES (%s, %s, %s, %s)",
            (title, subject, content, session['name'])
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Material uploaded successfully.")
        return redirect(url_for('teacher_dashboard'))

    return render_template('upload_material.html')


# ---------- Student: View Materials ----------
@app.route('/view_materials')
def view_materials():
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM material ORDER BY upload_date DESC")
    materials = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('view_materials.html', materials=materials)


# ---------- Teacher: Add Quiz Question ----------
@app.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM material ORDER BY upload_date DESC")
    materials = cursor.fetchall()

    if request.method == 'POST':
        material_id = request.form['material_id']
        question = request.form['question']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_answer = request.form['correct_answer'].upper()

        cursor2 = conn.cursor()
        cursor2.execute(
            """INSERT INTO quiz (material_id, question, option_a, option_b, option_c, option_d, correct_answer)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (material_id, question, option_a, option_b, option_c, option_d, correct_answer)
        )
        conn.commit()
        cursor2.close()
        flash("Quiz question added.")

    cursor.close()
    conn.close()
    return render_template('add_quiz.html', materials=materials)


# ---------- Student: Take Quiz ----------
@app.route('/take_quiz/<int:material_id>', methods=['GET', 'POST'])
def take_quiz(material_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM quiz WHERE material_id = %s", (material_id,))
    questions = cursor.fetchall()

    if request.method == 'POST':
        score = 0
        for q in questions:
            selected = request.form.get(f"q{q['quiz_id']}")
            if selected and selected.upper() == q['correct_answer']:
                score += 1

            cursor2 = conn.cursor()
            cursor2.execute(
                "INSERT INTO progress (student_id, quiz_id, score) VALUES (%s, %s, %s)",
                (session['student_id'], q['quiz_id'], 1 if selected and selected.upper() == q['correct_answer'] else 0)
            )
            conn.commit()
            cursor2.close()

        cursor.close()
        conn.close()
        flash(f"Quiz submitted. You scored {score} out of {len(questions)}.")
        return redirect(url_for('student_dashboard'))

    cursor.close()
    conn.close()
    return render_template('take_quiz.html', questions=questions, material_id=material_id)


# ---------- Student: View Progress ----------
@app.route('/progress')
def progress():
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.title, q.question, p.score, p.date_attempted
        FROM progress p
        JOIN quiz q ON p.quiz_id = q.quiz_id
        JOIN material m ON q.material_id = m.material_id
        WHERE p.student_id = %s
        ORDER BY p.date_attempted DESC
    """, (session['student_id'],))
    records = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('progress.html', records=records)


if __name__ == '__main__':
    app.run(debug=True)
