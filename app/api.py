#app/api.py
from app import app
from app.models import User
from flask import jsonify

@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    data = User.query.get_or_404(id).to_dict()
    return jsonify(data)

# Gibt alle Benutzer aus
@app.route('/api/users', methods=['GET'])
def get_users():
    data = User.query.all()
    return jsonify([s.todict() for s in data])