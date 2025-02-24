from flask import Blueprint, request, jsonify
from models.billets import Billet, db
import qrcode
import io
import base64
import uuid

ticket_bp = Blueprint('ticket_bp', __name__)

@ticket_bp.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json
    billet = Billet(id=str(uuid.uuid4()), name=data['name'], email=data['email'])
    db.session.add(billet)
    db.session.commit()
    
    qr = qrcode.make(billet.id)
    img_io = io.BytesIO()
    qr.save(img_io, format='PNG')
    img_io.seek(0)
    qr_base64 = base64.b64encode(img_io.getvalue()).decode()
    
    return jsonify({"id": billet.id, "qr_code": qr_base64})

@ticket_bp.route('/tickets', methods=['GET'])
def get_tickets():
    tickets = Billet.query.all()
    return jsonify([{"id": t.id, "name": t.name, "email": t.email} for t in tickets])

@ticket_bp.route('/update_ticket/<id>', methods=['PUT'])
def update_ticket(id):
    data = request.json
    billet = Billet.query.get(id)
    if not billet:
        return jsonify({"error": "Billet non trouvé"}), 404
    billet.name = data.get('name', billet.name)
    billet.email = data.get('email', billet.email)
    db.session.commit()
    return jsonify({"message": "Billet mis à jour"})

@ticket_bp.route('/delete_ticket/<id>', methods=['DELETE'])
def delete_ticket(id):
    billet = Billet.query.get(id)
    if not billet:
        return jsonify({"error": "Billet non trouvé"}), 404
    db.session.delete(billet)
    db.session.commit()
    return jsonify({"message": "Billet supprimé"})