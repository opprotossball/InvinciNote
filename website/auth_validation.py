from datetime import datetime, timedelta
import re
from . import db 
from .action_result import ActionResult
from .models import User, LoginAttempt
import bcrypt

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
    user = User.query.filter_by(email=email).first()
    # validate email
    if user:
        return ActionResult(False, 'User with this email already exists.') 
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

def validate_login(email, password):
    #validate email
    user = User.query.filter_by(email=email).first()
    if not (user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash)):
        return ActionResult(False, 'Invalid email or password.')
    else:
        return ActionResult(True, user)