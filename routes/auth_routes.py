from flask import Blueprint, request, jsonify
from services.db_service import load_students

auth_bp = Blueprint("auth", __name__)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "000"

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    username = data.get("id")        # 🔥 frontend still sends "id"
    password = data.get("password")
    role = data.get("role")

    # ================= ADMIN LOGIN =================
    if role == "admin":
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return jsonify({
                "success": True,
                "role": "admin"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Invalid admin login"
            })

    # ================= STUDENT LOGIN =================
    if role == "student":
        students = load_students()

        for s in students:
            # 🔥 NEW LOGIC
            if (
                s["name"].lower() == username.lower() and
                str(s["id"]) == str(password)
            ):
                return jsonify({
                    "success": True,
                    "role": "student",
                    "id": s["id"],
                    "name": s["name"]
                })

        return jsonify({
            "success": False,
            "message": "Invalid student login"
        })