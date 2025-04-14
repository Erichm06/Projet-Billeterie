from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask import session
from app.models.reservation import Reservation
main = Blueprint('main', __name__)
from app import db
from app.extensions import db, bcrypt
from app.models.events import Event
from app.models.user import User

# Route principale de l'application
@main.route('/')
def home():
    from app.models.events import Event
    events = Event.query.all()
    return render_template('index.html', events=events)

# Route pour afficher les détails d'un événement
@main.route('/reserver/<int:event_id>', methods=['GET', 'POST'])
def reserver(event_id):
    from app.models.events import Event

    # Vérifier si l'utilisateur est connecté
    if 'user_id' not in session:
        flash("Veuillez vous connecter pour réserver un billet.")
        return redirect(url_for('main.register'))

    # Rechercher l'événement par son ID
    event = Event.query.get(event_id)
    if not event:
        flash("Événement introuvable.")
        return redirect(url_for('main.dashboard'))

    # fonction render pour afficher la page de réservation
    return render_template("reserver.html", event=event, event_id=event_id, utilisateur=session.get('user'))

# Route pour afficher la page d'inscription
@main.route('/register', methods=['GET', 'POST'])
def register():
    from app.models.user import db, User

    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom']
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']
        confirm = request.form['confirmé']

        # Vérifier si les mots de passe correspondent
        if mot_de_passe != confirm:
            flash("Les mots de passe ne correspondent pas.")
            return redirect(url_for('main.register'))

        # Vérifier si l'email est déjà utilisé
        if User.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.")
            return redirect(url_for('main.register'))

        # Créer un nouvel utilisateur
        user = User(nom=nom, email=email)
        user.set_password(mot_de_passe)
        db.session.add(user)
        db.session.commit()

       ## Confirme la connexion de l'utilisateur 
        session['user_id'] = user.id
        session['user'] = user.nom
        flash(f"Bienvenue {user.nom} ! Vous êtes maintenant connecté.")
        return redirect(url_for('main.home'))

    # Afficher le formulaire d'inscription
    return render_template('register.html')

# Route pour afficher la page de connexion
@main.route('/login', methods=['GET', 'POST'])
def login():
    from app.models.user import User

    if request.method == 'POST':
        # Récupérer les informations du formulaire
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']

        # Vérifier les informations dans la base de données
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(mot_de_passe):
            # Stocker les informations dans la session
            session['user_id'] = user.id
            session['user'] = user.nom
            flash(f"Bienvenue {user.nom} ! Connexion réussie.")
            return redirect(url_for('main.home'))
        else:
            flash("Email ou mot de passe incorrect.")
            return redirect(url_for('main.login'))

    # Afficher la page de connexion
    return render_template('login.html')

# Route pour afficher la page de paiement
@main.route('/paiement/<int:event_id>', methods=['GET', 'POST'])
def paiement(event_id):

    # Rechercher l'événement par son ID
    event = Event.query.get(event_id)
    if not event:
        flash("Événement introuvable.")
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        # Récupérer les informations de paiement
        nom_carte = request.form.get('nom_carte')
        numero_carte = request.form.get('numero_carte')

        # Valider le numéro de carte
        if not numero_carte or not numero_carte.isdigit() or len(numero_carte) < 4:
            flash("Veuillez entrer un numéro de carte valide.")
            return redirect(url_for('main.paiement', event_id=event_id))

        # Vérifier si l'utilisateur est connecté
        user_id = session.get('user_id')
        if not user_id:
            flash("Vous devez être connecté pour réserver.")
            return redirect(url_for('main.login'))

        user = User.query.get(user_id)

        # Créer une réservation pour l'utilisateur
        reservation = Reservation(
            user_id=user.id,
            nom_utilisateur=user.nom,
            titre_evenement=event.nom,
            date_evenement=event.date.strftime('%d %B %Y')
        )
        db.session.add(reservation)
        db.session.commit()

        # Rediriger vers la confirmation
        return render_template('confirmation.html', event=event)

    # Afficher la page de paiement
    return render_template('paiement.html', event=event)

# Route pour afficher le tableau de bord de l'utilisateur
@main.route('/dashboard', methods=['GET'])
def dashboard():
    from app.models.user import User
    from app.models.reservation import Reservation

    # Vérifier si l'utilisateur est connecté
    user_id = session.get('user_id')
    if not user_id:
        flash("Connectez-vous pour accéder à votre tableau de bord.")
        return redirect(url_for('main.login'))

    # Ici on recupere les informations de l'utilisateur et ses réservations
    utilisateur = User.query.get(user_id)
    reservations = Reservation.query.filter_by(user_id=user_id).all()

    # Afficher le tableau de bord
    return render_template('dashboard.html', utilisateur=utilisateur, reservations=reservations)

# Route pour afficher la page pour logout
@main.route('/logout')
def logout():
    # Supprimer les informations de session (déconnexion)
    session.pop('user', None)
    session.pop('user_id', None)
    flash("Déconnexion réussie.", "info")
    return redirect(url_for('main.home'))

# route pour afficher la page de suppression d'un événement
@main.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    from app.models.reservation import Reservation

    # Vérifier si l'utilisateur est connecté
    user_id = session.get('user_id')
    if not user_id:
        flash("Vous devez être connecté pour supprimer un événement.")
        return redirect(url_for('main.login'))

    # Rechercher et supprimer la réservation
    reservation = Reservation.query.filter_by(id=event_id, user_id=user_id).first()
    if not reservation:
        flash("Événement introuvable ou non autorisé.")
        return redirect(url_for('main.dashboard'))

    db.session.delete(reservation)
    db.session.commit()
    flash("Événement supprimé avec succès. Votre paiement sera remboursé.")
    return redirect(url_for('main.dashboard'))