from database.db import get_connection

def add_student(student_id, name, image_url):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students (id, name, image_url)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, (student_id, name, image_url))

    conn.commit()
    cur.close()
    conn.close()