from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models.user import UserMixin
from .models.login_attempt import LoginAttempt
from . import db 
import bcrypt
from flask_login import login_user, login_required, logout_user, current_user
from .auth_validation import *
import time
import random
from .utils import get_b64encoded_qr
from .forms import TwoFactorForm

auth = Blueprint('auth', __name__)

enable_2fa = 'You have not enabled 2-Factor Authentication. Please enable first to login.'

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.totp_enabled:
            flash('You are already logged in.', 'info')
            return redirect(url_for('views.home'))
        else:
            flash(enable_2fa, 'info')
            return redirect(url_for('auth.totp_setup'))
    if request.method == 'POST':
        time.sleep(random.uniform(1, 3))
        email = request.form.get('email')
        password = request.form.get('password')
        validation = validate_login(email, password)
        if validation.success:
            login_user(validation.message, remember=True)
            if not current_user.totp_enabled:
                flash(enable_2fa, 'info')
                return redirect(url_for('auth.totp_setup'))
            return redirect(url_for('auth.totp'))
        else:
            flash(validation.message, category='error')
    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        if current_user.totp_enabled:
            flash('You are already registered.', 'info')
            return redirect(url_for('views.home'))
        else:
            flash(enable_2fa, 'info')
            return redirect(url_for('auth.totp_setup'))
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        validation = validate_sign_up(email, username, password1, password2)
        if validation.success:
            new_user = User(email=email, username=username, password_hash=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created! Now enable 2-Factor Authentication.', category='success')
            return redirect(url_for('auth.totp_setup'))
        else:
            flash(validation.message, category='error')
    return render_template('sign_up.html', user=current_user)

@auth.route('/setup-2fa')
@login_required
def totp_setup():
    secret = current_user.totp_secret
    uri = current_user.get_authentication_setup_uri()
    base64_qr_image = get_b64encoded_qr(uri)
    return render_template('totp_setup.html', secret=secret, qr_image=base64_qr_image, user=current_user)

@auth.route('/verify-2fa', methods=['GET', 'POST'])
@login_required
def totp():
    form = TwoFactorForm(request.form)
    if form.validate_on_submit():
        if current_user.is_otp_valid(form.otp.data):
            if current_user.totp_enabled:
                flash('2FA verification successful. You are logged in!', 'success')
                return redirect(url_for('views.home'))
            else:
                try:
                    current_user.totp_enabled = True
                    db.session.commit()
                    flash('2FA setup successful. You are logged in!', 'success')
                    return redirect(url_for('views.home'))
                except Exception:
                    db.session.rollback()
                    flash('2FA setup failed. Please try again.', 'error')
                    return redirect(url_for('auth.totp'))
        else:
            flash('Invalid code. Please try again.', 'error')
            return redirect(url_for('auth.totp'))
    else:
        if not current_user.totp_enabled:
            flash(enable_2fa, 'info')
        return render_template('totp.html', form=form, user=current_user)
