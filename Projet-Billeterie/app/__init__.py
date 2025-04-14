import locale
from flask import Flask
from app.models.user import db, bcrypt
from app.routes.main_routes import main
from app.models.reservation import Reservation
from app.routes.admin_routes import admin

# Initialisation de l'application flask
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bionics.db'

    # Configuration de la localisation pour les dates et heures en français
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

    # Initialisation de la base de données et de bcrypt
    db.init_app(app)
    bcrypt.init_app(app)
    app.register_blueprint(main)
    app.register_blueprint(admin)
    
    return app