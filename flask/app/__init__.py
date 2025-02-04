from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
DB_NAME = "database.db"

app = Flask(__name__)
app.config['APP_NAME'] = 'InvinciNote'
app.config['APP_SECRET_ENV'] = 'invictinoteAppSecret'
app.config['PEPPER_ENV'] = 'invincinotePepper' 
app.config['SECRET_KEY'] = os.environ[app.config['APP_SECRET_ENV']]
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['ALLOWED_TAGS'] = ['p', 'br', 'em', 'strong', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'a[href]']
csrf = CSRFProtect(app)
db.init_app(app)

from .views import views
from .auth import auth

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')

from .models.encrypted_note import EncryptedNote
from .models.note import Note
from .models.user import User

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.filter(User.id == int(id)).first()

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
