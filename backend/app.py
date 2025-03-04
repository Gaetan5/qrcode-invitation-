from flask import Flask, jsonify, request, abort
import qrcode
import io
import base64
import uuid
import re
import jwt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
from flask_marshmallow import Marshmallow
from flask_paginate import Pagination, get_page_args
import logging

app = Flask(__name__)
CORS(app)

# Configuration de la clé secrète pour JWT et des paramètres de la base de données
SECRET_KEY = "letogolais56z@"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation des extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Configuration de la journalisation
logging.basicConfig(level=logging.INFO)

# Définition du modèle Billet
class Billet(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

# Création des tables avec un contexte d'application
with app.app_context():
    db.create_all()

# Schéma Marshmallow pour la validation des données de billet
class BilletSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Billet
        include_relationships = True  # Inclure les relations
        load_instance = True          # Charger l'instance

# Instances des schémas pour un billet unique et plusieurs billets
billet_schema = BilletSchema()
billets_schema = BilletSchema(many=True)

# Fonction de validation de l'email
def validate_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

# Fonction pour générer un code QR et le convertir en base64
def generate_qr_code(data):
    qr = qrcode.make(data)
    img_io = io.BytesIO()
    qr.save(img_io, format='PNG')
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue()).decode()

# Décorateur pour vérifier le jeton JWT
def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-tokens')
        if not token:
            return jsonify({'message': 'Token est manquant'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token a expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token est invalide'}), 401
        return f(*args, **kwargs)
    return decorated

# Route pour générer un code QR pour un nouveau billet
@app.route('/generate_qr', methods=['POST'], endpoint='generate_qr')
@token_required
def generate_qr():
    try:
        data = request.get_json()

        # Validation des données avec Marshmallow
        errors = billet_schema.validate(data)
        if errors:
            return jsonify(errors), 400

        # Vérification si le nom et l'email sont présents
        if not data.get('name') or not data.get('email'):
            return jsonify({"message": "Name and email are required."}), 400

        # Validation de l'email
        if not validate_email(data['email']):
            return jsonify({"message": "Invalid email format."}), 400

        # Création et sauvegarde du nouveau billet
        billet = Billet(id=str(uuid.uuid4()), name=data['name'], email=data['email'])
        db.session.add(billet)
        db.session.commit()

        # Génération du QR code en base64
        qr_base64 = generate_qr_code(billet.id)
        return jsonify({"id": billet.id, "qr_code": qr_base64})

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

# Route pour récupérer tous les billets avec pagination
@app.route('/tickets', methods=['GET'], endpoint='get_tickets')
@token_required
def get_tickets():
    # Récupération des arguments de pagination
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    tickets = Billet.query.offset(offset).limit(per_page).all()
    pagination = Pagination(page=page, per_page=per_page, total=Billet.query.count(), record_name='tickets')
    result = billets_schema.dump(tickets)
    return jsonify({'tickets': result, 'pagination': pagination.info})

# Route pour mettre à jour un billet existant par son ID
@app.route('/update_ticket/<id>', methods=['PUT'], endpoint='update_ticket')
@token_required
def update_ticket(id):
    data = request.get_json()
    billet = Billet.query.get(id)
    if not billet:
        return jsonify({"error": "Billet non trouvé"}), 404

    # Validation des données avec Marshmallow
    errors = billet_schema.validate(data, partial=True)  # partial=True permet de valider partiellement
    if errors:
        return jsonify(errors), 400

    billet.name = data.get('name', billet.name)
    billet.email = data.get('email', billet.email)
    db.session.commit()
    return jsonify({"message": "Billet mis à jour"})

# Route pour supprimer un billet existant par son ID
@app.route('/delete_ticket/<id>', methods=['DELETE'], endpoint='delete_ticket')
@token_required
def delete_ticket(id):
    billet = Billet.query.get(id)
    if not billet:
        return jsonify({"error": "Billet non trouvé"}), 404
    db.session.delete(billet)
    db.session.commit()
    return jsonify({"message": "Billet supprimé"})

# Gestionnaire global des erreurs pour journaliser les erreurs
@app.errorhandler(Exception)
def handle_error(e):
    logging.error(f'Error: {str(e)}')
    return jsonify({'error': 'An error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)