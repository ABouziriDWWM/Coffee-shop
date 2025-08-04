"""
Modèle Bill pour la gestion des additions du coffee shop
"""
from datetime import datetime
from bson import ObjectId
from marshmallow import Schema, fields, validate, post_load
from src.config.database import get_db

class BillItem:
    """Classe pour représenter un item dans une addition"""
    def __init__(self, product_name, quantity, unit_price):
        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = quantity * unit_price

class Bill:
    """Modèle pour les additions"""
    
    def __init__(self, order_id, customer_name, items, cashier="", discount=0, _id=None):
        self._id = _id or ObjectId()
        self.bill_number = self._generate_bill_number()
        self.order_id = ObjectId(order_id) if isinstance(order_id, str) else order_id
        self.customer_name = customer_name
        self.items = items
        self.subtotal = self._calculate_subtotal()
        self.discount = discount
        self.tax = self._calculate_tax()
        self.total_amount = self._calculate_total()
        self.payment_method = ""
        self.payment_status = "pending"
        self.bill_date = datetime.utcnow()
        self.cashier = cashier
    
    def _generate_bill_number(self):
        """Génère un numéro d'addition unique"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"BILL-{timestamp}"
    
    def _calculate_subtotal(self):
        """Calcule le sous-total avant taxes et remises"""
        return sum(item.total_price for item in self.items)
    
    def _calculate_tax(self):
        """Calcule les taxes (TVA à 20%)"""
        tax_rate = 0.20
        return (self.subtotal - self.discount) * tax_rate
    
    def _calculate_total(self):
        """Calcule le montant total de l'addition"""
        return self.subtotal - self.discount + self.tax
    
    def apply_discount(self, discount_amount):
        """Applique une remise et recalcule les totaux"""
        self.discount = discount_amount
        self.tax = self._calculate_tax()
        self.total_amount = self._calculate_total()
    
    def set_payment_method(self, method):
        """Définit la méthode de paiement"""
        valid_methods = ["cash", "card", "mobile", "check"]
        if method in valid_methods:
            self.payment_method = method
        else:
            raise ValueError(f"Méthode de paiement invalide: {method}")
    
    def mark_as_paid(self):
        """Marque l'addition comme payée"""
        self.payment_status = "paid"
    
    def to_dict(self):
        """Convertit l'addition en dictionnaire pour MongoDB"""
        return {
            "_id": self._id,
            "billNumber": self.bill_number,
            "orderId": self.order_id,
            "customerName": self.customer_name,
            "items": [
                {
                    "productName": item.product_name,
                    "quantity": item.quantity,
                    "unitPrice": item.unit_price,
                    "totalPrice": item.total_price
                } for item in self.items
            ],
            "subtotal": self.subtotal,
            "tax": self.tax,
            "discount": self.discount,
            "totalAmount": self.total_amount,
            "paymentMethod": self.payment_method,
            "paymentStatus": self.payment_status,
            "billDate": self.bill_date,
            "cashier": self.cashier
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crée un Bill à partir d'un dictionnaire MongoDB"""
        items = [
            BillItem(
                item["productName"],
                item["quantity"],
                item["unitPrice"]
            ) for item in data.get("items", [])
        ]
        
        bill = cls(
            order_id=data["orderId"],
            customer_name=data["customerName"],
            items=items,
            cashier=data.get("cashier", ""),
            discount=data.get("discount", 0),
            _id=data.get("_id")
        )
        
        # Restaurer les valeurs depuis la DB
        bill.bill_number = data.get("billNumber")
        bill.payment_method = data.get("paymentMethod", "")
        bill.payment_status = data.get("paymentStatus", "pending")
        bill.bill_date = data.get("billDate")
        bill.subtotal = data.get("subtotal")
        bill.tax = data.get("tax")
        bill.total_amount = data.get("totalAmount")
        
        return bill

class BillService:
    """Service pour les opérations CRUD sur les additions"""
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.bills
    
    def create_bill_from_order(self, order, cashier=""):
        """Crée une addition à partir d'une commande"""
        items = [
            BillItem(
                item.product_name,
                item.quantity,
                item.price
            ) for item in order.items
        ]
        
        bill = Bill(
            order_id=order._id,
            customer_name=order.customer_name,
            items=items,
            cashier=cashier
        )
        
        result = self.collection.insert_one(bill.to_dict())
        bill._id = result.inserted_id
        return bill
    
    def get_bill_by_id(self, bill_id):
        """Récupère une addition par son ID"""
        data = self.collection.find_one({"_id": ObjectId(bill_id)})
        return Bill.from_dict(data) if data else None
    
    def get_bill_by_number(self, bill_number):
        """Récupère une addition par son numéro"""
        data = self.collection.find_one({"billNumber": bill_number})
        return Bill.from_dict(data) if data else None
    
    def get_bills_by_order(self, order_id):
        """Récupère toutes les additions d'une commande"""
        cursor = self.collection.find({"orderId": ObjectId(order_id)})
        return [Bill.from_dict(data) for data in cursor]
    
    def get_all_bills(self, payment_status=None, limit=50):
        """Récupère toutes les additions avec filtrage optionnel"""
        query = {"paymentStatus": payment_status} if payment_status else {}
        cursor = self.collection.find(query).sort("billDate", -1).limit(limit)
        return [Bill.from_dict(data) for data in cursor]
    
    def update_payment_status(self, bill_id, payment_status, payment_method=None):
        """Met à jour le statut de paiement d'une addition"""
        valid_statuses = ["pending", "paid", "refunded"]
        if payment_status not in valid_statuses:
            raise ValueError(f"Statut de paiement invalide: {payment_status}")
        
        update_data = {"paymentStatus": payment_status}
        if payment_method:
            update_data["paymentMethod"] = payment_method
        
        result = self.collection.update_one(
            {"_id": ObjectId(bill_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def apply_discount_to_bill(self, bill_id, discount_amount):
        """Applique une remise à une addition"""
        bill = self.get_bill_by_id(bill_id)
        if not bill:
            return False
        
        bill.apply_discount(discount_amount)
        
        result = self.collection.update_one(
            {"_id": ObjectId(bill_id)},
            {"$set": {
                "discount": bill.discount,
                "tax": bill.tax,
                "totalAmount": bill.total_amount
            }}
        )
        return result.modified_count > 0
    
    def delete_bill(self, bill_id):
        """Supprime une addition (seulement si non payée)"""
        bill = self.get_bill_by_id(bill_id)
        if bill and bill.payment_status == "pending":
            result = self.collection.delete_one({"_id": ObjectId(bill_id)})
            return result.deleted_count > 0
        return False

# Schémas de validation avec Marshmallow
class BillItemSchema(Schema):
    productName = fields.Str(required=True, validate=validate.Length(min=1))
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    unitPrice = fields.Float(required=True, validate=validate.Range(min=0))

class BillSchema(Schema):
    orderId = fields.Str(required=True)
    customerName = fields.Str(required=True, validate=validate.Length(min=1))
    items = fields.List(fields.Nested(BillItemSchema), required=True, validate=validate.Length(min=1))
    cashier = fields.Str(missing="")
    discount = fields.Float(missing=0, validate=validate.Range(min=0))
    paymentMethod = fields.Str(validate=validate.OneOf(["cash", "card", "mobile", "check"]))
    
    @post_load
    def make_bill(self, data, **kwargs):
        return data

