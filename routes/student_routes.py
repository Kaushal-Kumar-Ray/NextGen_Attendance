from flask import Blueprint, request, jsonify
from services.face_service import capture_face
from services.training_services import train_model

student_bp = Blueprint("student", __name__)

@student_bp.route("/capture_face", methods=["POST"])
def capture():
    return capture_face(request.json)

@student_bp.route("/train_model", methods=["POST"])
def train():
    return train_model()