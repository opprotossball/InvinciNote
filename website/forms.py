from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired

class TwoFactorForm(FlaskForm):
    otp = StringField('Enter your code', validators=[InputRequired(), Length(min=6, max=6)])