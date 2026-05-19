from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class Usuarios(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    biografia = db.Column(db.Text)
    eventos = db.relationship('Eventos', backref='organizador', lazy=True)
    registros = db.relationship('Registro', backref='usuario', lazy=True)



class Eventos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)

    organizador_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
        nullable=False
    )

    registros = db.relationship(
        'Registro',
        backref='evento',
        lazy=True,
        cascade="all, delete"
    )



class Registro(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
        nullable=False
    )
    event_id = db.Column(
        db.Integer,
        db.ForeignKey('eventos.id'),
        nullable=False
    )

    registered_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )