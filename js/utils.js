/**
 * Utilitaires JavaScript pour Coffee Lab
 */

// Utilitaires de formatage
const Utils = {
  // Formatage des prix
  formatPrice: (price) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  },

  // Formatage des dates
  formatDate: (date) => {
    if (!date) return '-';
    const d = new Date(date);
    return new Intl.DateTimeFormat('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(d);
  },

  // Formatage des dates relatives
  formatRelativeDate: (date) => {
    if (!date) return '-';
    const now = new Date();
    const d = new Date(date);
    const diffMs = now - d;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins} min`;
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    if (diffDays < 7) return `Il y a ${diffDays} jour${diffDays > 1 ? 's' : ''}`;
    
    return Utils.formatDate(date);
  },

  // Formatage des quantités
  formatQuantity: (quantity, unit) => {
    return `${quantity} ${unit}`;
  },

  // Génération d'ID uniques
  generateId: () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  },

  // Debounce pour les recherches
  debounce: (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Validation d'email
  isValidEmail: (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  // Validation de numéro de téléphone
  isValidPhone: (phone) => {
    const re = /^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$/;
    return re.test(phone);
  },

  // Capitalisation
  capitalize: (str) => {
    return str.charAt(0).toUpperCase() + str.slice(1);
  },

  // Traduction des statuts
  translateStatus: (status) => {
    const translations = {
      'pending': 'En Attente',
      'preparing': 'En Préparation',
      'ready': 'Prête',
      'completed': 'Terminée',
      'paid': 'Payé',
      'refunded': 'Remboursé',
      'available': 'Disponible',
      'low_stock': 'Stock Faible',
      'out_of_stock': 'Rupture',
      'expired': 'Expiré'
    };
    return translations[status] || status;
  },

  // Traduction des catégories
  translateCategory: (category) => {
    const translations = {
      'coffee': 'Café',
      'pastry': 'Pâtisserie',
      'equipment': 'Équipement',
      'supplies': 'Fournitures'
    };
    return translations[category] || category;
  },

  // Traduction des méthodes de paiement
  translatePaymentMethod: (method) => {
    const translations = {
      'cash': 'Espèces',
      'card': 'Carte',
      'mobile': 'Mobile',
      'check': 'Chèque'
    };
    return translations[method] || method;
  },

  // Calcul du pourcentage de stock
  calculateStockPercentage: (current, max) => {
    if (max === 0) return 0;
    return Math.round((current / max) * 100);
  },

  // Détermination du niveau de stock
  getStockLevel: (current, min, max) => {
    const percentage = Utils.calculateStockPercentage(current, max);
    if (current <= 0) return 'empty';
    if (current <= min) return 'low';
    if (percentage < 50) return 'medium';
    return 'high';
  },

  // Copie dans le presse-papiers
  copyToClipboard: async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      // Fallback pour les navigateurs plus anciens
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        document.body.removeChild(textArea);
        return true;
      } catch (err) {
        document.body.removeChild(textArea);
        return false;
      }
    }
  },

  // Téléchargement de fichier
  downloadFile: (data, filename, type = 'application/json') => {
    const blob = new Blob([data], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },

  // Validation de formulaire
  validateForm: (formData, rules) => {
    const errors = {};
    
    for (const [field, rule] of Object.entries(rules)) {
      const value = formData[field];
      
      if (rule.required && (!value || value.toString().trim() === '')) {
        errors[field] = 'Ce champ est requis';
        continue;
      }
      
      if (value && rule.type === 'email' && !Utils.isValidEmail(value)) {
        errors[field] = 'Format d\'email invalide';
        continue;
      }
      
      if (value && rule.type === 'phone' && !Utils.isValidPhone(value)) {
        errors[field] = 'Format de téléphone invalide';
        continue;
      }
      
      if (value && rule.type === 'number') {
        const num = parseFloat(value);
        if (isNaN(num)) {
          errors[field] = 'Doit être un nombre';
          continue;
        }
        if (rule.min !== undefined && num < rule.min) {
          errors[field] = `Doit être supérieur ou égal à ${rule.min}`;
          continue;
        }
        if (rule.max !== undefined && num > rule.max) {
          errors[field] = `Doit être inférieur ou égal à ${rule.max}`;
          continue;
        }
      }
      
      if (value && rule.minLength && value.length < rule.minLength) {
        errors[field] = `Doit contenir au moins ${rule.minLength} caractères`;
        continue;
      }
      
      if (value && rule.maxLength && value.length > rule.maxLength) {
        errors[field] = `Doit contenir au maximum ${rule.maxLength} caractères`;
        continue;
      }
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  },

  // Stockage local
  storage: {
    set: (key, value) => {
      try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
      } catch (err) {
        console.error('Erreur de stockage local:', err);
        return false;
      }
    },
    
    get: (key, defaultValue = null) => {
      try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
      } catch (err) {
        console.error('Erreur de lecture du stockage local:', err);
        return defaultValue;
      }
    },
    
    remove: (key) => {
      try {
        localStorage.removeItem(key);
        return true;
      } catch (err) {
        console.error('Erreur de suppression du stockage local:', err);
        return false;
      }
    }
  },

  // Gestion des erreurs
  handleError: (error, context = '') => {
    console.error(`Erreur ${context}:`, error);
    
    let message = 'Une erreur inattendue s\'est produite';
    
    if (error.response) {
      // Erreur de réponse HTTP
      if (error.response.data && error.response.data.error) {
        message = error.response.data.error;
      } else {
        message = `Erreur ${error.response.status}: ${error.response.statusText}`;
      }
    } else if (error.message) {
      message = error.message;
    }
    
    return message;
  }
};

// Export pour utilisation dans d'autres modules
window.Utils = Utils;

