import os
from flask import Flask

from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import Admin

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.imports import imports_bp
    from app.routes.halls import halls_bp
    from app.routes.exams import exams_bp
    from app.routes.allocation import allocation_bp
    from app.routes.seating import seating_bp
    from app.routes.search import search_bp
    from app.routes.export import export_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(imports_bp)
    app.register_blueprint(halls_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(allocation_bp)
    app.register_blueprint(seating_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(export_bp)

    @app.errorhandler(413)
    def too_large(e):
        return "File too large. Maximum upload size is 10 MB.", 413

    with app.app_context():
        db.create_all()
        _ensure_default_admin()

    return app


def _ensure_default_admin():
    """Convenience for local demo/eval only: seeds one admin login if none exist."""
    from app.models import Admin

    if Admin.query.count() == 0:
        admin = Admin(username="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
