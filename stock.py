from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from marshmallow import ValidationError
import logging

from src.models.Stock import StockService, StockSchema

logger = logging.getLogger(__name__)

# Création du blueprint pour les routes stock
stock_bp = Blueprint('stock', __name__, url_prefix='/api/stock')

# Instance du service stock
stock_service = StockService()
stock_schema = StockSchema()

@stock_bp.route('/', methods=['GET'])
def get_all_stock():
    """Récupère tous les produits en stock avec filtres optionnels"""
    try:
        # Paramètres de requête
        category = request.args.get('category')
        status = request.args.get('status')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Construire les filtres
        filters = {}
        if category:
            filters['category'] = category
        if status:
            filters['status'] = status
        if search:
            filters['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        
        # Récupérer les produits
        products = stock_service.get_all_stock(filters, page, limit)
        
        return jsonify({
            'success': True,
            'data': [product.to_dict() for product in products],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': stock_service.count_stock(filters)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du stock: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la récupération du stock'
        }), 500

@stock_bp.route('/<product_id>', methods=['GET'])
def get_stock_by_id(product_id):
    """Récupère un produit par son ID"""
    try:
        product = stock_service.get_stock_by_id(product_id)
        if not product:
            return jsonify({
                'success': False,
                'error': 'Produit non trouvé'
            }), 404
            
        return jsonify({
            'success': True,
            'data': product.to_dict()
        }), 200
        
    except InvalidId:
        return jsonify({
            'success': False,
            'error': 'ID de produit invalide'
        }), 400
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du produit {product_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la récupération du produit'
        }), 500

@stock_bp.route('/', methods=['POST'])
def create_stock():
    """Crée un nouveau produit en stock"""
    try:
        # Validation des données
        data = stock_schema.load(request.json)
        
        # Créer le produit
        product = stock_service.create_stock(data)
        
        return jsonify({
            'success': True,
            'message': 'Produit créé avec succès',
            'data': product.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Données invalides',
            'details': e.messages
        }), 400
    except Exception as e:
        logger.error(f"Erreur lors de la création du produit: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la création du produit'
        }), 500

@stock_bp.route('/<product_id>', methods=['PUT'])
def update_stock(product_id):
    """Met à jour un produit"""
    try:
        # Validation des données
        data = stock_schema.load(request.json, partial=True)
        
        # Mettre à jour le produit
        product = stock_service.update_stock(product_id, data)
        if not product:
            return jsonify({
                'success': False,
                'error': 'Produit non trouvé'
            }), 404
            
        return jsonify({
            'success': True,
            'message': 'Produit mis à jour avec succès',
            'data': product.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Données invalides',
            'details': e.messages
        }), 400
    except InvalidId:
        return jsonify({
            'success': False,
            'error': 'ID de produit invalide'
        }), 400
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du produit {product_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la mise à jour du produit'
        }), 500

@stock_bp.route('/<product_id>', methods=['DELETE'])
def delete_stock(product_id):
    """Supprime un produit"""
    try:
        success = stock_service.delete_stock(product_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Produit non trouvé'
            }), 404
            
        return jsonify({
            'success': True,
            'message': 'Produit supprimé avec succès'
        }), 200
        
    except InvalidId:
        return jsonify({
            'success': False,
            'error': 'ID de produit invalide'
        }), 400
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du produit {product_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la suppression du produit'
        }), 500

@stock_bp.route('/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts():
    """Récupère les alertes de stock faible"""
    try:
        alerts = stock_service.get_low_stock_alerts()
        
        return jsonify({
            'success': True,
            'data': [alert.to_dict() for alert in alerts],
            'count': len(alerts)
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des alertes: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la récupération des alertes'
        }), 500

@stock_bp.route('/categories', methods=['GET'])
def get_categories():
    """Récupère toutes les catégories de produits"""
    try:
        categories = stock_service.get_categories()
        
        return jsonify({
            'success': True,
            'data': categories
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des catégories: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la récupération des catégories'
        }), 500

