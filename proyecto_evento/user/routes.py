from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import app
from models import db, User, Event, Registration

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
      
        username = request.form.get('username')
        bio = request.form.get('bio')

       
        if not username:
            flash('El nombre de usuario no puede estar vacío.', 'danger')
            return redirect(url_for('profile'))

       
        existing_user = User.query.filter(User.username == username, User.id != current_user.id).first()
        if existing_user:
            flash('Ese nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('profile'))

       
        current_user.username = username
        current_user.bio = bio

        try:
            db.session.commit()
            flash('¡Perfil actualizado con éxito!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al actualizar el perfil.', 'danger')
            return redirect(url_for('profile'))

   
    if current_user.role == 'organizer':
        history = Event.query.filter_by(organizer_id=current_user.id).all()
    else:
        history = Event.query.join(Registration).filter(Registration.user_id == current_user.id).all()
    return render_template('user/profile.html', history=history)