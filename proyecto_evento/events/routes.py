from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime


from app import app, role_required
from models import db, User, Event, Registration

@app.route('/events')
@login_required
def events_list():
    
    if current_user.role == 'organizer':
        events = Event.query.filter_by(organizer_id=current_user.id).all()
    else:
        events = Event.query.all()
        
    return render_template('events/events_list.html', events=events)


@app.route('/events/create', methods=['GET', 'POST'])
@login_required
@role_required('organizer') 
def create_event():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        capacity = request.form.get('capacity')
        category = request.form.get('category')

       
        if not title or not date_str or not capacity or not category:
            flash('Por favor, llena todos los campos obligatorios.', 'danger')
            return render_template('events/create_events.html')

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            new_event = Event(
                title=title,
                description=description,
                date=date_obj,
                capacity=int(capacity),
                category=category,
                organizer_id=current_user.i
            )
            
            db.session.add(new_event)
            db.session.commit()
            flash('¡Evento creado exitosamente!', 'success')
            return redirect(url_for('events_list'))
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al crear el evento. Revisa los datos.', 'danger')

    return render_template('events/create_events.html')



@app.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@role_required('organizer')
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    
    if event.organizer_id != current_user.id:
        abort(403) 

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        date_str = request.form.get('date')
        event.capacity = int(request.form.get('capacity'))
        event.category = request.form.get('category')

        if date_str:
            event.date = datetime.strptime(date_str, '%Y-%m-%d')

        try:
            db.session.commit()
            flash('Evento actualizado correctamente.', 'success')
            return redirect(url_for('events_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el evento.', 'danger')

    return render_template('events/edit_events.html', event=event)


# ==========================================
# 4. ELIMINAR EVENTO (Solo el Organizador dueño)
# ==========================================
@app.route('/events/delete/<int:event_id>', methods=['POST'])
@login_required
@role_required('organizer')
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # RÚBRICA: Solo el creador puede eliminarlo
    if event.organizer_id != current_user.id:
        abort(403)

    try:
        # Al eliminar el evento, se deberían borrar sus inscripciones vinculadas
        Registration.query.filter_by(event_id=event.id).delete()
        db.session.delete(event)
        db.session.commit()
        flash('Evento eliminado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se pudo eliminar el evento.', 'danger')
        
    return redirect(url_for('events_list'))


# ==========================================
# 5. INSCRIBIRSE A UN EVENTO (Solo Asistentes)
# ==========================================
@app.route('/events/register/<int:event_id>', methods=['POST'])
@login_required
@role_required('attendee') # Solo asistentes pueden inscribirse
def register_to_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Verificar si ya está inscrito
    already_registered = Registration.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    if already_registered:
        flash('Ya estás inscrito en este evento.', 'warning')
        return redirect(url_for('events_list'))
    
    # RÚBRICA: Verificar cupo máximo disponible antes de inscribir
    current_registrations = Registration.query.filter_by(event_id=event.id).count()
    if current_registrations >= event.capacity:
        flash('Lo sentimos, no hay cupos disponibles para este evento.', 'danger')
        return redirect(url_for('events_list'))
    
    # Crear inscripción si pasa las validaciones
    new_registration = Registration(
        user_id=current_user.id,
        event_id=event.id,
        registered_at=datetime.utcnow()
    )
    
    try:
        db.session.add(new_registration)
        db.session.commit()
        flash(f'¡Te has inscrito exitosamente a {event.title}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al procesar la inscripción.', 'danger')
        
    return redirect(url_for('events_list'))


# ==========================================
# 6. CANCELAR INSCRIPCIÓN (Solo Asistentes)
# ==========================================
@app.route('/events/cancel/<int:event_id>', methods=['POST'])
@login_required
@role_required('attendee')
def cancel_registration(event_id):
    registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    if not registration:
        flash('No estás inscrito en este evento.', 'danger')
        return redirect(url_for('events_list'))
        
    try:
        db.session.delete(registration)
        db.session.commit()
        flash('Tu inscripción ha sido cancelada.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('No se pudo cancelar la inscripción.', 'danger')
        
    return redirect(url_for('events_list'))