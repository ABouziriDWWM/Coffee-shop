/**
 * Client API pour Coffee Lab
 */

class ApiClient {
  constructor() {
    this.baseURL = '/api';
    this.defaultHeaders = {
      'Content-Type': 'application/json'
    };
  }

  // Méthode générique pour les requêtes
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`Erreur API ${endpoint}:`, error);
      throw error;
    }
  }

  // Méthodes HTTP de base
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // === API COMMANDES ===

  // Récupérer toutes les commandes
  async getOrders(filters = {}) {
    return this.get('/orders', filters);
  }

  // Récupérer une commande par ID
  async getOrder(id) {
    return this.get(`/orders/${id}`);
  }

  // Récupérer une commande par numéro
  async getOrderByNumber(orderNumber) {
    return this.get(`/orders/number/${orderNumber}`);
  }

  // Créer une nouvelle commande
  async createOrder(orderData) {
    return this.post('/orders', orderData);
  }

  // Mettre à jour le statut d'une commande
  async updateOrderStatus(id, status) {
    return this.put(`/orders/${id}/status`, { status });
  }

  // Supprimer une commande
  async deleteOrder(id) {
    return this.delete(`/orders/${id}`);
  }

  // Récupérer les statistiques des commandes
  async getOrderStats() {
    return this.get('/orders/stats');
  }

  // === API ADDITIONS ===

  // Récupérer toutes les additions
  async getBills(filters = {}) {
    return this.get('/bills', filters);
  }

  // Récupérer une addition par ID
  async getBill(id) {
    return this.get(`/bills/${id}`);
  }

  // Récupérer une addition par numéro
  async getBillByNumber(billNumber) {
    return this.get(`/bills/number/${billNumber}`);
  }

  // Récupérer les additions d'une commande
  async getBillsByOrder(orderId) {
    return this.get(`/bills/order/${orderId}`);
  }

  // Créer une addition à partir d'une commande
  async createBillFromOrder(orderId, cashier = '') {
    return this.post(`/bills/from-order/${orderId}`, { cashier });
  }

  // Mettre à jour le statut de paiement
  async updatePaymentStatus(id, paymentStatus, paymentMethod = null) {
    return this.put(`/bills/${id}/payment`, { paymentStatus, paymentMethod });
  }

  // Appliquer une remise
  async applyDiscount(id, discountAmount) {
    return this.put(`/bills/${id}/discount`, { discountAmount });
  }

  // Supprimer une addition
  async deleteBill(id) {
    return this.delete(`/bills/${id}`);
  }

  // Récupérer les statistiques des additions
  async getBillStats() {
    return this.get('/bills/stats');
  }

  // === API STOCK ===

  // Récupérer tous les produits
  async getProducts(filters = {}) {
    return this.get('/stock', filters);
  }

  // Récupérer un produit par ID
  async getProduct(id) {
    return this.get(`/stock/${id}`);
  }

  // Récupérer un produit par productId
  async getProductByProductId(productId) {
    return this.get(`/stock/product-id/${productId}`);
  }

  // Créer un nouveau produit
  async createProduct(productData) {
    return this.post('/stock', productData);
  }

  // Mettre à jour la quantité en stock
  async updateStockQuantity(id, quantity, operation = 'add') {
    return this.put(`/stock/${id}/quantity`, { quantity, operation });
  }

  // Mettre à jour les informations d'un produit
  async updateProduct(id, updateData) {
    return this.put(`/stock/${id}`, updateData);
  }

  // Supprimer un produit
  async deleteProduct(id) {
    return this.delete(`/stock/${id}`);
  }

  // Récupérer les alertes de stock faible
  async getLowStockAlerts() {
    return this.get('/stock/alerts/low-stock');
  }

  // Récupérer les produits expirés
  async getExpiredProducts() {
    return this.get('/stock/alerts/expired');
  }

  // Récupérer les produits qui expirent bientôt
  async getExpiringSoon(days = 7) {
    return this.get('/stock/alerts/expiring-soon', { days });
  }

  // Récupérer le résumé du stock
  async getStockSummary() {
    return this.get('/stock/summary');
  }

  // Récupérer les statistiques du stock
  async getStockStats() {
    return this.get('/stock/stats');
  }

  // === API SYSTÈME ===

  // Vérifier la santé de l'API
  async healthCheck() {
    return this.get('/health');
  }

  // Récupérer les informations de l'API
  async getApiInfo() {
    return this.get('/info');
  }
}

// Classe pour gérer les notifications
class NotificationManager {
  constructor() {
    this.container = document.getElementById('notifications-container');
    this.notifications = new Map();
  }

  show(message, type = 'info', duration = 5000) {
    const id = Utils.generateId();
    const notification = this.createNotification(id, message, type);
    
    this.container.appendChild(notification);
    this.notifications.set(id, notification);

    // Animation d'entrée
    setTimeout(() => {
      notification.classList.add('show');
    }, 10);

    // Auto-suppression
    if (duration > 0) {
      setTimeout(() => {
        this.hide(id);
      }, duration);
    }

    return id;
  }

  createNotification(id, message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.dataset.id = id;
    
    const icon = this.getIcon(type);
    
    notification.innerHTML = `
      <div class="notification-content">
        <div class="notification-header">
          <i class="${icon}"></i>
          <button class="notification-close" onclick="notifications.hide('${id}')">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="notification-message">${message}</div>
      </div>
    `;

    return notification;
  }

  getIcon(type) {
    const icons = {
      success: 'fas fa-check-circle',
      error: 'fas fa-exclamation-circle',
      warning: 'fas fa-exclamation-triangle',
      info: 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
  }

  hide(id) {
    const notification = this.notifications.get(id);
    if (notification) {
      notification.classList.add('hide');
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
        this.notifications.delete(id);
      }, 300);
    }
  }

  clear() {
    this.notifications.forEach((notification, id) => {
      this.hide(id);
    });
  }

  // Méthodes de convenance
  success(message, duration) {
    return this.show(message, 'success', duration);
  }

  error(message, duration) {
    return this.show(message, 'error', duration);
  }

  warning(message, duration) {
    return this.show(message, 'warning', duration);
  }

  info(message, duration) {
    return this.show(message, 'info', duration);
  }
}

// Classe pour gérer le loading
class LoadingManager {
  constructor() {
    this.spinner = document.getElementById('loading-spinner');
    this.isLoading = false;
  }

  show() {
    this.isLoading = true;
    this.spinner.classList.add('active');
  }

  hide() {
    this.isLoading = false;
    this.spinner.classList.remove('active');
  }

  async wrap(promise) {
    this.show();
    try {
      const result = await promise;
      this.hide();
      return result;
    } catch (error) {
      this.hide();
      throw error;
    }
  }
}

// Instances globales
const api = new ApiClient();
const notifications = new NotificationManager();
const loading = new LoadingManager();

// Export pour utilisation dans d'autres modules
window.api = api;
window.notifications = notifications;
window.loading = loading;

