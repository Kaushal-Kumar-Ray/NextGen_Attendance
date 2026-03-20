from database.db import get_connection

def add_student(student_id, name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO students (id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (student_id, name)
    )

    conn.commit()
    cur.close()
    conn.close()