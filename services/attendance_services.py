import base64
import numpy as np
import cv2

from services.face_service import recognize_face
from models.attendance_model import mark_attendance


def process_attendance(data):
    image_data = data.get("image")

    if not image_data:
        return {"faces": []}

    # Decode image
    encoded = image_data.split(",")[1]
    img_bytes = base64.b64decode(encoded)
    img_array = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if frame is None:
        return {"faces": []}

    names = recognize_face(frame)

    results = []
    valid_student =None

    for name in names:
        if name != "Unknown":
            valid_student == name
            break

    if valid_student :
        # 🔥 SAVE FIRST (before any crash)
        print("detected:", valid_student)
        try:
            mark_attendance(valid_student)
            print(f"[DB SUCCESS] {valid_student}")
        except Exception as e:
            print("[DB ERROR]:", e)

    for name in names:
         results.append({"name": name})
    return {"faces": results}