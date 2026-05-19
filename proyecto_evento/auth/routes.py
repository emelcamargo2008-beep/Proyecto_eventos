from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import app
from models import db, Usuarios

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('nombre_usuario')
        email = request.form.get('correo')
        password = request.form.get('password')
        role = request.form.get('rol')  

        if not username or not email or not password or not role:
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('register.html')

        user_exists = Usuarios.query.filter((Usuarios.nombre_usuario == username) | (Usuarios.correo == email)).first()
        if user_exists:
            flash('El nombre de usuario o el correo ya están registrados.', 'danger')
            return render_template('register.html')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    
        new_user = Usuarios(
            nombre_usuario=nombre_usuario,
            correo=correo,
            password_hash=hashed_password,
            rol=rol,
            biografia=""
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login.html'))
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al registrar el usuario.', 'danger')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        correo = request.form.get('correo')
        password = request.form.get('password')

        user = Usuarios.query.filter_by(correo=correo).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'¡Bienvenido de nuevo, {user.nombre_usuario}!', 'success')
            return redirect(url_for('events_list'))
        else:
            flash('Correo electrónico o contraseña incorrectos.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login.html'))