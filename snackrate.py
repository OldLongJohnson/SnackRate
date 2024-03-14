from app import app, db
from app.models import User, Snack, Rating  # Importieren Sie die aktualisierten Modelle

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Snack': Snack, 'Rating': Rating}  # Fügen Sie 'Snack' und 'Rating' hinzu
