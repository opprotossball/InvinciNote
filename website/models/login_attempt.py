from .. import db
from sqlalchemy.sql import func

class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    success = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))