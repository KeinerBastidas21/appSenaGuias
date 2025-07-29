from flask import Blueprint, render_template, redirect, request, session, flash, url_for
from flask_mail import Message, Mail
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from app.models import Instructor, GuiaAprendizaje
from datetime import datetime

from . import mail

bp = Blueprint("main", __name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"))
mail = Mail()

# Listas fijas para selección
REGIONALES = ["Cauca", "Huila", "Antioquia", "Valle", "Nariño"]
PROGRAMAS = [
    "Desarrollo de Software", "Multimedia", "Inteligencia Artificial",
    "Analítica de Datos", "Construcción", "Contabilidad"
]

@bp.route("/")
def index():
    return redirect(url_for("main.login"))

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        contraseña = request.form.get("contraseña")
        regional = request.form.get("regional")

        if not all([nombre, correo, contraseña, regional]):
            return render_template("register.html", mensaje="Todos los campos son obligatorios.", regionales=REGIONALES)

        if Instructor.objects(correo=correo).first():
            return render_template("register.html", mensaje="Este correo ya está registrado.", regionales=REGIONALES)

        contrasena_hash = generate_password_hash(contraseña)

        nuevo_instructor = Instructor(
            nombre=nombre,
            correo=correo,
            regional=regional,
            contraseña=contrasena_hash
        )
        nuevo_instructor.save()

        # Enviar correo con credenciales
        try:
            msg = Message("Registro exitoso", recipients=[correo])
            msg.body = f"""
Hola {nombre},

Te has registrado exitosamente en la plataforma de guías de aprendizaje del SENA.

Tus credenciales son:
- Usuario (correo): {correo}
- Contraseña: {contraseña}

Por seguridad, te recomendamos cambiar tu contraseña después del primer ingreso.

Atentamente,
Plataforma SENA Guías
"""
            mail.send(msg)
        except Exception as e:
            return render_template("register.html", mensaje="Registro exitoso, pero error al enviar el correo.", regionales=REGIONALES)

        return render_template("login.html", mensaje="Registro exitoso. Revisa tu correo.")
    
    return render_template("register.html", regionales=REGIONALES)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["login_email"]
        contraseña = request.form["login_pass"]

        instructor = Instructor.objects(correo=correo).first()
        if instructor and check_password_hash(instructor.contraseña, contraseña):
            session["user_id"] = str(instructor.id)
            return redirect(url_for("main.subir_guia"))
        else:
            flash("Correo o contraseña incorrectos")
    return render_template("login.html")

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))

@bp.route("/subir_guia", methods=["GET", "POST"])
def subir_guia():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    instructor = Instructor.objects(id=session["user_id"]).first()

    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        programa = request.form["programa"]
        archivo = request.files["archivo_pdf"]

        if archivo and archivo.filename.endswith(".pdf"):
            nombre_archivo = secure_filename(archivo.filename)
            ruta = os.path.join("app/static/uploads", nombre_archivo)
            archivo.save(ruta)

            guia = GuiaAprendizaje(
                nombre=nombre,
                descripcion=descripcion,
                programa=programa,
                archivo_pdf=nombre_archivo,
                fecha=datetime.utcnow(),
                instructor=instructor
            )
            guia.save()

            flash("Guía subida exitosamente.")
            return redirect(url_for("main.listar_guias"))
        else:
            flash("Debe subir un archivo PDF válido.")

    return render_template("upload_guide.html", programas=PROGRAMAS)

@bp.route("/guias")
def listar_guias():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    guias = GuiaAprendizaje.objects().select_related()
    return render_template("list_guides.html", guias=guias)
