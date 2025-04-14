#Création de la base de données des événements
from app.extensions import db

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Rajoute de la colonne id de l'événement
    nom = db.Column(db.String(100), nullable=False) # Rajoute de la colonne le nom
    date = db.Column(db.DateTime, nullable=False) # Rajoute de la colonne la date
    cost = db.Column(db.Integer, nullable=False)  # Rajoute de la colonne le coût
    