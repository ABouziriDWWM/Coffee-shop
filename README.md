# Coffee Shop CRUD - Site Web

Site web CRUD modularisé et responsive pour un coffee shop , utilisant HTML, CSS, JavaScript, python et MongoDB.

## Fonctionnalités

- **Gestion des commandes** : Création, modification et suivi des commandes
- **Gestion des additions** : Génération automatique et gestion des paiements
- **Gestion du stock** : Inventaire en temps réel avec alertes de réapprovisionnement
- **Design futuriste** : Interface utilisateur unique avec néomorphisme et glassmorphisme
- **Responsive** : Compatible desktop et mobile
- **Validation des données** : Côté client et serveur

## Technologies

- **Backend** : Flask (Python)
- **Base de données** : MongoDB
- **Frontend** : HTML5, CSS3, JavaScript (Vanilla)


## Structure du projet finale

```
coffee-shop/
├── backend/                 # Application Flask
│   ├── src/
│   │   ├── models/         # Modèles MongoDB
│   │   ├── routes/         # Routes API
│   │   ├── config/         # Configuration
│   │   ├── middleware/     # Middleware de validation
│   │   └── static/         # Fichiers statiques frontend
│   └── venv/               # Environnement virtuel Python
├── frontend/               # Code source frontend
│   ├── modules/            # Modules par fonctionnalité
│   ├── shared/             # Composants partagés
│   └── assets/             # Images et ressources
├── docs/                   # Documentation
└── package.json            # Configuration du projet
```

## Installation et démarrage

1. Cloner le projet
2. Installer les dépendances backend :
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configurer MongoDB (voir docs/architecture_plan.md)
4. Démarrer l'application :
   ```bash
   python src/main.py
   ```

## Documentation

- [Plan d'architecture](docs/architecture_plan.md)
- [Concept de design](docs/design_concept.md)


