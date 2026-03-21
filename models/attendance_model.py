from database.db import get_connection

def mark_attendance(student_id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO attendance (student_id, date, time)
            VALUES (%s, CURRENT_DATE, CURRENT_TIME)
            ON CONFLICT (student_id, date) DO NOTHING
        """, (student_id,))
        conn.commit()
    except Exception as e:
        print("DB ERROR:", e)

    cur.close()
    conn.close()