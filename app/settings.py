from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from i18n import build_translator


def register_settings_routes(app):

    @app.route('/settings', methods=['GET', 'POST'])
    @login_required
    def settings():
        lang = current_user.language or 'id'
        t = build_translator(lang)

        if request.method == 'POST':
            action = request.form.get('action')

            # Change full name
            if action == 'update_name':
                new_name = request.form.get('full_name', '').strip()
                if not new_name:
                    flash(t('settings_name_empty'), 'error')
                else:
                    current_user.full_name = new_name
                    db.session.commit()
                    flash(t('settings_name_updated'), 'success')
                return redirect(url_for('settings'))

            # Change password
            if action == 'update_password':
                current_pwd = request.form.get('current_password')
                new_pwd = request.form.get('new_password')
                confirm_pwd = request.form.get('confirm_password')

                if not check_password_hash(current_user.password, current_pwd):
                    flash(t('settings_password_wrong'), 'error')
                elif len(new_pwd) < 6:
                    flash(t('settings_password_short'), 'error')
                elif new_pwd != confirm_pwd:
                    flash(t('settings_password_mismatch'), 'error')
                else:
                    current_user.password = generate_password_hash(new_pwd)
                    db.session.commit()
                    flash(t('settings_password_updated'), 'success')
                return redirect(url_for('settings'))

            # Change language
            if action == 'update_language':
                lang = request.form.get('language', 'id')
                if lang in ('id', 'en'):
                    current_user.language = lang
                    db.session.commit()
                    flash(t('settings_language_updated'), 'success')
                return redirect(url_for('settings'))

        return render_template('settings.html')
