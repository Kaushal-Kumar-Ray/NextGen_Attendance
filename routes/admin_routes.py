from flask import Flask, render_template, request, jsonify
import os
import csv
from datetime import datetime
import cv2
import base64
import numpy as np
import pickle
from flask import send_file
import subprocess



# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
TRAINER_DIR = os.path.join(BASE_DIR, "trainer")

STUDENTS_FILE = os.path.join(BASE_DIR, "students.csv")
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance.csv")

os.makedirs(DATASET_DIR, exist_ok=True)

# ---------------- FLASK APP ----------------
app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR
)

# ---------------- FACE DETECTOR ----------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ---------------- REGISTRATION SETTINGS ----------------
CAPTURE_LIMIT = 30
capture_counts = {}   # in-memory counter per student

# ---------------- LOAD MODEL (if exists) ----------------
recognizer = None
label_map = {}

MODEL_PATH = os.path.join(TRAINER_DIR, "face_trainer.yml")
LABELS_PATH = os.path.join(TRAINER_DIR, "labels.pkl")

if os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)

    with open(LABELS_PATH, "rb") as f:
        label_map = pickle.load(f)

# ---------------- CSV HELPERS ----------------
def load_students():
    if not os.path.exists(STUDENTS_FILE):
        return []

    students = []
    with open(STUDENTS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k.lower(): v.strip() for k, v in row.items()}
            row["id"] = row["id"].strip()   # 🔥 force normalize
            folder = os.path.join(DATASET_DIR, f"{row['id']}_{row['name']}")
            if os.path.isdir(folder):
                students.append(row)
    return students


def load_attendance():
    if not os.path.exists(ATTENDANCE_FILE):
        return []

    records = []
    with open(ATTENDANCE_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue

            clean = {}
            for k, v in row.items():
                if k is None:
                    continue
                clean[k.lower()] = v.strip() if isinstance(v, str) else ""

            # skip completely empty rows
            if not any(clean.values()):
                continue

            records.append(clean)

    return records




# ================= ROUTES =================

# -------- DASHBOARD --------
@app.route("/")
def dashboard():
    students = load_students()
    attendance = load_attendance()

    today = datetime.now().strftime("%Y-%m-%d")
    present_ids = {
        a["id"] for a in attendance if a.get("date") == today
    }

    total_students = len(students)
    present_today = len(present_ids)
    absent_today = total_students - present_today

    return render_template(
        "home.html",
        title="Dashboard",
        total_students=total_students,
        present_today=present_today,
        absent_today=absent_today,
        today=today
    )

# -------- REGISTER PAGE --------
@app.route("/register")
def register():
    return render_template("register.html", title="Register Student")

# -------- FACE CAPTURE API --------
@app.route("/capture_face", methods=["POST"])
def capture_face():
    data = request.json

    student_id = data.get("id")
    student_name = data.get("name")
    image_data = data.get("image")

    if not student_id or not student_name or not image_data:
        return jsonify({"error": "Invalid data"}), 400

    key = f"{student_id}_{student_name}"

    if key not in capture_counts:
        capture_counts[key] = 0

    # Decode image
    encoded = image_data.split(",")[1]
    img_bytes = base64.b64decode(encoded)
    img_array = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"count": capture_counts[key], "done": False})

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    save_dir = os.path.join(DATASET_DIR, key)
    os.makedirs(save_dir, exist_ok=True)

    for (x, y, w, h) in faces:
        if capture_counts[key] >= CAPTURE_LIMIT:
            break

        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        capture_counts[key] += 1
        cv2.imwrite(
            os.path.join(save_dir, f"{capture_counts[key]}.jpg"),
            face
        )

    # Write student ONCE
    if capture_counts[key] == 1:
        if not os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "w") as f:
                f.write("id,name\n")

        existing = load_students()
        if not any(s["id"] == student_id for s in existing):
            with open(STUDENTS_FILE, "a") as f:
                f.write(f"{student_id},{student_name}\n")

    return jsonify({
        "count": capture_counts[key],
        "done": capture_counts[key] >= CAPTURE_LIMIT
    })
#------------------- TRAIN MODEL API --------
@app.route("/train_model", methods=["POST"])
def train_model():
    try:
        # Run train.py as a subprocess
        subprocess.run(
            ["python", os.path.join(BASE_DIR, "backend", "train.py")],
            check=True
        )

        # Reload model after training
        global recognizer, label_map

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(MODEL_PATH)

        with open(LABELS_PATH, "rb") as f:
            label_map = pickle.load(f)

        return jsonify({"success": True})

    except Exception as e:
        print("[ERROR] Training failed:", e)
        return jsonify({"success": False})





# -------- ATTENDANCE PAGE --------
@app.route("/attendance")
def attendance_page():
    return render_template("attendance.html", title="Attendance")

# -------- ATTENDANCE PROCESS API --------
@app.route("/process_attendance", methods=["POST"])
def process_attendance():
    if recognizer is None:
        return jsonify({"faces": []})

    data = request.json
    image_data = data.get("image")

    if not image_data:
        return jsonify({"faces": []})

    encoded = image_data.split(",")[1]
    img_bytes = base64.b64decode(encoded)
    img_array = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"faces": []})

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(60, 60))

    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    attendance = load_attendance()
    present_ids = {a["id"] for a in attendance if a.get("date") == today}

    results = []

    for (x, y, w, h) in faces:
        face_img = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
        label, confidence = recognizer.predict(face_img)

        name = "Unknown"
        student_id = ""

        if confidence < 70:
            student = label_map.get(label)
            if student:
                student_id = student["id"]
                name = student["name"]

                if student_id not in present_ids:
                    if not os.path.exists(ATTENDANCE_FILE):
                        with open(ATTENDANCE_FILE, "w") as f:
                            f.write("id,name,date,time\n")

                    with open(ATTENDANCE_FILE, "a") as f:
                        f.write(f"{student_id},{name},{today},{now_time}\n")

        results.append({
            "x": int(x),
            "y": int(y),
            "w": int(w),
            "h": int(h),
            "name": name
        })

    return jsonify({"faces": results})


# --------Student Records Page --------
@app.route("/students")
def students_page():
    students = load_students()
    attendance = load_attendance()

    today = datetime.now().strftime("%Y-%m-%d")

    present_ids = {
        a["id"]
        for a in attendance
        if a.get("date") == today
    }

    enriched = []
    for s in students:
        enriched.append({
            "id": s["id"],
            "name": s["name"],
            "present": s["id"] in present_ids
        })

    total = len(students)
    present = len(present_ids)
    absent = total - present

    return render_template(
        "students.html",
        title="Students",
        students=enriched,
        total=total,
        present=present,
        absent=absent
    )

@app.route("/records")
def records_page():
    records = load_attendance()
    return render_template(
        "records.html",
        title="Attendance Records",
        records=records
    )

@app.route("/download-attendance")
def download_attendance():
    if not os.path.exists(ATTENDANCE_FILE):
        return "No attendance file found", 404

    return send_file(
        ATTENDANCE_FILE,
        as_attachment=True,
        download_name="attendance.csv"
    )

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(port=3000)



