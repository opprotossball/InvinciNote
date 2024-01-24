from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, LoginAttempt
from . import db 
import bcrypt
from flask_login import login_user, login_required, logout_user, current_user
from .auth_validation import *
import time
import random

auth = Blueprint('auth', __name__)

def generate_password_hash(password):
    bpass = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(bpass, salt)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        time.sleep(random.uniform(1, 3))
        email = request.form.get('email')
        password = request.form.get('password')
        validation = validate_login(email, password)
        if validation.success:
            flash('Logged in successfully!', category='success')
            login_user(validation.message, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash(validation.message, category='error')
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        validation = validate_sign_up(email, username, password1, password2)
        if validation.success:
            new_user = User(email=email, first_name=username, password_hash=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
        else:
            flash(validation.message, category='error')
    return render_template("sign_up.html", user=current_user)
