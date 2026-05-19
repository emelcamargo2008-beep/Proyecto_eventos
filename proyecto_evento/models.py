from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Usuarios(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), nullable=False)
    biografia = db.Column(db.Text, nullable=True)

    eventos_creados = db.relationship('Eventos', backref='organizador', lazy=True)


class Eventos(db.Model):
    __tablename__ = 'eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.String(100), nullable=False)  
    categoria = db.Column(db.String(100), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)


class Registro(db.Model):
    __tablename__ = 'registro'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=db.func.current_timestamp())


    usuario = db.relationship('Usuarios', backref=db.backref('inscripciones', lazy=True))
    evento = db.relationship('Eventos', backref=db.backref('asistentes', lazy=True))