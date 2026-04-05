<<<<<<< HEAD
CREATE TABLE students (
=======
CREATE TABLE if not exists  students (
>>>>>>> 1d7e363635bb8865ba8c25daa9b5b3126823fbbf
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

<<<<<<< HEAD
CREATE TABLE attendance (
=======
CREATE TABLE if not exists attendance (
>>>>>>> 1d7e363635bb8865ba8c25daa9b5b3126823fbbf
    id SERIAL PRIMARY KEY,
    student_id VARCHAR,
    date DATE,
    time TIME,
    UNIQUE(student_id, date), -- 🔥 prevents duplicate attendance
    FOREIGN KEY (student_id) REFERENCES students(id)
);

<<<<<<< HEAD
CREATE TABLE leaves (
=======
CREATE TABLE  if not exists leaves (
>>>>>>> 1d7e363635bb8865ba8c25daa9b5b3126823fbbf
    id SERIAL PRIMARY KEY,
    student_id VARCHAR,
    reason TEXT,
    status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
<<<<<<< HEAD
=======
);

CREATE TABLE  if not exists admin_otp (
    id SERIAL PRIMARY KEY,
    email VARCHAR,
    otp VARCHAR,
    expires_at TIMESTAMP
>>>>>>> 1d7e363635bb8865ba8c25daa9b5b3126823fbbf
);