from app.models.user import User
from app.extensions import db, bcrypt

# Definition de la fonction pour créer un utilisateur admin
def create_admin_user():
    email = "admin@example.com" # courriel admin
    password_clair = "admin_password"  # mot de passe admin
    
    # Hashage du mot de passe
    hashed_password = bcrypt.generate_password_hash(password_clair).decode('utf-8')
    
    # pour creer l'utilisateur admin
    admin_user = User(nom="Admin", email=email, password=hashed_password, is_admin=True)
    db.session.add(admin_user)
    db.session.commit()
    print(f"Admin user '{admin_user.nom}' created successfully!")

if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        create_admin_user()