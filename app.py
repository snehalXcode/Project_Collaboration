from datetime import datetime
from functools import wraps
import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)

# Secret key is required for sessions and flash messages.
app.config["SECRET_KEY"] = "change-this-secret-key-in-production"

# SQLite database configuration: store DB file inside dedicated data folder.
db_path = os.path.join(DATA_DIR, "smart_groups.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Predefined list of subjects shown on dashboard.
DEFAULT_SUBJECTS = [
    "Artificial Intelligence",
    "DBMS",
    "Computer Networks",
    "Software Engineering",
    "Operating Systems",
    "Cloud Computing",
    "Machine Learning",
    "Data Structures",
    "Web Technologies",
]


class User(db.Model):
    """Stores student account information."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Subject(db.Model):
    """Represents a course/subject for which groups can be formed."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    groups = db.relationship("ProjectGroup", backref="subject", lazy=True)


class ProjectGroup(db.Model):
    """Represents a project group for a specific subject."""

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    team_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    leader = db.relationship("User", foreign_keys=[leader_id])
    members = db.relationship("GroupMember", backref="group", lazy=True, cascade="all, delete-orphan")
    tasks = db.relationship("Task", backref="group", lazy=True, cascade="all, delete-orphan")
    messages = db.relationship("Message", backref="group", lazy=True, cascade="all, delete-orphan")


class GroupMember(db.Model):
    """Links users to groups and indicates the leader."""

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("project_group.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_leader = db.Column(db.Boolean, default=False)

    user = db.relationship("User")


class Task(db.Model):
    """Stores tasks for a group and a simple completion flag for progress tracking."""

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("project_group.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)


class Message(db.Model):
    """Represents a simple chat message in a group."""

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("project_group.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")


def login_required(view_func):
    """Decorator to ensure a user is logged in before accessing a route."""

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def get_current_user():
    """Convenience helper to return the currently logged-in user object or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def seed_subjects():
    """Populate the Subject table with a default set if it's empty."""
    if Subject.query.count() == 0:
        for name in DEFAULT_SUBJECTS:
            db.session.add(Subject(name=name))
        db.session.commit()


def initialize_database():
    """Create all tables and ensure subjects exist before serving traffic."""
    db.create_all()
    seed_subjects()


@app.route("/")
def index():
    """Redirects to dashboard if logged in, otherwise to login page."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles new student sign up."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        roll_number = request.form.get("roll_number", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not all([name, roll_number, email, password]):
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("login"))

        user = User(name=name, roll_number=roll_number, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticates a student and starts a session."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id

        # Append a simple login record to a log file inside the data folder.
        log_path = os.path.join(DATA_DIR, "login_log.txt")
        try:
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(
                    f"{datetime.utcnow().isoformat()} | user_id={user.id} | "
                    f"name={user.name} | email={user.email}\n"
                )
        except OSError:
            # If logging fails, do not block the login flow.
            pass

        flash("Logged in successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clears the session for the current user."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Shows subjects as cards and indicates group status for the logged-in student."""
    user = get_current_user()
    subjects = Subject.query.order_by(Subject.name).all()

    # For each subject, determine if the user is already part of a group.
    subject_status = []
    for subject in subjects:
        group = (
            ProjectGroup.query.join(GroupMember)
            .filter(
                ProjectGroup.subject_id == subject.id,
                GroupMember.user_id == user.id,
            )
            .first()
        )
        subject_status.append(
            {
                "subject": subject,
                "group": group,
            }
        )

    return render_template("dashboard.html", user=user, subject_status=subject_status)


@app.route("/students")
@login_required
def students():
    """Shows a simple list of all enrolled students in the system."""
    user = get_current_user()
    all_students = User.query.order_by(User.name).all()
    return render_template("students.html", user=user, students=all_students)


@app.route("/subject/<int:subject_id>/create_group", methods=["GET", "POST"])
@login_required
def create_group(subject_id: int):
    """Allows a student to create a group for a subject and select members."""
    user = get_current_user()
    subject = db.session.get(Subject, subject_id)
    if not subject:
        flash("Subject not found.", "danger")
        return redirect(url_for("dashboard"))

    # Enforce rule: one group per subject per student.
    existing_group = (
        ProjectGroup.query.join(GroupMember)
        .filter(
            ProjectGroup.subject_id == subject.id,
            GroupMember.user_id == user.id,
        )
        .first()
    )
    if existing_group:
        flash("You are already in a group for this subject.", "warning")
        return redirect(url_for("group_detail", group_id=existing_group.id))

    # Compute availability: students not in any group for this subject are "Available".
    all_users = User.query.order_by(User.name).all()
    users_in_subject_groups = (
        db.session.query(User.id)
        .join(GroupMember, GroupMember.user_id == User.id)
        .join(ProjectGroup, ProjectGroup.id == GroupMember.group_id)
        .filter(ProjectGroup.subject_id == subject.id)
        .distinct()
        .all()
    )
    unavailable_ids = {row[0] for row in users_in_subject_groups}

    available_students = [u for u in all_users if u.id not in unavailable_ids]
    unavailable_students = [u for u in all_users if u.id in unavailable_ids]

    if request.method == "POST":
        try:
            team_size = int(request.form.get("team_size", "0"))
        except ValueError:
            team_size = 0

        selected_ids = request.form.getlist("members")
        member_ids = {int(uid) for uid in selected_ids if uid.isdigit()}

        # Include leader in size counting.
        total_members = 1 + len(member_ids)

        if team_size <= 0:
            flash("Please enter a valid team size.", "danger")
            return redirect(request.url)

        if total_members > team_size:
            flash("Team size cannot exceed the chosen limit.", "danger")
            return redirect(request.url)

        # Ensure leader is not accidentally selected and all members are available.
        if user.id in member_ids:
            member_ids.remove(user.id)

        invalid_members = [mid for mid in member_ids if mid in unavailable_ids]
        if invalid_members:
            flash("One or more selected students are not available.", "danger")
            return redirect(request.url)

        # Create the group and associated member records.
        group = ProjectGroup(subject_id=subject.id, leader_id=user.id, team_size=team_size)
        db.session.add(group)
        db.session.flush()  # Get group.id before inserting members.

        # Add leader as a group member.
        db.session.add(GroupMember(group_id=group.id, user_id=user.id, is_leader=True))

        # Add selected members.
        for mid in member_ids:
            db.session.add(GroupMember(group_id=group.id, user_id=mid, is_leader=False))

        db.session.commit()
        flash("Group created successfully.", "success")
        return redirect(url_for("group_detail", group_id=group.id))

    return render_template(
        "create_group.html",
        user=user,
        subject=subject,
        available_students=available_students,
        unavailable_students=unavailable_students,
    )


@app.route("/group/<int:group_id>", methods=["GET", "POST"])
@login_required
def group_detail(group_id: int):
    """Displays the group dashboard, including members, tasks, and simple chat."""
    user = get_current_user()
    group = db.session.get(ProjectGroup, group_id)
    if not group:
        flash("Group not found.", "danger")
        return redirect(url_for("dashboard"))

    # Ensure current user is part of this group.
    membership = GroupMember.query.filter_by(group_id=group.id, user_id=user.id).first()
    if not membership:
        flash("You do not have access to this group.", "danger")
        return redirect(url_for("dashboard"))

    # Handle creation of tasks and chat messages via POST.
    action = request.form.get("action")

    if request.method == "POST":
        if action == "add_task":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            if title:
                task = Task(group_id=group.id, title=title, description=description)
                db.session.add(task)
                db.session.commit()
                flash("Task added.", "success")
            else:
                flash("Task title is required.", "danger")

        elif action == "toggle_task":
            task_id = request.form.get("task_id")
            task = Task.query.filter_by(id=task_id, group_id=group.id).first()
            if task:
                task.is_completed = not task.is_completed
                db.session.commit()
                flash("Task status updated.", "success")

        elif action == "send_message":
            content = request.form.get("content", "").strip()
            if content:
                message = Message(group_id=group.id, user_id=user.id, content=content)
                db.session.add(message)
                db.session.commit()
            else:
                flash("Message cannot be empty.", "danger")

        return redirect(url_for("group_detail", group_id=group.id))

    # Calculate simple progress statistics for tasks.
    total_tasks = len(group.tasks)
    completed_tasks = len([t for t in group.tasks if t.is_completed])
    progress_percent = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    # Sort messages by time for chat display.
    messages = sorted(group.messages, key=lambda m: m.created_at)

    return render_template(
        "group_detail.html",
        user=user,
        group=group,
        membership=membership,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        progress_percent=progress_percent,
        messages=messages,
    )


if __name__ == "__main__":
    # In Flask 3, before_first_request was removed, so we
    # explicitly initialize the database when the app starts.
    with app.app_context():
        initialize_database()
    app.run(debug=True)

