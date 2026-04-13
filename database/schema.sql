CREATE TABLE if not exists  students (
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE if not exists attendance (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR,
    date DATE,
    time TIME,
    UNIQUE(student_id, date), -- 🔥 prevents duplicate attendance
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE  if not exists leaves (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR,
    reason TEXT,
    status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE  if not exists admin_otp (
    id SERIAL PRIMARY KEY,
    email VARCHAR,
    otp VARCHAR,
    expires_at TIMESTAMP
);

