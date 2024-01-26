from .. import db
from flask_login import UserMixin
import pyotp
from flask import current_app

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(150))
    username = db.Column(db.String(150))
    totp_enabled = db.Column(db.Boolean, nullable=False, default=False)
    totp_secret = db.Column(db.String, unique=True)
    notes = db.relationship('Note')
    encrypted_notes = db.relationship('EncryptedNote')

    def __init__(self, email, username, password_hash):
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.totp_secret = pyotp.random_base32()

    def get_authentication_setup_uri(self):
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.username, issuer_name=current_app.config['APP_NAME'])

    def is_otp_valid(self, user_otp):
        totp = pyotp.parse_uri(self.get_authentication_setup_uri())
        return totp.verify(user_otp)