from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, Usuarios

routes_auth = Blueprint('auth', __name__)

@routes_auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('events.events_list'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role') 

        if not username or not email or not password or not role:
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('auth/register.html')

        user_exists = Usuarios.query.filter((Usuarios.nombre_usuario == username) | (Usuarios.correo == email)).first()
        if user_exists:
            flash('El nombre de usuario o el correo ya están registrados.', 'danger')
            return render_template('auth/register.html')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = Usuarios(
            nombre_usuario=username,
            correo=email,
            password_hash=hashed_password,
            rol=role,
            biografia=""
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al registrar el usuario.', 'danger')

    return render_template('auth/register.html')

@routes_auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('events.events_list'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Usuarios.query.filter_by(correo=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'¡Bienvenido de nuevo, {user.nombre_usuario}!', 'success')
            return redirect(url_for('events.events_list'))
        else:
            flash('Correo electrónico o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html')

@routes_auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))