import os
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_mail import Mail
from dotenv import load_dotenv

load_dotenv()

db = MongoEngine()
mail = Mail()

def create_app():
    app = Flask(__name__)

    app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave_por_defecto_insegura")

    db.init_app(app)
    mail.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app