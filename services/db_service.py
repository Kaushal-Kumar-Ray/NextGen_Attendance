from database.db import get_connection

def load_students():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM students")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [{"id": r[0], "name": r[1]} for r in rows]


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