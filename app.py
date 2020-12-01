from flask import Flask
from flask_login import LoginManager
from flask_principal import Principal

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['UPLOAD_FOLDER'] = 'files'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

principal = Principal(app)
