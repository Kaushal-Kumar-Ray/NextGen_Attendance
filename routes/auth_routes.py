<<<<<<< HEAD
from flask import Blueprint, request, jsonify
from services.db_service import load_students

auth_bp = Blueprint("auth", __name__)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "000"
=======
from flask import Blueprint, request, jsonify, session
from services.db_service import load_students
from database.db import get_connection

import os
import random
from datetime import datetime, timedelta

from services.email_service import send_email_otp

auth_bp = Blueprint("auth", __name__)

# ================= ADMIN CONFIG =================
ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")


# ================= ADMIN: SEND OTP =================
@auth_bp.route("/admin/send-otp", methods=["POST"])
def send_otp():
    data = request.json

    admin_id = data.get("id")
    email = data.get("email")

    # 🔐 Validate admin
    if admin_id != ADMIN_ID or email != ADMIN_EMAIL:
        return jsonify({
            "success": False,
            "message": "Invalid admin credentials"
        })

    otp = str(random.randint(100000, 999999))
    expires_at = datetime.now() + timedelta(minutes=5)

    conn = get_connection()
    cur = conn.cursor()

    # Remove old OTP
    cur.execute("DELETE FROM admin_otp WHERE email = %s", (email,))

    # Save new OTP
    cur.execute(
        "INSERT INTO admin_otp (email, otp, expires_at) VALUES (%s, %s, %s)",
        (email, otp, expires_at)
    )

    conn.commit()
    cur.close()
    conn.close()

    # 📧 Send OTP via Brevo
    sent = send_email_otp(email, otp)

    if not sent:
        return jsonify({
            "success": False,
            "message": "Failed to send OTP"
        })

    return jsonify({
        "success": True,
        "message": "OTP sent"
    })


# ================= ADMIN: VERIFY OTP =================
@auth_bp.route("/admin/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json

    email = data.get("email")
    otp = data.get("otp")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT otp, expires_at FROM admin_otp WHERE email = %s",
        (email,)
    )

    row = cur.fetchone()

    if not row:
        return jsonify({
            "success": False,
            "message": "No OTP found"
        })

    stored_otp, expires_at = row

    # ⏱ Expiry check
    if datetime.now() > expires_at:
        return jsonify({
            "success": False,
            "message": "OTP expired"
        })

    # ❌ Wrong OTP
    if otp != stored_otp:
        return jsonify({
            "success": False,
            "message": "Invalid OTP"
        })

    # ✅ LOGIN SUCCESS
    session["role"] = "admin"
    session["user"] = email

    # Delete OTP after use
    cur.execute("DELETE FROM admin_otp WHERE email = %s", (email,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "success": True,
        "role": "admin"
    })


# ================= STUDENT LOGIN =================
>>>>>>> 1d7e363635bb8865ba8c25daa9b5b3126823fbbf

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

<<<<<<< HEAD
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
=======
    username = data.get("id")
    password = data.get("password")
    role = data.get("role")

>>>>>>> 1d7e363635bb8865ba8c25daa9b5b3126823fbbf
    if role == "student":
        students = load_students()

        for s in students:
<<<<<<< HEAD
            # 🔥 NEW LOGIC
=======
>>>>>>> 1d7e363635bb8865ba8c25daa9b5b3126823fbbf
            if (
                s["name"].lower() == username.lower() and
                str(s["id"]) == str(password)
            ):
<<<<<<< HEAD
=======
                # ✅ SET SESSION ONLY AFTER SUCCESS
                session["role"] = "student"
                session["user"] = s["id"]

>>>>>>> 1d7e363635bb8865ba8c25daa9b5b3126823fbbf
                return jsonify({
                    "success": True,
                    "role": "student",
                    "id": s["id"],
                    "name": s["name"]
                })

        return jsonify({
            "success": False,
            "message": "Invalid student login"
<<<<<<< HEAD
        })
=======
        })

    return jsonify({
        "success": False,
        "message": "Invalid role"
    })


# ================= LOGOUT =================
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()  # 🔥 clears admin/student session
    return {"success": True}
>>>>>>> 1d7e363635bb8865ba8c25daa9b5b3126823fbbf
