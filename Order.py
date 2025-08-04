"""
Modèle Order pour la gestion des commandes du coffee shop
"""
from datetime import datetime
from bson import ObjectId
from marshmallow import Schema, fields, validate, post_load
from src.config.database import get_db

class OrderItem:
    """Classe pour représenter un item dans une commande"""
    def __init__(self, product_name, quantity, price, customizations=None):
        self.product_name = product_name
        self.quantity = quantity
        self.price = price
        self.customizations = customizations or []

class Order:
    """Modèle pour les commandes"""
    
    def __init__(self, customer_name, items, notes="", _id=None):
        self._id = _id or ObjectId()
        self.order_number = self._generate_order_number()
        self.customer_name = customer_name
        self.items = items
        self.total_amount = self._calculate_total()
        self.status = "pending"
        self.order_date = datetime.utcnow()
        self.estimated_time = self._calculate_estimated_time()
        self.notes = notes
    
    def _generate_order_number(self):
        """Génère un numéro de commande unique"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORD-{timestamp}"
    
    def _calculate_total(self):
        """Calcule le montant total de la commande"""
        return sum(item.quantity * item.price for item in self.items)
    
    def _calculate_estimated_time(self):
        """Calcule le temps estimé de préparation en minutes"""
        base_time = 5  # 5 minutes de base
        item_time = len(self.items) * 3  # 3 minutes par item
        return base_time + item_time
    
    def to_dict(self):
        """Convertit l'ordre en dictionnaire pour MongoDB"""
        return {
            "_id": self._id,
            "orderNumber": self.order_number,
            "customerName": self.customer_name,
            "items": [
                {
                    "productName": item.product_name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "customizations": item.customizations
                } for item in self.items
            ],
            "totalAmount": self.total_amount,
            "status": self.status,
            "orderDate": self.order_date,
            "estimatedTime": self.estimated_time,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crée un Order à partir d'un dictionnaire MongoDB"""
        items = [
            OrderItem(
                item["productName"],
                item["quantity"],
                item["price"],
                item.get("customizations", [])
            ) for item in data.get("items", [])
        ]
        
        order = cls(
            customer_name=data["customerName"],
            items=items,
            notes=data.get("notes", ""),
            _id=data.get("_id")
        )
        
        # Restaurer les valeurs depuis la DB
        order.order_number = data.get("orderNumber")
        order.status = data.get("status", "pending")
        order.order_date = data.get("orderDate")
        order.estimated_time = data.get("estimatedTime")
        order.total_amount = data.get("totalAmount")
        
        return order

class OrderService:
    """Service pour les opérations CRUD sur les commandes"""
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.orders
    
    def create_order(self, order_data):
        """Crée une nouvelle commande"""
        items = [
            OrderItem(
                item["productName"],
                item["quantity"],
                item["price"],
                item.get("customizations", [])
            ) for item in order_data.get("items", [])
        ]
        
        order = Order(
            customer_name=order_data["customerName"],
            items=items,
            notes=order_data.get("notes", "")
        )
        
        result = self.collection.insert_one(order.to_dict())
        order._id = result.inserted_id
        return order
    
    def get_order_by_id(self, order_id):
        """Récupère une commande par son ID"""
        data = self.collection.find_one({"_id": ObjectId(order_id)})
        return Order.from_dict(data) if data else None
    
    def get_order_by_number(self, order_number):
        """Récupère une commande par son numéro"""
        data = self.collection.find_one({"orderNumber": order_number})
        return Order.from_dict(data) if data else None
    
    def get_all_orders(self, status=None, limit=50):
        """Récupère toutes les commandes avec filtrage optionnel"""
        query = {"status": status} if status else {}
        cursor = self.collection.find(query).sort("orderDate", -1).limit(limit)
        return [Order.from_dict(data) for data in cursor]
    
    def update_order_status(self, order_id, new_status):
        """Met à jour le statut d'une commande"""
        valid_statuses = ["pending", "preparing", "ready", "completed"]
        if new_status not in valid_statuses:
            raise ValueError(f"Statut invalide: {new_status}")
        
        result = self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": new_status}}
        )
        return result.modified_count > 0
    
    def delete_order(self, order_id):
        """Supprime une commande"""
        result = self.collection.delete_one({"_id": ObjectId(order_id)})
        return result.deleted_count > 0

# Schémas de validation avec Marshmallow
class OrderItemSchema(Schema):
    productName = fields.Str(required=True, validate=validate.Length(min=1))
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    customizations = fields.List(fields.Str(), missing=[])

class OrderSchema(Schema):
    customerName = fields.Str(required=True, validate=validate.Length(min=1))
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1))
    notes = fields.Str(missing="")
    
    @post_load
    def make_order(self, data, **kwargs):
        return data

