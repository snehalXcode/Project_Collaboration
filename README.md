# Smart Group Formation and Collaboration System for Students

This is a simple web-based project to help college students form project groups for different subjects and collaborate within those groups.

## Tech Stack

- **Frontend**: HTML, CSS (vanilla)
- **Backend**: Python (Flask)
- **Database**: SQLite (via Flask-SQLAlchemy)

## Main Features

- **User Authentication**: Students can sign up and log in (name, roll number, email, password).
- **Dashboard**: Shows available subjects as cards.
- **Group Creation**:
  - Student creates a group and automatically becomes **Team Leader**.
  - Leader selects subject and team size.
  - Leader picks members only from **Available** students (not already in a group for that subject).
- **Student Availability**:
  - Students are split into **Available** and **Unavailable** for each subject.
  - A student can belong to **only one group per subject**.
- **Group Dashboard**:
  - Member list and leader badge.
  - Task assignment and completion (basic progress tracker).
  - Simple group chat (message board style).

## Folder Structure

```text
Project collabration tool/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md
├── smart_groups.db         # SQLite DB (created automatically on first run)
├── templates/
│   ├── base.html           # Base layout (navbar, flash messages)
│   ├── login.html          # Login page
│   ├── register.html       # Sign-up page
│   ├── dashboard.html      # Subject dashboard with cards
│   ├── create_group.html   # Group creation + available/unavailable lists
│   └── group_detail.html   # Group dashboard (members, tasks, chat)
└── static/
    └── css/
        └── style.css       # Basic student-friendly styling
```

## Running the Project

1. **Create and activate a virtual environment** (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Flask app:

```bash
python app.py
```

4. Open your browser and go to:

```text
http://127.0.0.1:5000/
```

The database and default subjects are created automatically on first run.

