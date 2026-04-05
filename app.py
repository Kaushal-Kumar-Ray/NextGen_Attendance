from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)

app.secret_key = "super-secret-key"

from routes.main_routes import main_bp
from routes.student_routes import student_bp
from routes.attendance_routes import attendance_bp
from routes.leave_routes import leave_bp
from routes.auth_routes import auth_bp


app.register_blueprint(main_bp)
app.register_blueprint(student_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(leave_bp)
app.register_blueprint(auth_bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
    