from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
from database import db
from models import User, Application
from i18n import build_translator


def _admin_required():
    """Check if current user is admin, return error response if not."""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return None


def _normalize_url(url):
    """Ensure URL has a proper scheme, default to https if missing."""
    url = url.strip()
    if not url.startswith(('http://', 'https://', '//')):
        url = 'https://' + url
    return url


def register_admin_routes(app):
    
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            flash('Akses ditolak!', 'error')
            return redirect(url_for('portal'))
            
        users = User.query.all()
        apps = Application.query.order_by(Application.order).all()
        return render_template('admin.html', users=users, apps=apps)
    
    @app.route('/admin/apps', methods=['POST'])
    @login_required
    def admin_add_app():
        err = _admin_required()
        if err:
            return err
            
        data = request.json
        app = Application(
            name=data.get('name'),
            description=data.get('description'),
            url=_normalize_url(data.get('url', '')),
            icon=data.get('icon', 'fa-apple'),
            order=data.get('order', 0)
        )
        db.session.add(app)
        db.session.commit()
        
        return jsonify({'message': 'Aplikasi berhasil ditambahkan'}), 201
    
    @app.route('/admin/apps/<int:app_id>', methods=['PUT'])
    @login_required
    def admin_update_app(app_id):
        err = _admin_required()
        if err:
            return err
            
        app = Application.query.get_or_404(app_id)
        data = request.json
        
        app.name = data.get('name', app.name)
        app.description = data.get('description', app.description)
        app.url = _normalize_url(data.get('url', app.url))
        app.icon = data.get('icon', app.icon)
        app.order = data.get('order', app.order)
        app.is_active = data.get('is_active', app.is_active)
        app.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Aplikasi berhasil diupdate'}), 200
    
    @app.route('/admin/apps/<int:app_id>', methods=['DELETE'])
    @login_required
    def admin_delete_app(app_id):
        err = _admin_required()
        if err:
            return err
            
        app = Application.query.get_or_404(app_id)
        db.session.delete(app)
        db.session.commit()
        
        return jsonify({'message': 'Aplikasi berhasil dihapus'}), 200
    
    @app.route('/admin/users', methods=['POST'])
    @login_required
    def admin_add_user():
        err = _admin_required()
        if err:
            return err
            
        data = request.json
        
        # Check username uniqueness
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        user = User(
            full_name=data.get('full_name'),
            username=data.get('username'),
            password=generate_password_hash(data.get('password')),
            role=data.get('role', 'user'),
            language=data.get('language', 'id')
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User berhasil ditambahkan'}), 201
    
    @app.route('/admin/users/<int:user_id>', methods=['PUT'])
    @login_required
    def admin_update_user(user_id):
        err = _admin_required()
        if err:
            return err
        
        t = build_translator(current_user.language or 'id')
        user = User.query.get_or_404(user_id)
        data = request.json
        
        # Check username uniqueness if changed
        new_username = data.get('username', user.username)
        if new_username != user.username and User.query.filter_by(username=new_username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        user.full_name = data.get('full_name', user.full_name)
        user.username = new_username
        user.role = data.get('role', user.role)
        user.language = data.get('language', user.language)
        
        # Reset password if provided
        if data.get('password'):
            user.password = generate_password_hash(data['password'])
        
        db.session.commit()
        return jsonify({'message': 'User berhasil diupdate'}), 200
    
    @app.route('/admin/users/<int:user_id>/reset-password', methods=['PUT'])
    @login_required
    def admin_reset_user_password(user_id):
        err = _admin_required()
        if err:
            return err
        
        user = User.query.get_or_404(user_id)
        data = request.json
        new_password = data.get('password', 'user123')
        
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({'message': f'Password berhasil direset menjadi {new_password}'}), 200
    
    @app.route('/admin/users/<int:user_id>', methods=['DELETE'])
    @login_required
    def admin_delete_user(user_id):
        err = _admin_required()
        if err:
            return err
        
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting yourself
        if user.id == current_user.id:
            return jsonify({'error': 'Tidak bisa menghapus akun sendiri'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User berhasil dihapus'}), 200
    
    @app.route('/admin/logs')
    @login_required
    def admin_logs():
        if current_user.role != 'admin':
            flash('Akses ditolak!', 'error')
            return redirect(url_for('portal'))
        
        from models import LoginLog
        page = request.args.get('page', 1, type=int)
        logs = LoginLog.query.order_by(LoginLog.login_time.desc()).paginate(page=page, per_page=20, error_out=False)
        return render_template('admin_logs.html', logs=logs)