import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from db import get_db_connection

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret_key"   # needed for sessions

UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------- HOME ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form["role"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        table = "student" if role == "student" else "teacher"
        placeholder = "?" if conn.__class__.__module__.startswith("sqlite3") else "%s"

        cursor.execute(f"SELECT * FROM {table} WHERE email = {placeholder}", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email already registered. Please log in.")
            cursor.close()
            conn.close()
            return redirect(url_for("register"))

        if role == "student":
            cursor.execute(
                f"INSERT INTO student (name, email, password) VALUES ({placeholder}, {placeholder}, {placeholder})",
                (name, email, hashed_pw)
            )
        else:
            subject = request.form.get("subject", "")
            cursor.execute(
                f"INSERT INTO teacher (name, email, password, subject) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})",
                (name, email, hashed_pw, subject)
            )

        conn.commit()
        cursor.close()
        conn.close()

        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form["role"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        table = "student" if role == "student" else "teacher"
        id_col = "student_id" if role == "student" else "teacher_id"
        placeholder = "?" if conn.__class__.__module__.startswith("sqlite3") else "%s"

        cursor.execute(f"SELECT * FROM {table} WHERE email = {placeholder}", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user[id_col]
            session["name"] = user["name"]
            session["role"] = role
            flash(f"Welcome, {user['name']}!")
            if role == "student":
                return redirect(url_for("student_dashboard"))
            else:
                return redirect(url_for("teacher_dashboard"))
        else:
            flash("Invalid email or password.")
            return redirect(url_for("login"))

    return render_template("login.html")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("index"))


# ---------- STUDENT DASHBOARD ----------
@app.route("/student_dashboard")
def student_dashboard():
    if session.get("role") != "student":
        flash("Please log in as a student to view this page.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM material ORDER BY upload_date DESC")
    materials = cursor.fetchall()

    cursor.execute("SELECT * FROM quiz ORDER BY created_at DESC")
    quizzes = cursor.fetchall()

    cursor.execute(
        "SELECT q.title, qa.score, qa.total_questions, qa.submitted_at FROM quiz_attempt qa JOIN quiz q ON q.quiz_id = qa.quiz_id WHERE qa.student_id = ? ORDER BY qa.submitted_at DESC",
        (session["user_id"],)
    )
    attempts = cursor.fetchall()

    total_questions = sum(int(row["total_questions"]) for row in attempts) if attempts else 0
    total_score = sum(int(row["score"]) for row in attempts) if attempts else 0
    average = round((total_score / total_questions) * 100, 1) if total_questions else 0

    cursor.close()
    conn.close()

    return render_template(
        "student_dashboard.html",
        materials=materials,
        quizzes=quizzes,
        attempts=attempts,
        total_score=total_score,
        total_questions=total_questions,
        average=average,
    )


# ---------- TEACHER DASHBOARD ----------
@app.route("/teacher_dashboard")
def teacher_dashboard():
    if session.get("role") != "teacher":
        flash("Please log in as a teacher to view this page.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = "?" if conn.__class__.__module__.startswith("sqlite3") else "%s"
    cursor.execute(
        f"SELECT * FROM material WHERE uploaded_by = {placeholder} ORDER BY upload_date DESC",
        (session["user_id"],)
    )
    materials = cursor.fetchall()

    cursor.execute(
        f"SELECT * FROM quiz WHERE created_by = {placeholder} ORDER BY created_at DESC",
        (session["user_id"],)
    )
    quizzes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("teacher_dashboard.html", materials=materials, quizzes=quizzes)


# ---------- QUIZ MANAGEMENT ----------
@app.route("/teacher_quizzes")
def teacher_quizzes():
    if session.get("role") != "teacher":
        flash("Please log in as a teacher to manage quizzes.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = "?" if conn.__class__.__module__.startswith("sqlite3") else "%s"
    cursor.execute(
        f"SELECT * FROM quiz WHERE created_by = {placeholder} ORDER BY created_at DESC",
        (session["user_id"],)
    )
    quizzes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("teacher_quizzes.html", quizzes=quizzes)


@app.route("/create_quiz", methods=["GET", "POST"])
def create_quiz():
    if session.get("role") != "teacher":
        flash("Please log in as a teacher to create a quiz.")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description", "")
        question = request.form["question"]
        option_a = request.form["option_a"]
        option_b = request.form["option_b"]
        option_c = request.form["option_c"]
        option_d = request.form["option_d"]
        correct_option = request.form["correct_option"].upper()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO quiz (title, description, created_by) VALUES (?, ?, ?)",
            (title, description, session["user_id"])
        )
        quiz_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO quiz_question (quiz_id, question, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (quiz_id, question, option_a, option_b, option_c, option_d, correct_option)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Quiz created successfully!")
        return redirect(url_for("teacher_quizzes"))

    return render_template("create_quiz.html")


@app.route("/quiz/<int:quiz_id>", methods=["GET", "POST"])
def quiz_detail(quiz_id):
    if session.get("role") != "student":
        flash("Please log in as a student to attempt quizzes.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz WHERE quiz_id = ?", (quiz_id,))
    quiz = cursor.fetchone()
    cursor.execute("SELECT * FROM quiz_question WHERE quiz_id = ?", (quiz_id,))
    question = cursor.fetchone()
    cursor.close()
    conn.close()

    if not quiz or not question:
        flash("This quiz is not available yet.")
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        submitted_answer = request.form.get("answer", "").upper()
        is_correct = submitted_answer == question["correct_option"]
        total_questions = 1
        score = 1 if is_correct else 0

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO quiz_attempt (quiz_id, student_id, score, total_questions) VALUES (?, ?, ?, ?)",
            (quiz_id, session["user_id"], score, total_questions)
        )
        conn.commit()
        cursor.close()
        conn.close()

        if is_correct:
            flash("Correct! Great job.")
        else:
            flash(f"Not quite. The correct answer was {question['correct_option']}.")
        return redirect(url_for("progress"))

    return render_template("quiz_detail.html", quiz=quiz, question=question)


@app.route("/progress")
def progress():
    if session.get("role") != "student":
        flash("Please log in as a student to view progress.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT q.title, qa.score, qa.total_questions, qa.submitted_at FROM quiz_attempt qa JOIN quiz q ON q.quiz_id = qa.quiz_id WHERE qa.student_id = ? ORDER BY qa.submitted_at DESC",
        (session["user_id"],)
    )
    attempts = cursor.fetchall()
    total_questions = sum(int(row["total_questions"]) for row in attempts) if attempts else 0
    total_score = sum(int(row["score"]) for row in attempts) if attempts else 0
    average = round((total_score / total_questions) * 100, 1) if total_questions else 0
    last_score = attempts[0] if attempts else None
    cursor.close()
    conn.close()

    return render_template(
        "progress.html",
        attempts=attempts,
        total_score=total_score,
        total_questions=total_questions,
        average=average,
        last_score=last_score,
    )


# ---------- UPLOAD MATERIAL (teacher only) ----------
@app.route("/upload_material", methods=["GET", "POST"])
def upload_material():
    if session.get("role") != "teacher":
        flash("Please log in as a teacher to upload material.")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        file = request.files["file"]

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(filepath)

        conn = get_db_connection()
        cursor = conn.cursor()
        placeholder = "?" if conn.__class__.__module__.startswith("sqlite3") else "%s"
        cursor.execute(
            f"INSERT INTO material (title, description, file_path, uploaded_by, upload_date) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, { 'CURRENT_DATE' if conn.__class__.__module__.startswith('sqlite3') else 'CURDATE()' })",
            (title, description, filepath, session["user_id"])
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Material uploaded successfully!")
        return redirect(url_for("teacher_dashboard"))

    return render_template("upload_material.html")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
