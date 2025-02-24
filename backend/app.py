from flask import Flask, jsonify, request, abort
import qrcode
import io
import base64
import uuid
import re
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
CORS(app)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Définition du modèle Billet
class Billet(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

# Création des tables avec un contexte d'application
with app.app_context():
    db.create_all()

# Validation de l'email
def validate_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

# Génération du QR code
def generate_qr_code(data):
    qr = qrcode.make(data)
    img_io = io.BytesIO()
    qr.save(img_io, format='PNG')
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue()).decode()

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    try:
        data = request.json
        if not data.get('name') or not data.get('email'):
            abort(400, description="Name and email are required.")
        if not validate_email(data['email']):
            abort(400, description="Invalid email format.")
        
        billet = Billet(id=str(uuid.uuid4()), name=data['name'], email=data['email'])
        db.session.add(billet)
        db.session.commit()
        
        qr_base64 = generate_qr_code(billet.id)
        return jsonify({"id": billet.id, "qr_code": qr_base64})
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, description="Database error.")
    except Exception as e:
        abort(500, description="An error occurred.")

@app.route('/tickets', methods=['GET'])
def get_tickets():
    tickets = Billet.query.all()
    return jsonify([{"id": t.id, "name": t.name, "email": t.email} for t in tickets])

if __name__ == '__main__':
    app.run(debug=True)