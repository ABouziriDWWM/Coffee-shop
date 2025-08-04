# Plan d'Architecture - Coffee Shop CRUD

## Vue d'ensemble du projet

Site web CRUD modularisé et responsive pour un coffee shop avec un style inhabituel, utilisant HTML, CSS, JavaScript et MongoDB.

## Architecture modulaire

### Structure des dossiers
```
coffee-shop/
├── backend/
│   ├── models/
│   │   ├── Order.js
│   │   ├── Bill.js
│   │   └── Stock.js
│   ├── routes/
│   │   ├── orders.js
│   │   ├── bills.js
│   │   └── stock.js
│   ├── middleware/
│   │   └── validation.js
│   ├── config/
│   │   └── database.js
│   └── server.js
├── frontend/
│   ├── modules/
│   │   ├── orders/
│   │   ├── bills/
│   │   └── stock/
│   ├── shared/
│   │   ├── css/
│   │   ├── js/
│   │   └── components/
│   ├── assets/
│   └── index.html
└── package.json
```

## Modèles de données MongoDB

### Collection: Orders (Commandes)
```javascript
{
  _id: ObjectId,
  orderNumber: String (unique),
  customerName: String,
  items: [{
    productName: String,
    quantity: Number,
    price: Number,
    customizations: [String]
  }],
  totalAmount: Number,
  status: String, // 'pending', 'preparing', 'ready', 'completed'
  orderDate: Date,
  estimatedTime: Number, // minutes
  notes: String
}
```

### Collection: Bills (Additions)
```javascript
{
  _id: ObjectId,
  billNumber: String (unique),
  orderId: ObjectId,
  customerName: String,
  items: [{
    productName: String,
    quantity: Number,
    unitPrice: Number,
    totalPrice: Number
  }],
  subtotal: Number,
  tax: Number,
  discount: Number,
  totalAmount: Number,
  paymentMethod: String,
  paymentStatus: String, // 'pending', 'paid', 'refunded'
  billDate: Date,
  cashier: String
}
```

### Collection: Stock (Inventaire)
```javascript
{
  _id: ObjectId,
  productId: String (unique),
  productName: String,
  category: String, // 'coffee', 'pastry', 'equipment', 'supplies'
  currentStock: Number,
  minStock: Number,
  maxStock: Number,
  unit: String, // 'kg', 'pieces', 'liters'
  supplier: String,
  lastRestocked: Date,
  expirationDate: Date,
  costPrice: Number,
  sellingPrice: Number,
  status: String // 'available', 'low_stock', 'out_of_stock', 'expired'
}
```

## Fonctionnalités CRUD par module

### Module Commandes
- **Create**: Nouvelle commande avec sélection de produits
- **Read**: Liste des commandes, détails d'une commande
- **Update**: Modifier statut, ajouter/supprimer items
- **Delete**: Annuler une commande

### Module Additions
- **Create**: Générer addition à partir d'une commande
- **Read**: Liste des additions, détails d'une addition
- **Update**: Modifier méthode de paiement, appliquer remises
- **Delete**: Annuler une addition (avec conditions)

### Module Stock
- **Create**: Ajouter nouveau produit au stock
- **Read**: Vue d'ensemble du stock, détails par produit
- **Update**: Mettre à jour quantités, prix, informations produit
- **Delete**: Retirer un produit du catalogue

## Pages web principales

### 1. Dashboard principal
- Vue d'ensemble des commandes en cours
- Alertes stock faible
- Statistiques du jour

### 2. Page Commandes
- Interface de création de commandes
- Liste des commandes avec filtres
- Gestion du statut des commandes

### 3. Page Additions
- Génération automatique d'additions
- Historique des paiements
- Gestion des remises et taxes

### 4. Page Stock
- Inventaire en temps réel
- Alertes de réapprovisionnement
- Gestion des fournisseurs

## Validation des données

### Côté client (JavaScript)
- Validation des champs obligatoires
- Format des données (email, téléphone, prix)
- Cohérence des quantités et montants

### Côté serveur (Node.js/Express)
- Validation avec Joi ou express-validator
- Vérification de l'intégrité des données
- Contrôles métier (stock disponible, etc.)

## Style inhabituel - Concept initial

### Thème: "Coffee Lab Futuriste"
- Design inspiré des laboratoires scientifiques
- Éléments néomorphiques et glassmorphisme
- Animations fluides et micro-interactions
- Palette de couleurs terre/café avec accents néon
- Typographie moderne et géométrique

