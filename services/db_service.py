from database.db import get_connection


from database.db import get_connection

def load_students():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            s.id, 
            s.name, 
            s.image_url,
            COUNT(a.id) AS present_count,
            MAX(a.date) AS last_attendance_date
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        GROUP BY s.id
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    students = []

    for r in rows:
        students.append({
            "id": r[0],
            "name": r[1],
            "image_url": r[2],
            "present": r[3] if r[3] else 0,
            "last_attendance_date": str(r[4]) if r[4] else None
        })

    return students

def load_attendance():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.id, s.name, a.date, a.time
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "name": r[1],
            "date": str(r[2]),
            "time": str(r[3])
        }
        for r in rows
    ]