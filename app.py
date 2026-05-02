import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, AdminUser
from config import config

csrf = CSRFProtect()
login_manager = LoginManager()

def create_app(config_name=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')

    cfg = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[cfg])

    # Extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # Blueprints
    from routes.shop import shop
    from routes.admin import admin as admin_bp
    app.register_blueprint(shop)
    app.register_blueprint(admin_bp)

    # Exempt admin API endpoints from CSRF (they use JSON)
    csrf.exempt(shop)  # shop uses JSON APIs with session

    # Create tables + seed admin on first run
    with app.app_context():
        db.create_all()
        _seed_admin()

    return app

def _seed_admin():
    """Create default admin if none exists."""
    from models import AdminUser
    if AdminUser.query.count() == 0:
        admin = AdminUser(username='admin', full_name='Admin', email='admin@chakkipremium.com')
        admin.set_password('chakki@2026')
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin created: admin / chakki@2026")

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)