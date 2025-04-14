#Creation de la base de données des réservations
from app.extensions import db

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Rajoute l'id de la réservation
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Rajoute de la colonne id de l'utilisateur dans la réservation
    nom_utilisateur = db.Column(db.String(100), nullable=False) # Rajoute de la colonne le nom de l'utilisateur dans l'id de la réservation
    titre_evenement = db.Column(db.String(120), nullable=False) # Rajoute de la colonne le titre de l'événement dans l'id de la réservation
    date_evenement = db.Column(db.String(50), nullable=False) # Rajoute de la colonne la date de l'événement dans l'id de la réservation
    statut = db.Column(db.String(50), default='Actif')  # Rajoute de la colonne le statut de la réservation si actif ou annulé


    user = db.relationship('User', backref=db.backref('reservations', lazy=True)) # Rajoute la relation entre l'utilisateur et la réservation. Ce code veux dire que chaque reservation est connecte a un utilisateur spécifique.