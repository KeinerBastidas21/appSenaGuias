from mongoengine import Document, StringField, EmailField, ReferenceField, DateTimeField
from datetime import datetime

class Instructor(Document):
    nombre = StringField(required=True)
    correo = EmailField(required=True, unique=True)
    regional = StringField(required=True)
    contraseña = StringField(required=True)

class GuiaAprendizaje(Document):
    nombre = StringField(required=True)
    descripcion = StringField(required=True)
    programa = StringField(required=True)
    archivo_pdf = StringField(required=True)
    fecha = DateTimeField(default=datetime.utcnow)
    instructor = ReferenceField(Instructor)
