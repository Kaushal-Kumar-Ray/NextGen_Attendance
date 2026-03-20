from database.db import get_connection

def mark_attendance(student_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO attendance (student_id, date, time)
        VALUES (%s, CURRENT_DATE, CURRENT_TIME)
    """, (student_id,))

    conn.commit()
    cur.close()
    conn.close()