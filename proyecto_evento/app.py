import os
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

from config import Config
app.config.from_object(Config)

from models import db, Usuarios
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  
login_manager.login_message = 'Por favor, inicia sesión para acceder.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('auth/login.html'), 403 

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return redirect(url_for('events.events_list'))

from auth.routes import routes_auth
from events.routes import routes_events
from user.routes import routes_user

app.register_blueprint(routes_auth)
app.register_blueprint(routes_events)
app.register_blueprint(routes_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)