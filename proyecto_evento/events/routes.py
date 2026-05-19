from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from models import db, Usuarios, Eventos, Registro

routes_events = Blueprint('events', __name__)

def role_required(role):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.rol != role:
                return render_template('auth/login.html'), 403  
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@routes_events.route('/events')
@login_required
def events_list():
    if current_user.rol == 'organizer':
        events = Eventos.query.filter_by(organizer_id=current_user.id).all()
    else:
        events = Eventos.query.all()
    return render_template('events/events_list.html', events=events)


@routes_events.route('/events/create', methods=['GET', 'POST'])
@login_required
@role_required('organizer')
def create_event():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        fecha = request.form.get('fecha') 
        capacidad = request.form.get('capacidad')
        categoria = request.form.get('categoria')

        if not titulo or not fecha or not capacidad or not categoria:
            flash('Por favor, llena todos los campos obligatorios.', 'danger')
            return render_template('events/create_events.html')

        try:
            new_event = Eventos(
                titulo=titulo,
                descripcion=descripcion,
                fecha=fecha,
                capacidad=int(capacidad),
                categoria=categoria,
                organizer_id=current_user.id
            )
            db.session.add(new_event)
            db.session.commit()
            flash('¡Evento creado exitosamente!', 'success') 
            return redirect(url_for('events.events_list'))
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al crear el evento.', 'danger')

    return render_template('events/create_events.html')

@routes_events.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Eventos.query.get_or_404(event_id)
    
    if current_user.rol != 'admin' and event.organizer_id != current_user.id:
        flash('No tienes permiso para editar este evento.', 'danger')
        return redirect(url_for('events.events_list'))
        
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        fecha = request.form.get('fecha')
        capacidad = request.form.get('capacidad')
        categoria = request.form.get('categoria')

        if not titulo or not fecha or not capacidad or not categoria:
            flash('Por favor, llena todos los campos obligatorios.', 'danger')
            return render_template('events/edit_events.html', event=event)

        try:
            event.titulo = titulo
            event.descripcion = descripcion if descripcion else ""
            event.fecha = str(fecha)
            event.capacidad = int(capacidad)
            event.categoria = categoria
            
            db.session.commit()
            flash('¡Evento actualizado exitosamente!', 'success')
            return redirect(url_for('events.events_list'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error real al editar en base de datos: {e}")
            flash('Ocurrió un error al actualizar el evento.', 'danger')
    return render_template('events/edit_events.html', event=event)

@routes_events.route('/events/delete/<int:event_id>', methods=['POST'])
@login_required
@role_required('organizer')
def delete_event(event_id):
    event = Eventos.query.get_or_404(event_id)
    
    if event.organizer_id != current_user.id:
        abort(403)

    try:
        db.session.delete(event) 
        db.session.commit()
        flash('Evento eliminado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se pudo eliminar el evento.', 'danger')
        
    return redirect(url_for('events.events_list'))

@routes_events.route('/events/register/<int:event_id>', methods=['POST'])
@login_required
@role_required('attendee')
def register_to_event(event_id):
    event = Eventos.query.get_or_404(event_id)
    
    already_registered = Registro.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    if already_registered:
        flash('Ya estás inscrito en este evento.', 'warning')
        return redirect(url_for('events.events_list'))
    
    current_registrations = Registro.query.filter_by(event_id=event.id).count()
    if current_registrations >= event.capacidad:
        flash('Lo sentimos, no hay cupos disponibles.', 'danger')
        return redirect(url_for('events.events_list'))
    
    new_registration = Registro(
        user_id=current_user.id,
        event_id=event.id
    )
    
    try:
        db.session.add(new_registration)
        db.session.commit()
        flash(f'¡Te has inscrito a {event.titulo}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al procesar la inscripción.', 'danger')
        
    return redirect(url_for('events.events_list'))

@routes_events.route('/events/cancel/<int:event_id>', methods=['POST'])
@login_required
@role_required('attendee')
def cancel_registration(event_id):
    registration = Registro.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    if not registration:
        flash('No estás inscrito en este evento.', 'danger')
        return redirect(url_for('events.events_list'))
        
    try:
        db.session.delete(registration)
        db.session.commit()
        flash('Tu inscripción ha sido cancelada.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('No se pudo cancelar la inscripción.', 'danger')
        
    return redirect(url_for('events.events_list'))