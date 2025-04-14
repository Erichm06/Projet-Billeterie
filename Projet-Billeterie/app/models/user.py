#Creation de la base de données des utilisateurs
from app.extensions import db, bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Rajoute de la colonne id de l'utilisateur
    nom = db.Column(db.String(100), nullable=False) # Rajoute de la colonne le nom
    email = db.Column(db.String(120), unique=True, nullable=False) # Rajoute de la colonne adresse courriel
    password = db.Column(db.String(200), nullable=False) # Rajoute de la colonne le mot de passe
    is_admin = db.Column(db.Boolean, default=False)  # Rajoute de la colonne le statut de l'utilisateur si admin ou pas

# Definition des methode pour hacher le mot de passe
    def set_password(self, mot_de_passe_clair):
        self.password = bcrypt.generate_password_hash(mot_de_passe_clair).decode('utf-8')

#Definition de la méthode pour vérifier le mot de passe et authentifier l'utilisateur
    def check_password(self, mot_de_passe):
        return bcrypt.check_password_hash(self.password, mot_de_passe)
