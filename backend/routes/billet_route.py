from flask import Blueprint, current_app, request, jsonify
from models.billets import Billet, db
import qrcode
import io
import base64
import uuid
import jwt
from flask_marshmallow import Marshmallow
import logging
from flask_paginate import Pagination, get_page_args
from app import validate_email  # Import de la fonction validate_email depuis app.py

# Configuration de la clé secrète pour JWT et de la journalisation
SECRET_KEY = "letogolais56z@"
logging.basicConfig(level=logging.INFO)

# Initialisation de Marshmallow
ma = Marshmallow(current_app)

# Schéma Marshmallow pour la validation des billets
class BilletSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Billet

# Instances des schémas
billet_schema = BilletSchema()
billets_schema = BilletSchema(many=True)

# Création du Blueprint pour organiser les routes
ticket_bp = Blueprint('ticket_bp', __name__)

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

# Route pour générer un code QR
@ticket_bp.route('/generate_qr', methods=['POST'])
@token_required
def generate_qr():
    data = request.json
    errors = billet_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    # Création d'un nouvel objet Billet avec des données uniques
    billet = Billet(id=str(uuid.uuid4()), name=data['name'], email=data['email'])
    
    if not data.get('name') or not data.get('email'):
        return jsonify({"message": "Name and email are required."}), 400
    if not validate_email(data['email']):
        return jsonify({"message": "Invalid email format."}), 400
    
    db.session.add(billet)
    db.session.commit()
    
    # Génération du code QR pour l'ID du billet
    qr = qrcode.make(billet.id)
    img_io = io.BytesIO()
    qr.save(img_io, format='PNG')
    img_io.seek(0)
    qr_base64 = base64.b64encode(img_io.getvalue()).decode()
    
    return jsonify({"id": billet.id, "qr_code": qr_base64})

# Route pour récupérer tous les billets avec pagination
@ticket_bp.route('/tickets', methods=['GET'])
@token_required
def get_tickets():
    # Récupération des arguments de pagination
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    tickets = Billet.query.offset(offset).limit(per_page).all()
    pagination = Pagination(page=page, per_page=per_page, total=Billet.query.count(), record_name='tickets')
    result = billets_schema.dump(tickets)
    return jsonify({'tickets': result, 'pagination': pagination.info})

# Route pour mettre à jour un billet existant par son ID
@ticket_bp.route('/update_ticket/<id>', methods=['PUT'])
@token_required
def update_ticket(id):
    data = request.json
    billet = Billet.query.get(id)
    if not billet:
        return jsonify({"error": "Billet non trouvé"}), 404
    billet.name = data.get('name', billet.name)
    billet.email = data.get('email', billet.email)
    db.session.commit()
    return jsonify({"message": "Billet mis à jour"})

# Route pour supprimer un billet existant par son ID
@ticket_bp.route('/delete_ticket/<id>', methods=['DELETE'])
@token_required
def delete_ticket(id):
    billet = Billet.query.get(id)
    if not billet:
        return jsonify({"error": "Billet non trouvé"}), 404
    db.session.delete(billet)
    db.session.commit()
    return jsonify({"message": "Billet supprimé"})

# Gestionnaire global des erreurs pour journaliser les erreurs
@ticket_bp.errorhandler(Exception)
def handle_error(e):
    logging.error(f'Error: {str(e)}')
    return jsonify({'error': 'Something went wrong!'}), 500
