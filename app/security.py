import secrets
from flask import session, request, abort

def generate_csrf_token():
    """Generate or retrieve CSRF token from session."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

def validate_csrf_token():
    """Validate CSRF token from form submission against session."""
    token = request.form.get('_csrf_token')
    if not token or token != session.get('_csrf_token'):
        abort(403)
