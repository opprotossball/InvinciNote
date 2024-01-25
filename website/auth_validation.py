from datetime import datetime, timedelta
import re
from . import db 
from .action_result import ActionResult
from .models.user import User
from .models.login_attempt import LoginAttempt
import bcrypt
from flask import current_app
import os

def password_check(password):
    short_error = len(password) < 8
    long_error = len(password) > 64
    digit_error = re.search(r"\d", password) is None
    uppercase_error = re.search(r"[A-Z]", password) is None
    lowercase_error = re.search(r"[a-z]", password) is None
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None
    password_ok = not(short_error or long_error or digit_error or uppercase_error or lowercase_error or symbol_error)
    return {
        'password_ok': password_ok,
        'short_error': short_error,
        'long_error': long_error,
        'digit_error': digit_error,
        'uppercase_error': uppercase_error,
        'lowercase_error': lowercase_error,
        'symbol_error': symbol_error,
    }

def validate_sign_up(email, username, password1, password2):
    if not validate_email(email):
        return ActionResult(False, 'Enter valid email.')
    if not validate_username(username):
        return ActionResult(False, 'Username can contain up to 32 alphanumeric characters and underscores.')
    user = User.query.filter_by(email=email).first()
    if user:
        return ActionResult(False, 'User with this email already exists.') 
    return validate_passwords(password1, password2)

def validate_passwords(password1, password2):
    if not password1 or not password2:
        return ActionResult(False, 'Passwords cannot be empty.')
    if password1 != password2:
        return ActionResult(False, 'Passwords don\'t match.')
    check = password_check(password1)
    if check['password_ok']:
        return ActionResult(True, 'ok')
    if check['short_error']:
        return ActionResult(False, 'Password must be at least 8 characters long.')
    if check['long_error']:
        return ActionResult(False, 'Password must not exceed 64 characters.')
    if check['digit_error']:
        return ActionResult(False, 'Password must contain at least one digit.')
    if check['uppercase_error']:
        return ActionResult(False, 'Password must contain at least one uppercase letter.')
    if check['lowercase_error']:
        return ActionResult(False, 'Password must contain at least one lowercase letter.')
    if check['symbol_error']:
        return ActionResult(False, 'Password must contain at least one special character.')
    else:
        return ActionResult(False, 'Password is too weak.')

def check_login_block(user_id):
    time_mins = 10
    failed_attempts = 5
    time_ago = datetime.utcnow() - timedelta(minutes=time_mins)
    recent_attempts = (
        db.session.query(LoginAttempt)
        .filter(
            LoginAttempt.user_id == user_id,
            LoginAttempt.date >= time_ago,
            LoginAttempt.success == False
        )
        .limit(failed_attempts) 
        .all()
    )
    return len(recent_attempts) >= failed_attempts

def check_password(password, password_hash):
    pepper = os.environ[current_app.config['PEPPER_ENV']]
    bytes = (password + pepper).encode('utf-8')
    return bcrypt.checkpw(bytes, password_hash)

def validate_login(email, password):
    if not validate_email(email):
        return ActionResult(False, 'Enter valid email')
    user = User.query.filter_by(email=email).first()
    if not (user and check_password(password, user.password_hash)):
        return ActionResult(False, 'Invalid email or password.')
    else:
        return ActionResult(True, user)
    
def generate_password_hash(password):
    pepper = os.environ[current_app.config['PEPPER_ENV']]
    bytes = (password + pepper).encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(bytes, salt)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def validate_username(username):
    pattern = r'^[a-zA-Z0-9_ąćęłńóśźżĄĆĘŁŃÓŚŹŻ ]{1,32}$'
    return re.match(pattern, username) is not None
