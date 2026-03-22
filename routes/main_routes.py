from flask import Blueprint, render_template, send_file
from services.db_service import load_students, load_attendance
from datetime import datetime
import os

main_bp = Blueprint("main", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@main_bp.route("/")
def root():
    return render_template("login.html")


@main_bp.route("/dashboard")
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

    # Total unique days
    total_days = len(set([a["date"] for a in attendance]))

    enriched = []

    for s in students:
        present_days = len([a for a in attendance if a["id"] == s["id"]])

        percentage = 0
        if total_days > 0:
            percentage = round((present_days / total_days) * 100, 2)

        enriched.append({
            "id": s["id"],
            "name": s["name"],
            "present": present_days > 0,
            "percentage": percentage,
            "image_url": s.get("image_url")
        })

    return render_template(
        "students.html",
        students=enriched,
        total=len(students),
        present=len([s for s in enriched if s["present"]]),
        absent=len([s for s in enriched if not s["present"]])
    )

@main_bp.route("/student-leaves")
def student_leaves_page():
    return render_template("student_leaves.html")


@main_bp.route("/records")
def records_page():
    return render_template(
        "records.html",
        records=load_attendance()
    )

@main_bp.route("/student-dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")





@main_bp.route("/student/<id>/attendance")
def student_attendance(id):
    from services.db_service import load_attendance, load_students

    attendance = load_attendance()
    students = load_students()

    student = next((s for s in students if s["id"] == id), None)

    total_days = len(set([a["date"] for a in attendance]))
    present_days = len([a for a in attendance if a["id"] == id])

    percentage = 0
    if total_days > 0:
        percentage = round((present_days / total_days) * 100, 2)

    return {
        "name": student["name"] if student else "Unknown",
        "percentage": percentage
    }


@main_bp.route("/admin/leaves")
def admin_leaves():
    return render_template("leave_requests.html")


"""@main_bp.route("/download-attendance")
def download_attendance():
    return send_file(ATTENDANCE_FILE, as_attachment=True)"""