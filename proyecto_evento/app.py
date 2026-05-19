import os
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from functools import wraps

app = Flask(__name__)

from config import config
app.config.from_object(config['development'])


from models import db, Usuarios
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  
login_manager.login_message = 'Por favor, inicia sesión para acceder.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id)) 


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.rol != role: 
                return render_template('login.html'), 403  
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('login.html'), 403 

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return redirect(url_for('events_list'))

from auth.routes import *
from events.routes import *
from user.routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)