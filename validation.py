"""
Middleware de validation pour l'application Coffee Shop
"""
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

def validate_json(f):
    """Décorateur pour valider que la requête contient du JSON valide"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json'
                }), 400
            
            if request.get_json() is None:
                return jsonify({
                    'success': False,
                    'error': 'Corps de requête JSON invalide'
                }), 400
        
        return f(*args, **kwargs)
    return decorated_function

def validate_required_fields(required_fields):
    """Décorateur pour valider la présence de champs requis"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                data = request.get_json()
                missing_fields = []
                
                for field in required_fields:
                    if field not in data or data[field] is None or data[field] == '':
                        missing_fields.append(field)
                
                if missing_fields:
                    return jsonify({
                        'success': False,
                        'error': 'Champs requis manquants',
                        'missing_fields': missing_fields
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_positive_number(field_name):
    """Décorateur pour valider qu'un champ est un nombre positif"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                data = request.get_json()
                
                if field_name in data:
                    try:
                        value = float(data[field_name])
                        if value < 0:
                            return jsonify({
                                'success': False,
                                'error': f'{field_name} doit être un nombre positif'
                            }), 400
                    except (ValueError, TypeError):
                        return jsonify({
                            'success': False,
                            'error': f'{field_name} doit être un nombre valide'
                        }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_email(field_name='email'):
    """Décorateur pour valider le format d'un email"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                data = request.get_json()
                
                if field_name in data and data[field_name]:
                    email = data[field_name]
                    if '@' not in email or '.' not in email.split('@')[-1]:
                        return jsonify({
                            'success': False,
                            'error': f'Format d\'email invalide pour {field_name}'
                        }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_string_length(field_name, min_length=1, max_length=255):
    """Décorateur pour valider la longueur d'une chaîne"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                data = request.get_json()
                
                if field_name in data and data[field_name] is not None:
                    value = str(data[field_name])
                    if len(value) < min_length or len(value) > max_length:
                        return jsonify({
                            'success': False,
                            'error': f'{field_name} doit contenir entre {min_length} et {max_length} caractères'
                        }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_choice(field_name, choices):
    """Décorateur pour valider qu'une valeur fait partie d'une liste de choix"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                data = request.get_json()
                
                if field_name in data and data[field_name] is not None:
                    if data[field_name] not in choices:
                        return jsonify({
                            'success': False,
                            'error': f'{field_name} doit être l\'une des valeurs suivantes: {", ".join(choices)}'
                        }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_request():
    """Décorateur pour logger les requêtes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger.info(f"{request.method} {request.path} - IP: {request.remote_addr}")
            
            if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
                # Logger les données de la requête (sans les mots de passe)
                data = request.get_json()
                safe_data = {k: v for k, v in data.items() if 'password' not in k.lower()}
                logger.debug(f"Request data: {safe_data}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def handle_errors(f):
    """Décorateur pour gérer les erreurs de manière uniforme"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Erreur de validation: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    return decorated_function

# Middleware pour valider les paramètres de pagination
def validate_pagination():
    """Valide les paramètres de pagination dans les query parameters"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            page = request.args.get('page', '1')
            limit = request.args.get('limit', '50')
            
            try:
                page = int(page)
                limit = int(limit)
                
                if page < 1:
                    return jsonify({
                        'success': False,
                        'error': 'Le numéro de page doit être supérieur à 0'
                    }), 400
                
                if limit < 1 or limit > 100:
                    return jsonify({
                        'success': False,
                        'error': 'La limite doit être entre 1 et 100'
                    }), 400
                
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Paramètres de pagination invalides'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

