from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db
from models import User, LoginLog
import time


def get_client_ip(request):
    """Get client IP address safely."""
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'Unknown'


def register_auth_routes(app):
    
    @app.route('/', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('portal'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Rate limiting: check last login attempt time
            now = time.time()
            last_attempt = session.get('last_login_attempt', 0)
            if now - last_attempt < 1:
                flash('Terlalu banyak percobaan. Silakan tunggu.', 'error')
                return render_template('login.html')
            session['last_login_attempt'] = now
            
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                login_user(user)
                session.permanent = True  # 3 hour session timeout
                
                # Log login with validated IP
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
        # Update logout time
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
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not check_password_hash(current_user.password, current_password):
                flash('Password saat ini salah!', 'error')
                return render_template('change_password.html')
            
            if len(new_password) < 6:
                flash('Password baru minimal 6 karakter!', 'error')
                return render_template('change_password.html')
            
            if new_password != confirm_password:
                flash('Konfirmasi password tidak cocok!', 'error')
                return render_template('change_password.html')
            
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            
            flash('Password berhasil diubah!', 'success')
            return redirect(url_for('portal'))
        
        return render_template('change_password.html')