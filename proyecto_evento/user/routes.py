from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from models import db, Usuarios, Eventos, Registro

routes_user = Blueprint('user', __name__)

@routes_user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        bio = request.form.get('bio')

        if not username:
            flash('El nombre de usuario no puede estar vacío.', 'danger')
            return redirect(url_for('user.profile'))

        existing_user = Usuarios.query.filter(Usuarios.nombre_usuario == username, Usuarios.id != current_user.id).first()
        if existing_user:
            flash('Ese nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('user.profile'))

        current_user.nombre_usuario = username
        current_user.biografia = bio

        try:
            db.session.commit()
            flash('¡Perfil actualizado con éxito!', 'success')
            return redirect(url_for('user.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al actualizar el perfil.', 'danger')
            return redirect(url_for('user.profile'))

    if current_user.rol == 'organizer':
        history = Eventos.query.filter_by(organizer_id=current_user.id).all()
    else:
        history = Eventos.query.join(Registro).filter(Registro.user_id == current_user.id).all()

    return render_template('user/profile.html', history=history)