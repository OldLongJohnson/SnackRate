from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from flask_login import UserMixin
from sqlalchemy.sql import func
from app import db, login

# Tabelle für die Favoriten-Beziehung zwischen Usern und Snacks
favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('snack_id', db.Integer, db.ForeignKey('snack.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    # Benutzermodell mit Grundattributen und Beziehungen
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    snacks = db.relationship('Snack', backref='author', lazy='dynamic')
    ratings = db.relationship('Rating', backref='rater', lazy='dynamic')
    favorited_snacks = db.relationship('Snack', secondary=favorites,
                                       backref=db.backref('favorited_by', lazy='dynamic'), lazy='dynamic')

    # Passwort-Hash-Funktionen
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Erzeugt einen Avatar basierend auf der E-Mail-Adresse
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    # Funktionen zur Handhabung von Favoriten
    def favorite_snack(self, snack):
        if not self.has_favorited(snack):
            self.favorited_snacks.append(snack)

    def unfavorite_snack(self, snack):
        if self.has_favorited(snack):
            self.favorited_snacks.remove(snack)

    def has_favorited(self, snack):
        return self.favorited_snacks.filter(favorites.c.snack_id == snack.id).count() > 0

class Snack(db.Model):
    # Snackmodell mit Attributen und durchschnittlicher Bewertungsfunktion
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), unique=True, index=True)
    description = db.Column(db.String(140))
    category = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Berechnet die durchschnittliche Bewertung eines Snacks
    def average_rating(self):
        return db.session.query(func.avg(Rating.rating)).filter(Rating.snack_id == self.id).scalar()

class Rating(db.Model):
    # Bewertungsmodell mit Beziehungen zu User und Snack
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    comment = db.Column(db.String(140), nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    snack_id = db.Column(db.Integer, db.ForeignKey('snack.id'))

    # Beziehungen zu User und Snack für die Rückverfolgung
    user = db.relationship('User', backref='user_ratings')
    snack = db.relationship('Snack', backref='snack_ratings')

# Lädt den Benutzer basierend auf der Benutzer-ID
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
