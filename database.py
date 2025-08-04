"""
Configuration de la base de données MongoDB pour le Coffee Shop CRUD
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

# Configuration de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Configuration et connexion à MongoDB"""
    
    def __init__(self):
        # Configuration par défaut pour développement local
        self.MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.DATABASE_NAME = os.getenv('DATABASE_NAME', 'coffee_shop_db')
        self.client = None
        self.db = None
    
    def connect(self):
        """Établit la connexion à MongoDB"""
        try:
            self.client = MongoClient(self.MONGO_URI)
            # Test de la connexion
            self.client.admin.command('ping')
            self.db = self.client[self.DATABASE_NAME]
            logger.info(f"Connexion réussie à MongoDB: {self.DATABASE_NAME}")
            return True
        except ConnectionFailure as e:
            logger.error(f"Échec de connexion à MongoDB: {e}")
            return False
    
    def get_database(self):
        """Retourne l'instance de la base de données"""
        if self.db is None:
            self.connect()
        return self.db
    
    def close_connection(self):
        """Ferme la connexion à MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Connexion MongoDB fermée")

# Instance globale de configuration
db_config = DatabaseConfig()

def get_db():
    """Fonction utilitaire pour obtenir la base de données"""
    return db_config.get_database()

def init_collections():
    """Initialise les collections avec des index pour optimiser les performances"""
    db = get_db()
    
    # Index pour la collection orders
    db.orders.create_index("orderNumber", unique=True)
    db.orders.create_index("status")
    db.orders.create_index("orderDate")
    
    # Index pour la collection bills
    db.bills.create_index("billNumber", unique=True)
    db.bills.create_index("orderId")
    db.bills.create_index("paymentStatus")
    
    # Index pour la collection stock
    db.stock.create_index("productId", unique=True)
    db.stock.create_index("category")
    db.stock.create_index("status")
    
    logger.info("Collections et index initialisés")

