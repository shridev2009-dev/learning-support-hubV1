# Learning Support Hub — Setup Instructions

## Live app
The deployed app is hosted on Render: https://learning-support-hubv1.onrender.com/

## 1. Requirements
Install Flask and MySQL connector:
```
pip install flask mysql-connector-python
```

## 2. Set up the database
1. Open MySQL (Workbench or command line).
2. Run the contents of `schema.sql` — this creates the `learning_hub` database
  and the five tables: `student`, `teachers`, `material`, `quiz`, `progress`.

## 3. Configure database connection
Copy `.env.example` to `.env` and set the MySQL connection values for your local
database. Set a private `FLASK_SECRET_KEY`, `ADMIN_USERNAME`, and
`ADMIN_PASSWORD` in `.env` as well; change the example admin password before
using the app. The application loads these values automatically.
For hosted MySQL providers, use their supplied host and port; set the matching
`MYSQL_HOST` and `MYSQL_PORT` values in your deployment environment.

## 4. Run the app
From inside the `learning_hub` folder:
```
python app.py
```
Then open your browser at: http://127.0.0.1:5000/

Student registration (while the local app is running):
http://127.0.0.1:5000/register

This address is local to your computer; it is not a public link.

Admin registration management (after signing in with the configured admin account):
http://127.0.0.1:5000/admin/students
Admins can review, edit, and delete student registration records. Deleting a
student also deletes their progress records because of the schema's cascading
foreign key. This page manages records; it does not expose database schema
changes.

## 5. Login credentials
- **Students**: Register via the Register page, then log in with that email/password.
- **Teachers**: Register at `/teacher_register`, then log in with the new username and password.
- **Admins**: Use the username and password configured in `.env`.
- **Demo teacher**: Use the built-in login —
  - Username: `teacher1`
  - Password: `teacher123`
  (You can change these in `app.py` at the top.)

## 6. Project flow
1. Teacher logs in → uploads study material (module) → adds quiz questions linked to that module.
2. Student registers/logs in → views materials → takes quiz on a module → views their progress/scores.

## 7. Folder structure
```
learning_hub/
├── app.py              # Main Flask app with all routes
├── db.py                # MySQL connection helper
├── schema.sql            # Database schema (run this first)
├── templates/            # HTML pages (Jinja2 templates)
└── static/
    └── style.css          # Styling
```

## Notes for your project report
- Passwords are stored as plain text for simplicity — this is acceptable for a
  Class 12 board project. If you want to add password hashing, ask and it can
  be added using `werkzeug.security`.
- Teacher login currently uses the built-in credentials above. The `teachers`
  table is available for future database-backed teacher accounts.
- Foreign keys are used between `material` → `quiz` → `progress` → `student`,
  which you can highlight in your viva as good relational design.
