"""
Routes API pour la gestion des additions
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from bson import ObjectId
from src.models.Bill import BillService, BillSchema
from src.models.Order import OrderService
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du blueprint
bills_bp = Blueprint('bills', __name__, url_prefix='/api/bills')

# Instances des services
bill_service = BillService()
order_service = OrderService()
bill_schema = BillSchema()

@bills_bp.route('/', methods=['GET'])
def get_all_bills():
    """Récupère toutes les additions avec filtrage optionnel"""
    try:
        payment_status = request.args.get('paymentStatus')
        limit = int(request.args.get('limit', 50))
        
        bills = bill_service.get_all_bills(payment_status=payment_status, limit=limit)
        
        bills_data = []
        for bill in bills:
            bill_dict = bill.to_dict()
            # Convertir ObjectId en string pour JSON
            bill_dict['_id'] = str(bill_dict['_id'])
            bill_dict['orderId'] = str(bill_dict['orderId'])
            bills_data.append(bill_dict)
        
        return jsonify({
            'success': True,
            'data': bills_data,
            'count': len(bills_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des additions: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@bills_bp.route('/<bill_id>', methods=['GET'])
def get_bill_by_id(bill_id):
    """Récupère une addition par son ID"""
    try:
        # Vérifier si c'est un ObjectId valide
        if not ObjectId.is_valid(bill_id):
            return jsonify({
                'success': False,
                'error': 'ID d\'addition invalide'
            }), 400
        
        bill = bill_service.get_bill_by_id(bill_id)
        
        if not bill:
            return jsonify({
                'success': False,
                'error': 'Addition non trouvée'
            }), 404
        
        bill_dict = bill.to_dict()
        bill_dict['_id'] = str(bill_dict['_id'])
        bill_dict['orderId'] = str(bill_dict['orderId'])
        
        return jsonify({
            'success': True,
            'data': bill_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'addition {bill_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@bills_bp.route('/number/<bill_number>', methods=['GET'])
def get_bill_by_number(bill_number):
    """Récupère une addition par son numéro"""
    try:
        bill = bill_service.get_bill_by_number(bill_number)
        
        if not bill:
            return jsonify({
                'success': False,
                'error': 'Addition non trouvée'
            }), 404
        
        bill_dict = bill.to_dict()
        bill_dict['_id'] = str(bill_dict['_id'])
        bill_dict['orderId'] = str(bill_dict['orderId'])
        
        return jsonify({
            'success': True,
            'data': bill_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'addition {bill_number}: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@bills_bp.route('/order/<order_id>', methods=['GET'])
def get_bills_by_order(order_id):
    """Récupère toutes les additions d'une commande"""
    try:
        # Vérifier si c'est un ObjectId valide
        if not ObjectId.is_valid(order_id):
            return jsonify({
                'success': False,
                'error': 'ID de commande invalide'
            }), 400
        
        bills = bill_service.get_bills_by_order(order_id)
        
        bills_data = []
        for bill in bills:
            bill_dict = bill.to_dict()
            bill_dict['_id'] = str(bill_dict['_id'])
            bill_dict['orderId'] = str(bill_dict['orderId'])
            bills_data.append(bill_dict)
        
        return jsonify({
            'success': True,
            'data': bills_data,
            'count': len(bills_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des additions pour la commande {order_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@bills_bp.route('/from-order/<order_id>', methods=['POST'])
def create_bill_from_order(order_id):
    """Crée une addition à partir d'une commande"""
    try:
        # Vérifier si c'est un ObjectId valide
        if not ObjectId.is_valid(order_id):
            return jsonify({
                'success': False,
                'error': 'ID de commande invalide'
            }), 400
        
        # Récupérer la commande
        order = order_service.get_order_by_id(order_id)
        if not order:
            return jsonify({
                'success': False,
                'error': 'Commande non trouvée'
            }), 404
        
        # Vérifier que la commande est prête ou terminée
        if order.status not in ['ready', 'completed']:
            return jsonify({
                'success': False,
                'error': 'La commande doit être prête ou terminée pour générer une addition'
            }), 400
        
        # Récupérer le caissier depuis les données de la requête
        data = request.get_json() or {}
        cashier = data.get('cashier', '')
        
        # Créer l'addition
        bill = bill_service.create_bill_from_order(order, cashier)
        
        bill_dict = bill.to_dict()
        bill_dict['_id'] = str(bill_dict['_id'])
        bill_dict['orderId'] = str(bill_dict['orderId'])
        
        return jsonify({
            'success': True,
            'message': 'Addition créée avec succès',
            'data': bill_dict
        }), 201
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'addition: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@bills_bp.route('/<bill_id>/payment', methods=['PUT'])
def update_payment_status(bill_id):
    """Met à jour le statut de paiement d'une addition"""
    try:
        # Vérifier si c'est un ObjectId valide
        if not ObjectId.is_valid(bill_id):
            return jsonify({
                'success': False,
                'error': 'ID d\'addition invalide'
            }), 400
        
        data = request.get_json()
        payment_status = data.get('paymentStatus')
        payment_method = data.get('paymentMethod')
        
        if not payment_status:
            return jsonify({
                'success': False,
                'error': 'Statut de paiement requis'
            }), 400
        
        # Mettre à jour le statut de paiement
        success = bill_service.update_payment_status(bill_id, payment_status, payment_method)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Impossible de mettre à jour le statut de paiement'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Statut de paiement mis à jour avec succès'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du paiement: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@bills_bp.route('/<bill_id>/discount', methods=['PUT'])
def apply_discount(bill_id):
    """Applique une remise à une addition"""
    try:
        # Vérifier si c'est un ObjectId valide
        if not ObjectId.is_valid(bill_id):
            return jsonify({
                'success': False,
                'error': 'ID d\'addition invalide'
            }), 400
        
        data = request.get_json()
        discount_amount = data.get('discountAmount')
        
        if discount_amount is None or discount_amount < 0:
            return jsonify({
                'success': False,
                'error': 'Montant de remise invalide'
            }), 400
        
        # Appliquer la remise
        success = bill_service.apply_discount_to_bill(bill_id, discount_amount)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Impossible d\'appliquer la remise'
            }), 400
        
        # Récupérer l'addition mise à jour
        bill = bill_service.get_bill_by_id(bill_id)
        bill_dict = bill.to_dict()
        bill_dict['_id'] = str(bill_dict['_id'])
        bill_dict['orderId'] = str(bill_dict['orderId'])
        
        return jsonify({
            'success': True,
            'message': 'Remise appliquée avec succès',
            'data': bill_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de l'application de la remise: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@bills_bp.route('/<bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    """Supprime une addition (seulement si non payée)"""
    try:
        # Vérifier si c'est un ObjectId valide
        if not ObjectId.is_valid(bill_id):
            return jsonify({
                'success': False,
                'error': 'ID d\'addition invalide'
            }), 400
        
        # Supprimer l'addition
        success = bill_service.delete_bill(bill_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Impossible de supprimer l\'addition (peut-être déjà payée)'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Addition supprimée avec succès'
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'addition: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@bills_bp.route('/stats', methods=['GET'])
def get_bill_stats():
    """Récupère les statistiques des additions"""
    try:
        # Récupérer toutes les additions pour calculer les stats
        all_bills = bill_service.get_all_bills(limit=1000)
        
        stats = {
            'total': len(all_bills),
            'pending': len([b for b in all_bills if b.payment_status == 'pending']),
            'paid': len([b for b in all_bills if b.payment_status == 'paid']),
            'refunded': len([b for b in all_bills if b.payment_status == 'refunded']),
            'total_revenue': sum(b.total_amount for b in all_bills if b.payment_status == 'paid'),
            'total_tax': sum(b.tax for b in all_bills if b.payment_status == 'paid'),
            'total_discounts': sum(b.discount for b in all_bills),
            'average_bill_amount': 0
        }
        
        paid_bills = [b for b in all_bills if b.payment_status == 'paid']
        if len(paid_bills) > 0:
            stats['average_bill_amount'] = sum(b.total_amount for b in paid_bills) / len(paid_bills)
        
        # Statistiques par méthode de paiement
        payment_methods = {}
        for bill in paid_bills:
            method = bill.payment_method or 'unknown'
            if method not in payment_methods:
                payment_methods[method] = {'count': 0, 'amount': 0}
            payment_methods[method]['count'] += 1
            payment_methods[method]['amount'] += bill.total_amount
        
        stats['payment_methods'] = payment_methods
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul des statistiques: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

# Gestionnaire d'erreurs pour le blueprint
@bills_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint non trouvé'
    }), 404

@bills_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Méthode non autorisée'
    }), 405

