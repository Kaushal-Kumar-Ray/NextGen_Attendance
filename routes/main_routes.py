from flask import Blueprint, render_template, send_file
from services.csv_service import load_students, load_attendance
from datetime import datetime
import os

main_bp = Blueprint("main", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance.csv")

@main_bp.route("/")
def dashboard():
    students = load_students()
    attendance = load_attendance()

    today = datetime.now().strftime("%Y-%m-%d")
    present_ids = {a["id"] for a in attendance if a.get("date") == today}

    return render_template(
        "home.html",
        total_students=len(students),
        present_today=len(present_ids),
        absent_today=len(students) - len(present_ids),
        today=today
    )

@main_bp.route("/register")
def register():
    return render_template("register.html")

@main_bp.route("/attendance")
def attendance_page():
    return render_template("attendance.html")

@main_bp.route("/students")
def students_page():
    students = load_students()
    attendance = load_attendance()

    today = datetime.now().strftime("%Y-%m-%d")
    present_ids = {a["id"] for a in attendance if a.get("date") == today}

    enriched = [
        {"id": s["id"], "name": s["name"], "present": s["id"] in present_ids}
        for s in students
    ]

    return render_template(
        "students.html",
        students=enriched,
        total=len(students),
        present=len(present_ids),
        absent=len(students) - len(present_ids)
    )

@main_bp.route("/records")
def records_page():
    return render_template(
        "records.html",
        records=load_attendance()
    )

@main_bp.route("/download-attendance")
def download_attendance():
    return send_file(ATTENDANCE_FILE, as_attachment=True)