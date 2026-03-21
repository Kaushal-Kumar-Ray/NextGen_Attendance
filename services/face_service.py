import os
import base64
import numpy as np
import cv2
from deepface import DeepFace
import pickle
import time
import gc

# 🔥 Reduce TensorFlow logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from models.student_model import add_student

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
EMBEDDING_PATH = os.path.join(BASE_DIR, "trainer", "embeddings.pkl")

os.makedirs(DATASET_DIR, exist_ok=True)

capture_counts = {}
saved_students = set()
CAPTURE_LIMIT = 30

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# 🔥 LOAD EMBEDDINGS ONCE (IMPORTANT)
if os.path.exists(EMBEDDING_PATH):
    with open(EMBEDDING_PATH, "rb") as f:
        known_embeddings, known_ids = pickle.load(f)
else:
    known_embeddings, known_ids = [], []


# ================= CAPTURE =================
def capture_face(data):
    student_id = data.get("id")
    student_name = data.get("name")
    image_data = data.get("image")

    if not student_id or not student_name or not image_data:
        return {"error": "Invalid data"}, 400

    key = f"{student_id}_{student_name}"

    if key not in capture_counts:
        capture_counts[key] = 0

    encoded = image_data.split(",")[1]
    img_bytes = base64.b64decode(encoded)
    img_array = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if frame is None:
        return {"count": capture_counts[key], "done": False}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    save_dir = os.path.join(DATASET_DIR, key)
    os.makedirs(save_dir, exist_ok=True)

    for (x, y, w, h) in faces[:1]:  # 🔥 limit to 1 face
        if capture_counts[key] >= CAPTURE_LIMIT:
            break

        face = frame[y:y+h, x:x+w]
        face = cv2.resize(face, (160, 160))

        capture_counts[key] += 1

        cv2.imwrite(
            os.path.join(save_dir, f"{capture_counts[key]}.jpg"),
            face
        )

    done = capture_counts[key] >= CAPTURE_LIMIT

    if done and key not in saved_students:
        try:
            add_student(student_id, student_name)
            saved_students.add(key)
            print(f"[DB] Student saved: {student_id}")
        except Exception as e:
            print("[ERROR] Student DB:", e)

    return {
        "count": capture_counts[key],
        "done": done
    }


# ================= TRAIN =================
def generate_embeddings():
    embeddings = []
    labels = []

    for folder in os.listdir(DATASET_DIR):
        folder_path = os.path.join(DATASET_DIR, folder)
        student_id = folder.split("_")[0]

        for img_name in os.listdir(folder_path):
            path = os.path.join(folder_path, img_name)

            try:
                rep = DeepFace.represent(
                    img_path=path,
                    model_name="ArcFace",
                    detector_backend="opencv",
                    enforce_detection=False
                )

                embeddings.append(rep[0]["embedding"])
                labels.append(student_id)

            except Exception as e:
                print("Training error:", e)

    with open(EMBEDDING_PATH, "wb") as f:
        pickle.dump((embeddings, labels), f)

    global known_embeddings, known_ids
    known_embeddings, known_ids = embeddings, labels
    return {"success": True}


# ================= RECOGNITION =================
def recognize_face(frame):
    global known_embeddings, known_ids

    if len(known_embeddings) == 0:
        return []

    results = []

    faces = face_cascade.detectMultiScale(frame, 1.2, 5)

    for (x, y, w, h) in faces[:1]:
        face_img = frame[y:y+h, x:x+w]

        try:
            rep = DeepFace.represent(
                img_path=face_img,
                model_name="ArcFace",
                detector_backend="opencv",
                enforce_detection=False
            )

            face_vector = np.array(rep[0]["embedding"])

        except Exception as e:
            print("Embedding error:", e)
            results.append("Unknown")
            continue

        distances = [
            np.linalg.norm(np.array(emb) - face_vector)
            for emb in known_embeddings
        ]

        if len(distances) == 0:
            results.append("Unknown")
            continue

        min_dist = min(distances)
        index = distances.index(min_dist)

        print("Distance:", min_dist)

        if min_dist < 3.0:  # 🔥 tuned threshold
            results.append(known_ids[index])
        else:
            results.append("Unknown")

    return results