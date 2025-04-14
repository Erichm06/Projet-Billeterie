from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from app.extensions import db, bcrypt
from app.models.reservation import Reservation
from app.models.user import User
from app.models.events import Event
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Definition de la methode pour vérifier si l'utilisateur est connecté en tant qu'administrateur
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):  
            flash('Vous devez être administrateur pour accéder à cette page.', 'danger')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Definition de la route admin pour la page de connexion de l'administrateur
@admin.route('/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password) and user.is_admin:
            # Si l'utilisateur est trouvé et que le mot de passe est correct, on le connecte
            session['user_id'] = user.id
            session['is_admin'] = True
            flash('Connexion réussie !', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Email ou mot de passe invalide.', 'danger')
    return render_template('admin_login.html')

# Definition de la route admin pour la déconnexion de l'administrateur
@admin.route('/logout')
def admin_logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('admin.admin_login'))

# Definition de la route admin pour le tableau de bord de l'administrateur
@admin.route('/dashboard')
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

# Definition de la route admin pour la gestion des événements
@admin.route('/add_event', methods=['GET', 'POST'])
@admin_required

# Route pour ajouter un événement
def add_event():

    if request.method == 'POST':
        titre = request.form['titre']
        cost = request.form['cost']
        description = request.form.get('description', '')

        # Conversion de la date dans un format A-M-J
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()

        # Vérification si l'événement existe déjà
        new_event = Event(
            nom=titre,
            date=date,
            cost=cost,
        )
        # Ajout de l'événement à la base de données
        db.session.add(new_event)
        db.session.commit()
        
        flash("Événement ajouté avec succès !", "success")
        return redirect(url_for('admin.admin_events'))

    return render_template('admin_add_event.html')

# Definition de la route admin pour la gestion des événements
@admin.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@admin_required
def edit_event(event_id):

    # Rechercher l'événement spécifique avec son ID
    event = Event.query.get(event_id)
    if not event:
        flash("Événement introuvable.", "danger")
        return redirect(url_for('admin.admin_events'))

    if request.method == 'POST':
        # Mettre à jour les détails de l'événement
        event.nom = request.form['nom']
        event.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        event.cost = request.form['cost']

    # Vérification si l'événement existe déjà
        db.session.commit()

        flash("Événement modifié avec succès !", "success")
        return redirect(url_for('admin.admin_events'))


    return render_template('admin_edit_event.html', event=event)

# Definition de la route admin pour supprimer un événement
@admin.route('/delete_event/<int:event_id>', methods=['POST'])
@admin_required
def delete_event_admin(event_id):
    
    event = Event.query.get(event_id) # Récupérer l'événement spécifique par son ID
    if not event:
        flash("Événement introuvable.", "danger")
        return redirect(url_for('admin.admin_events'))
    
    # Récupérer toutes les réservations associées à cet événement
    reservations = Reservation.query.filter_by(titre_evenement=event.nom).all() 
    for reservation in reservations:
        reservation.statut = 'Annulé' # Marquer la réservation comme annulée
    db.session.commit() 

    db.session.delete(event) # Supprimer l'événement
    db.session.commit()

    flash("Événement supprimé avec succès. Les réservations associées ont été marquées comme 'Annulé'.", "success")
    return redirect(url_for('admin.admin_events'))

# Definition de la route admin pour la gestion des réservations
@admin.route('/reservations')
@admin_required

def manage_reservations():
    reservations = Reservation.query.all()
    return render_template('admin_manage_reservations.html', reservations=reservations)

# Definition de la route admin pour la gestion des réservations d'un utilisateur spécifique
@admin.route('/user/<int:user_id>/reservations')
@admin_required
def user_reservations(user_id):
    user = User.query.get_or_404(user_id)
    reservations = Reservation.query.filter_by(user_id=user.id).all()
    return render_template('admin_user_reservations.html', user=user, reservations=reservations)

# Definition de la route admin pour la gestion des événements
@admin.route('/events')
@admin_required
def admin_events():
    from app.models.events import Event
    events = Event.query.all()
    return render_template('admin_events.html', events=events)

# Definition de la route admin pour supprimer une réservation
@admin.route('/delete_reservation/<int:reservation_id>', methods=['POST'])
@admin_required  # Assure que seul un admin peut accéder à cette route
def delete_reservation_admin(reservation_id):

    # Récupérer la réservation spécifique par son ID
    reservation = Reservation.query.get(reservation_id)

    if not reservation:
        flash("Réservation introuvable.", "danger")
        return redirect(request.referrer)  # Retourne à la page qui a fait la requete

    # Supprimer la réservation
    db.session.delete(reservation)
    db.session.commit()
    flash("La réservation a été supprimée avec succès.", "success")

    # Retourner à la page actuelle (au lieu de manage_reservations)
    return redirect(request.referrer)