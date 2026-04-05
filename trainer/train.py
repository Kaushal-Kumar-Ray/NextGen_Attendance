import cv2
import os
import numpy as np
import pickle

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATASET_DIR = os.path.join(BASE_DIR, "dataset")
TRAINER_DIR = os.path.join(BASE_DIR, "trainer")

MODEL_PATH = os.path.join(TRAINER_DIR, "face_trainer.yml")
LABELS_PATH = os.path.join(TRAINER_DIR, "labels.pkl")

os.makedirs(TRAINER_DIR, exist_ok=True)

# ---------------- FACE RECOGNIZER ----------------
recognizer = cv2.face.LBPHFaceRecognizer_create(
    radius=1,
    neighbors=8,
    grid_x=8,
    grid_y=8
)

faces = []
labels = []
label_map = {}
label_id = 0

print("[INFO] Training started...")

# IMPORTANT: sorted for consistent label mapping
for folder in sorted(os.listdir(DATASET_DIR)):
    folder_path = os.path.join(DATASET_DIR, folder)

    if not os.path.isdir(folder_path):
        continue

    # folder format: ID_Name
    try:
        student_id, student_name = folder.split("_", 1)
    except ValueError:
        print(f"[WARN] Skipping invalid folder: {folder}")
        continue

    label_map[label_id] = {
        "id": student_id.strip(),
        "name": student_name.strip()
    }

    for img_name in os.listdir(folder_path):
        img_path = os.path.join(folder_path, img_name)

        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        img = cv2.resize(img, (200, 200))
        faces.append(img)
        labels.append(label_id)

    label_id += 1

# ---------------- SAFETY CHECK ----------------
if not faces:
    raise RuntimeError("No images found in dataset! Cannot train model.")

# ---------------- TRAIN & SAVE ----------------
recognizer.train(faces, np.array(labels))
recognizer.save(MODEL_PATH)

with open(LABELS_PATH, "wb") as f:
    pickle.dump(label_map, f)

print("[SUCCESS] Training completed")
print("[INFO] Students trained:", label_id)
print("[INFO] Model saved at:", MODEL_PATH)
