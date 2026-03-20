import csv
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STUDENTS_FILE = os.path.join(BASE_DIR, "students.csv")
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance.csv")
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

def load_students():
    if not os.path.exists(STUDENTS_FILE):
        return []

    students = []
    with open(STUDENTS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k.lower(): v.strip() for k, v in row.items()}
            folder = os.path.join(DATASET_DIR, f"{row['id']}_{row['name']}")
            if os.path.isdir(folder):
                students.append(row)
    return students

def load_attendance():
    if not os.path.exists(ATTENDANCE_FILE):
        return []

    with open(ATTENDANCE_FILE, newline="") as f:
        return list(csv.DictReader(f))