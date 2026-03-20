from flask import Blueprint, request, jsonify
from services.attendance_services import process_attendance

attendance_bp = Blueprint("attendance", __name__)

@attendance_bp.route("/process_attendance", methods=["POST"])
def process():
    return process_attendance(request.json)