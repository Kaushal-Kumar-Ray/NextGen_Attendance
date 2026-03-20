from flask import Flask
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# 🔥 IMPORT ROUTES
from routes.main_routes import main_bp
from routes.student_routes import student_bp
from routes.attendance_routes import attendance_bp

app.register_blueprint(main_bp)
app.register_blueprint(student_bp)
app.register_blueprint(attendance_bp)

if __name__ == "__main__":
    app.run(port=3000, debug=True)