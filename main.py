import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.config.database import db_config, init_collections
from src.routes.orders import orders_bp
from src.routes.bills import bills_bp
from src.routes.stock import stock_bp
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'coffee_shop_secret_key_2024'

# Configuration CORS pour permettre les requêtes cross-origin
CORS(app, origins="*")

# Enregistrement des blueprints
app.register_blueprint(orders_bp)
app.register_blueprint(bills_bp)
app.register_blueprint(stock_bp)

# Route de santé pour vérifier que l'API fonctionne
@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé de l'API"""
    try:
        # Tester la connexion à MongoDB
        db = db_config.get_database()
        db.command('ping')
        
        return jsonify({
            'success': True,
            'message': 'API Coffee Shop opérationnelle',
            'database': 'MongoDB connecté',
            'version': '1.0.0'
        }), 200
    except Exception as e:
        logger.error(f"Erreur de santé de l'API: {e}")
        return jsonify({
            'success': False,
            'message': 'Problème de connexion à la base de données',
            'error': str(e)
        }), 500

# Route pour obtenir les informations de l'API
@app.route('/api/info', methods=['GET'])
def api_info():
    """Informations sur l'API Coffee Shop"""
    return jsonify({
        'name': 'Coffee Shop CRUD API',
        'version': '1.0.0',
        'description': 'API pour la gestion d\'un coffee shop avec style futuriste',
        'endpoints': {
            'orders': '/api/orders',
            'bills': '/api/bills',
            'stock': '/api/stock',
            'health': '/api/health'
        },
        'features': [
            'Gestion des commandes',
            'Gestion des additions',
            'Gestion du stock',
            'Validation des données',
            'Alertes de stock'
        ]
    }), 200

# Gestionnaire d'erreurs global
@app.errorhandler(404)
def not_found(error):
    if '/api/' in str(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint API non trouvé'
        }), 404
    # Pour les autres routes, servir le frontend
    return serve('')

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erreur interne du serveur: {error}")
    return jsonify({
        'success': False,
        'error': 'Erreur interne du serveur'
    }), 500

# Routes pour servir le frontend (SPA)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Sert les fichiers statiques du frontend"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return jsonify({
            'success': False,
            'error': 'Dossier statique non configuré'
        }), 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'success': False,
                'message': 'Frontend non déployé',
                'info': 'Utilisez les endpoints API: /api/health, /api/info'
            }), 404

def initialize_app():
    """Initialise l'application et la base de données"""
    try:
        # Connexion à MongoDB
        if db_config.connect():
            logger.info("Connexion à MongoDB réussie")
            # Initialiser les collections et index
            init_collections()
            logger.info("Collections MongoDB initialisées")
        else:
            logger.error("Échec de connexion à MongoDB")
            
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation: {e}")

if __name__ == '__main__':
    # Initialiser l'application
    initialize_app()
    
    # Démarrer le serveur
    logger.info("Démarrage du serveur Coffee Shop API...")
    app.run(host='0.0.0.0', port=5000, debug=True)

