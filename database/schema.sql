CREATE TABLE students (
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR,
    date DATE,
    time TIME,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE leaves (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR,
    reason TEXT,
    status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);