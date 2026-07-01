from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from database import db
from models import User, LoginLog
import re


def get_client_ip(request):
    """Get client IP address safely."""
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'Unknown'


def validate_password_strength(password):
    """Check password strength: min 8 chars, at least 1 letter and 1 number."""
    if len(password) < 8:
        return 'Password minimal 8 karakter!'
    if not re.search(r'[A-Za-z]', password):
        return 'Password harus mengandung huruf!'
    if not re.search(r'[0-9]', password):
        return 'Password harus mengandung angka!'
    return None


def is_login_blocked():
    """Check if login is blocked due to too many failed attempts."""
    attempts = session.get('login_attempts', 0)
    block_until = session.get('login_block_until', 0)
    now = datetime.utcnow().timestamp()
    
    if attempts >= 5 and now < block_until:
        remaining = int(block_until - now)
        return f'Terlalu banyak percobaan. Coba lagi dalam {remaining // 60} menit {remaining % 60} detik.'
    
    if now >= block_until:
        session['login_attempts'] = 0
        session['login_block_until'] = 0
    
    return None


def record_failed_attempt():
    """Record a failed login attempt."""
    session['login_attempts'] = session.get('login_attempts', 0) + 1
    if session['login_attempts'] >= 5:
        session['login_block_until'] = datetime.utcnow().timestamp() + 900  # 15 menit


def register_auth_routes(app):
    
    @app.route('/', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('portal'))
        
        block_msg = is_login_blocked()
            
        if request.method == 'POST':
            # CSRF check
            from security import validate_csrf_token
            validate_csrf_token()
            
            # Check if blocked
            if block_msg:
                flash(block_msg, 'error')
                return render_template('login.html')
            
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                # Success - reset attempts
                session['login_attempts'] = 0
                session['login_block_until'] = 0
                
                login_user(user)
                session.permanent = True
                
                ip_address = get_client_ip(request)
                log = LoginLog(
                    user_id=user.id,
                    login_time=datetime.utcnow(),
                    ip_address=ip_address
                )
                db.session.add(log)
                db.session.commit()
                
                session['login_log_id'] = log.id
                return redirect(url_for('portal'))
            else:
                record_failed_attempt()
                block_msg = is_login_blocked()
                if block_msg:
                    flash(block_msg, 'error')
                else:
                    flash('Username atau password salah!', 'error')
                
        return render_template('login.html')
    
    @app.route('/portal')
    @login_required
    def portal():
        from models import Application
        apps = Application.query.filter_by(is_active=True).order_by(Application.order).all()
        return render_template('portal.html', apps=apps, user=current_user)
    
    @app.route('/logout')
    @login_required
    def logout():
        log_id = session.get('login_log_id')
        if log_id:
            log = LoginLog.query.get(log_id)
            if log:
                log.logout_time = datetime.utcnow()
                db.session.commit()
        
        logout_user()
        session.clear()
        flash('Anda telah logout.', 'success')
        return redirect(url_for('login'))
    
    @app.route('/change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        if request.method == 'POST':
            from security import validate_csrf_token
            validate_csrf_token()
            
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not check_password_hash(current_user.password, current_password):
                flash('Password saat ini salah!', 'error')
                return render_template('change_password.html')
            
            pwd_error = validate_password_strength(new_password)
            if pwd_error:
                flash(pwd_error, 'error')
                return render_template('change_password.html')
            
            if new_password != confirm_password:
                flash('Konfirmasi password tidak cocok!', 'error')
                return render_template('change_password.html')
            
            if check_password_hash(current_user.password, new_password):
                flash('Password baru tidak boleh sama dengan password lama!', 'error')
                return render_template('change_password.html')
            
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            
            flash('Password berhasil diubah!', 'success')
            return redirect(url_for('portal'))
        
        return render_template('change_password.html')