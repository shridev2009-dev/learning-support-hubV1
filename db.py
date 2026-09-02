import os
import sqlite3

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except Exception:  # pragma: no cover - optional dependency
    mysql = None
    MySQLError = Exception

# If python-dotenv is installed and a .env file exists, load it automatically.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv is optional; if it's not installed, environment variables
    # can still be set externally (PowerShell, cmd, system env).
    pass


def _is_placeholder_value(value):
    if value is None:
        return True
    value = str(value).strip()
    return value == "" or value.lower() in {
        "replace_with_db_password",
        "secure_password_here",
        "your_password",
        "changeme",
        "password"
    }


def _create_sqlite_schema(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS student (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS teacher (
            teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            subject TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS material (
            material_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            file_path TEXT NOT NULL,
            uploaded_by INTEGER NOT NULL,
            upload_date TEXT NOT NULL DEFAULT CURRENT_DATE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz (
            quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_DATE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_question (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL CHECK(correct_option IN ('A','B','C','D')),
            FOREIGN KEY(quiz_id) REFERENCES quiz(quiz_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_attempt (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            submitted_at TEXT NOT NULL DEFAULT CURRENT_DATE,
            FOREIGN KEY(quiz_id) REFERENCES quiz(quiz_id)
        )
        """
    )
    conn.commit()


def get_sqlite_connection():
    db_path = os.path.join(os.path.dirname(__file__), "learning_hub.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _create_sqlite_schema(conn)
    return conn


def get_db_connection():
    """Return a MySQL connection when configured, otherwise fall back to SQLite."""
    host = os.environ.get("MYSQL_HOST", "localhost")
    user = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    database = os.environ.get("MYSQL_DATABASE", "learning_hub")

    if mysql is None or _is_placeholder_value(password) or os.environ.get("USE_SQLITE", "").lower() in {"1", "true", "yes"}:
        return get_sqlite_connection()

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        return conn
    except MySQLError as e:
        return get_sqlite_connection()
