import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cv2
import numpy as np
from sklearn.metrics import accuracy_score, classification_report

from services.face_service import recognize_face

TEST_DIR = "dataset/test"

y_true = []
y_pred = []

for person in os.listdir(TEST_DIR):
    person_path = os.path.join(TEST_DIR, person)

    for img_name in os.listdir(person_path):
        img_path = os.path.join(person_path, img_name)

        img = cv2.imread(img_path)

        result = recognize_face(img)  # should return name

        predicted = result if result else "Unknown"

        y_true.append(person)
        y_pred.append(predicted)

# 📊 METRICS
print("Accuracy:", accuracy_score(y_true, y_pred))
print("\nReport:\n", classification_report(y_true, y_pred))

# run : python evaluate_model.py