# Importieren der benötigten Module und Objekte
from flask import render_template
from app import app, db

# Behandlung von 404-Fehlern (Seite nicht gefunden)
@app.errorhandler(404)
def not_found_error(error):
    # Rückgabe der benutzerdefinierten 404-Seite mit entsprechendem 404 Statuscode
    return render_template('404.html'), 404

# Behandlung von 500-Fehlern (Interner Serverfehler)
@app.errorhandler(500)
def internal_error(error):
    # Zurücksetzen der aktuellen Datenbank-Sitzung, um inkonsistente Datenbankzustände zu vermeiden
    db.session.rollback()
    # Rückgabe der benutzerdefinierten 500-Seite mit entsprechendem 500 Statuscode
    return render_template('500.html'), 500
