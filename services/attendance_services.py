import base64
import numpy as np
import cv2
from datetime import datetime
import os
from services.face_service import recognize_face
from services.csv_service import load_attendance

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance.csv")


def process_attendance(data):
    image_data = data.get("image")

    if not image_data:
        return {"faces": []}

    encoded = image_data.split(",")[1]
    img_bytes = base64.b64decode(encoded)
    img_array = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    names = recognize_face(frame)

    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    attendance = load_attendance()
    present_ids = {a["id"] for a in attendance if a.get("date") == today}

    results = []

    for name in names:
        student_id = name

        if student_id != "Unknown" and student_id not in present_ids:
            if not os.path.exists(ATTENDANCE_FILE):
                with open(ATTENDANCE_FILE, "w") as f:
                    f.write("id,date,time\n")

            with open(ATTENDANCE_FILE, "a") as f:
                f.write(f"{student_id},{today},{now_time}\n")

        results.append({"name": student_id})

    return {"faces": results}