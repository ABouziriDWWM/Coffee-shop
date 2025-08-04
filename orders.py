"""
Routes API pour la gestion des commandes
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from bson import ObjectId
from src.models.Order import OrderService, OrderSchema
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du blueprint
orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

# Instance du service
order_service = OrderService()
order_schema = OrderSchema()

@orders_bp.route('/', methods=['GET'])
def get_all_orders():
    """Récupère toutes les commandes avec filtrage optionnel"""
    try:
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        orders = order_service.get_all_orders(status=status, limit=limit)
        
        orders_data = []
        for order in orders:
            order_dict = order.to_dict()
            # Convertir ObjectId en string pour JSON
            order_dict['_id'] = str(order_dict['_id'])
            orders_data.append(order_dict)
        
        return jsonify({
            'success': True,
            'data': orders_data,
            'count': len(orders_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des commandes: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@orders_bp.route('/<order_id>', methods=['GET'])
def get_order_by_id(order_id):
    """Récupère une commande par son ID"""
    try:
        # Vérifier si c'est un ObjectId valide
        if not ObjectId.is_valid(order_id):
            return jsonify({
                'success': False,
                'error': 'ID de commande invalide'
            }), 400
        
        order = order_service.get_order_by_id(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'error': 'Commande non trouvée'
            }), 404
        
        order_dict = order.to_dict()
        order_dict['_id'] = str(order_dict['_id'])
        
        return jsonify({
            'success': True,
            'data': order_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la commande {order_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@orders_bp.route('/number/<order_number>', methods=['GET'])
def get_order_by_number(order_number):
    """Récupère une commande par son numéro"""
    try:
        order = order_service.get_order_by_number(order_number)
        
        if not order:
            return jsonify({
                'success': False,
                'error': 'Commande non trouvée'
            }), 404
        
        order_dict = order.to_dict()
        order_dict['_id'] = str(order_dict['_id'])
        
        return jsonify({
            'success': True,
            'data': order_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la commande {order_number}: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@orders_bp.route('/', methods=['POST'])
def create_order():
    """Crée une nouvelle commande"""
    try:
        # Validation des données
        try:
            order_data = order_schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'error': 'Données invalides',
                'details': err.messages
            }), 400
        
        # Créer la commande
        order = order_service.create_order(order_data)
        
        order_dict = order.to_dict()
        order_dict['_id'] = str(order_dict['_id'])
        
        return jsonify({
            'success': True,
            'message': 'Commande créée avec succès',
            'data': order_dict
        }), 201
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de la commande: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@orders_bp.route('/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Met à jour le statut d'une commande"""
    try:
        # Vérifier si c'est un ObjectId valide
        if not ObjectId.is_valid(order_id):
            return jsonify({
                'success': False,
                'error': 'ID de commande invalide'
            }), 400
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({
                'success': False,
                'error': 'Statut requis'
            }), 400
        
        # Mettre à jour le statut
        success = order_service.update_order_status(order_id, new_status)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Impossible de mettre à jour le statut'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Statut mis à jour avec succès'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du statut: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@orders_bp.route('/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Supprime une commande"""
    try:
        # Vérifier si c'est un ObjectId valide
        if not ObjectId.is_valid(order_id):
            return jsonify({
                'success': False,
                'error': 'ID de commande invalide'
            }), 400
        
        # Vérifier que la commande existe
        order = order_service.get_order_by_id(order_id)
        if not order:
            return jsonify({
                'success': False,
                'error': 'Commande non trouvée'
            }), 404
        
        # Vérifier que la commande peut être supprimée (statut pending)
        if order.status != 'pending':
            return jsonify({
                'success': False,
                'error': 'Seules les commandes en attente peuvent être supprimées'
            }), 400
        
        # Supprimer la commande
        success = order_service.delete_order(order_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Impossible de supprimer la commande'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Commande supprimée avec succès'
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la commande: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@orders_bp.route('/stats', methods=['GET'])
def get_order_stats():
    """Récupère les statistiques des commandes"""
    try:
        # Récupérer toutes les commandes pour calculer les stats
        all_orders = order_service.get_all_orders(limit=1000)
        
        stats = {
            'total': len(all_orders),
            'pending': len([o for o in all_orders if o.status == 'pending']),
            'preparing': len([o for o in all_orders if o.status == 'preparing']),
            'ready': len([o for o in all_orders if o.status == 'ready']),
            'completed': len([o for o in all_orders if o.status == 'completed']),
            'total_revenue': sum(o.total_amount for o in all_orders if o.status == 'completed'),
            'average_order_value': 0
        }
        
        if stats['completed'] > 0:
            completed_orders = [o for o in all_orders if o.status == 'completed']
            stats['average_order_value'] = sum(o.total_amount for o in completed_orders) / len(completed_orders)
        
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
@orders_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint non trouvé'
    }), 404

@orders_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Méthode non autorisée'
    }), 405

