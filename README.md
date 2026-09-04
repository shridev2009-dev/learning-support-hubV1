# Learning Support Hub — Setup Instructions

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
database. The application loads these values automatically.

## 4. Run the app
From inside the `learning_hub` folder:
```
python app.py
```
Then open your browser at: http://127.0.0.1:5000/

## 5. Login credentials
- **Students**: Register via the Register page, then log in with that email/password.
- **Teacher**: Use the built-in login —
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
