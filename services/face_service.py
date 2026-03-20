import os
import base64
import numpy as np
import cv2
from deepface import DeepFace
import pickle

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
EMBEDDING_PATH = os.path.join(BASE_DIR, "trainer", "embeddings.pkl")

capture_counts = {}
CAPTURE_LIMIT = 30


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

    save_dir = os.path.join(DATASET_DIR, key)
    os.makedirs(save_dir, exist_ok=True)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face = cv2.resize(gray, (200, 200))

    capture_counts[key] += 1
    cv2.imwrite(os.path.join(save_dir, f"{capture_counts[key]}.jpg"), face)

    return {
        "count": capture_counts[key],
        "done": capture_counts[key] >= CAPTURE_LIMIT
    }


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
                    model_name="Facenet",
                    enforce_detection=False
                )

                embeddings.append(rep[0]["embedding"])
                labels.append(student_id)

            except:
                continue

    with open(EMBEDDING_PATH, "wb") as f:
        pickle.dump((embeddings, labels), f)

    return {"success": True}


def recognize_face(frame):
    if not os.path.exists(EMBEDDING_PATH):
        return []

    with open(EMBEDDING_PATH, "rb") as f:
        known_embeddings, known_ids = pickle.load(f)

    results = []

    try:
        reps = DeepFace.represent(
            img_path=frame,
            model_name="Facenet",
            enforce_detection=False
        )
    except:
        return []

    for rep in reps:
        embedding = rep["embedding"]

        distances = np.linalg.norm(
            np.array(known_embeddings) - np.array(embedding),
            axis=1
        )

        min_dist = np.min(distances)
        index = np.argmin(distances)

        if min_dist < 10:  # threshold
            results.append(known_ids[index])
        else:
            results.append("Unknown")

    return results