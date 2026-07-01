from flask import Flask, session, request, abort
from flask_login import current_user
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise RuntimeError('SECRET_KEY environment variable is required')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_DEBUG', '0') != '1'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=3)
app.config['ALLOWED_HOSTS'] = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# CSRF token injection for all templates
from security import generate_csrf_token
@app.context_processor
def inject_csrf():
    return dict(csrf_token=generate_csrf_token())

# Host header validation
@app.before_request
def validate_host():
    host = request.headers.get('Host', '').split(':')[0]
    allowed = app.config['ALLOWED_HOSTS']
    if host and host not in allowed and host != 'localhost' and not host.startswith('192.168.') and not host.startswith('10.'):
        abort(403)

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

# Initialize database
from database import db, login_manager, init_db
init_db(app)

# Import models for database creation
from models import User, LoginLog, Application

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# i18n context processor
from i18n import build_translator
@app.context_processor
def inject_i18n():
    if current_user.is_authenticated:
        lang = current_user.language or 'id'
    else:
        lang = 'id'
    _ = build_translator(lang)
    return dict(_=_)

# Register routes
from auth import register_auth_routes
from admin import register_admin_routes
from settings import register_settings_routes

register_auth_routes(app)
register_admin_routes(app)
register_settings_routes(app)

# Auto-logout when session expires
@app.before_request
def check_session_timeout():
    if current_user.is_authenticated and not session.get('_session_checked'):
        session['_session_checked'] = True

# Create database tables and seed default admin
with app.app_context():
    db.create_all()
    
    # Auto-migrate: add missing columns for existing tables
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('users')]
    if 'language' not in columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR(5) DEFAULT 'id'"))
        db.session.commit()
        print("Migration: added column 'language' to users table")
    
    # Create default admin only if no users exist
    if User.query.count() == 0:
        from werkzeug.security import generate_password_hash
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        admin = User(
            full_name='Administrator',
            username='admin',
            password=generate_password_hash(admin_password),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Default admin created: username=admin, password={admin_password}")
        print("WARNING: Change the default admin password immediately after first login!")

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    port = int(os.getenv('FLASK_PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)