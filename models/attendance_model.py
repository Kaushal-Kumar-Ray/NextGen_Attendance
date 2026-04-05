from datetime import datetime
from database.db import get_connection

def mark_attendance(student_id):
    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    cur.execute("""
        INSERT INTO attendance (student_id, date, time)
        VALUES (%s, %s, %s)
        ON CONFLICT (student_id, date) DO NOTHING
    """, (student_id, date, time))

    conn.commit()
    cur.close()
    conn.close()