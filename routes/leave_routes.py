from flask import Blueprint, request, jsonify
from database.db import get_connection
from services.db_service import load_attendance

# 🔥 Blueprint
leave_bp = Blueprint("leave", __name__)


# ================= APPLY LEAVE =================
@leave_bp.route("/apply-leave", methods=["POST"])
def apply_leave():
    data = request.json

    student_id = data.get("student_id")
    reason = data.get("reason")

    if not student_id or not reason:
        return jsonify({"message": "Invalid data"}), 400

    # 📊 Calculate attendance %
    attendance = load_attendance()

    total_days = len(set([a["date"] for a in attendance]))
    present_days = len([a for a in attendance if a["id"] == student_id])

    percentage = 0
    if total_days > 0:
        percentage = (present_days / total_days) * 100

    # 🧠 Smart rule
    status = "approved" if percentage >= 80 else "pending"

    # 💾 Save to DB
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO leaves (student_id, reason, status) VALUES (%s, %s, %s)",
        (student_id, reason, status)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": f"Leave {status}",
        "status": status
    })


# ================= GET ALL LEAVES =================
@leave_bp.route("/leaves", methods=["GET"])
def get_leaves():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT l.id, s.name, s.id, l.reason, l.status, l.created_at
        FROM leaves l
        JOIN students s ON l.student_id = s.id
        ORDER BY l.created_at DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    leaves = []
    for r in rows:
        leaves.append({
            "id": r[0],
            "name": r[1],
            "student_id": r[2],
            "reason": r[3],
            "status": r[4],
            "created_at": str(r[5])
        })

    return jsonify(leaves)


# ================= APPROVE LEAVE =================
@leave_bp.route("/approve-leave", methods=["POST"])
def approve_leave():
    data = request.json
    leave_id = data.get("leave_id")

    if not leave_id:
        return jsonify({"message": "Invalid request"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE leaves SET status = 'approved' WHERE id = %s",
        (leave_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Leave approved"})


# ================= REJECT LEAVE =================
@leave_bp.route("/reject-leave", methods=["POST"])
def reject_leave():
    data = request.json
    leave_id = data.get("leave_id")

    if not leave_id:
        return jsonify({"message": "Invalid request"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE leaves SET status = 'rejected' WHERE id = %s",
        (leave_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Leave rejected"})



@leave_bp.route("/student-leaves/<student_id>", methods=["GET"])
def student_leaves(student_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT reason, status, created_at
        FROM leaves
        WHERE student_id = %s
        ORDER BY created_at DESC
    """, (student_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    leaves = []
    for r in rows:
        leaves.append({
            "reason": r[0],
            "status": r[1],
            "created_at": str(r[2])
        })

    return jsonify(leaves)