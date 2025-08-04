/**
 * Module Dashboard pour Coffee Lab
 */

class DashboardModule {
  constructor() {
    this.stats = {
      orders: 0,
      revenue: 0,
      lowStock: 0,
      pendingBills: 0
    };
    this.recentOrders = [];
    this.stockAlerts = [];
  }

  async init() {
    console.log('Initialisation du module Dashboard');
    await this.loadData();
    this.render();
  }

  async loadData() {
    try {
      loading.show();
      
      // Charger les statistiques en parallèle
      const [orderStats, billStats, stockStats, recentOrders, stockAlerts] = await Promise.all([
        this.loadOrderStats(),
        this.loadBillStats(),
        this.loadStockStats(),
        this.loadRecentOrders(),
        this.loadStockAlerts()
      ]);

      this.stats = {
        orders: orderStats.pending || 0,
        revenue: billStats.total_revenue || 0,
        lowStock: stockStats.low_stock || 0,
        pendingBills: billStats.pending || 0
      };

      this.recentOrders = recentOrders;
      this.stockAlerts = stockAlerts;

    } catch (error) {
      console.error('Erreur lors du chargement des données du dashboard:', error);
      notifications.error('Erreur lors du chargement des données');
    } finally {
      loading.hide();
    }
  }

  async loadOrderStats() {
    try {
      const response = await api.getOrderStats();
      return response.data;
    } catch (error) {
      console.error('Erreur lors du chargement des stats commandes:', error);
      return {};
    }
  }

  async loadBillStats() {
    try {
      const response = await api.getBillStats();
      return response.data;
    } catch (error) {
      console.error('Erreur lors du chargement des stats additions:', error);
      return {};
    }
  }

  async loadStockStats() {
    try {
      const response = await api.getStockStats();
      return response.data;
    } catch (error) {
      console.error('Erreur lors du chargement des stats stock:', error);
      return {};
    }
  }

  async loadRecentOrders() {
    try {
      const response = await api.getOrders({ limit: 5 });
      return response.data || [];
    } catch (error) {
      console.error('Erreur lors du chargement des commandes récentes:', error);
      return [];
    }
  }

  async loadStockAlerts() {
    try {
      const response = await api.getLowStockAlerts();
      return response.data || [];
    } catch (error) {
      console.error('Erreur lors du chargement des alertes stock:', error);
      return [];
    }
  }

  render() {
    this.renderStats();
    this.renderRecentOrders();
    this.renderStockAlerts();
    this.attachEvents();
  }

  renderStats() {
    // Mettre à jour les cartes de statistiques
    document.getElementById('total-orders').textContent = this.stats.orders;
    document.getElementById('total-revenue').textContent = Utils.formatPrice(this.stats.revenue);
    document.getElementById('low-stock-count').textContent = this.stats.lowStock;
    document.getElementById('pending-bills').textContent = this.stats.pendingBills;
  }

  renderRecentOrders() {
    const container = document.getElementById('recent-orders-list');
    
    if (this.recentOrders.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">
            <i class="fas fa-shopping-cart"></i>
          </div>
          <div class="empty-state-title">Aucune commande récente</div>
          <div class="empty-state-message">Les nouvelles commandes apparaîtront ici</div>
        </div>
      `;
      return;
    }

    container.innerHTML = this.recentOrders.map(order => `
      <div class="order-item" data-id="${order._id}">
        <div class="order-item-header">
          <span class="order-number">${order.orderNumber}</span>
          <span class="order-time">${Utils.formatRelativeDate(order.orderDate)}</span>
        </div>
        <div class="order-customer">${order.customerName}</div>
        <div class="order-total">${Utils.formatPrice(order.totalAmount)}</div>
        <span class="status-badge ${order.status}">${Utils.translateStatus(order.status)}</span>
      </div>
    `).join('');
  }

  renderStockAlerts() {
    const container = document.getElementById('stock-alerts-list');
    
    if (this.stockAlerts.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="empty-state-title">Aucune alerte</div>
          <div class="empty-state-message">Tous les produits sont en stock suffisant</div>
        </div>
      `;
      return;
    }

    container.innerHTML = this.stockAlerts.map(product => `
      <div class="alert-item" data-id="${product._id}">
        <div class="alert-product">${product.productName}</div>
        <div class="alert-message">
          Stock actuel: ${Utils.formatQuantity(product.currentStock, product.unit)}
          (Min: ${Utils.formatQuantity(product.minStock, product.unit)})
        </div>
        <span class="category-badge ${product.category}">${Utils.translateCategory(product.category)}</span>
      </div>
    `).join('');
  }

  attachEvents() {
    // Événement de rafraîchissement
    const refreshBtn = document.querySelector('#dashboard-module .btn-primary');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', async () => {
        await this.refresh();
      });
    }

    // Événements sur les commandes récentes
    document.querySelectorAll('#recent-orders-list .order-item').forEach(item => {
      item.addEventListener('click', () => {
        const orderId = item.dataset.id;
        this.openOrderDetails(orderId);
      });
    });

    // Événements sur les alertes stock
    document.querySelectorAll('#stock-alerts-list .alert-item').forEach(item => {
      item.addEventListener('click', () => {
        const productId = item.dataset.id;
        this.openProductDetails(productId);
      });
    });
  }

  async openOrderDetails(orderId) {
    try {
      const response = await api.getOrder(orderId);
      const order = response.data;
      
      const content = `
        <div class="modal-header">
          <h3 class="modal-title">Détails de la commande ${order.orderNumber}</h3>
          <button class="modal-close" onclick="modal.hide()">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="order-details">
            <div class="detail-row">
              <span class="detail-label">Client:</span>
              <span class="detail-value">${order.customerName}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Date:</span>
              <span class="detail-value">${Utils.formatDate(order.orderDate)}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Statut:</span>
              <span class="status-badge ${order.status}">${Utils.translateStatus(order.status)}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Total:</span>
              <span class="detail-value">${Utils.formatPrice(order.totalAmount)}</span>
            </div>
            <div class="detail-section">
              <h4>Articles commandés:</h4>
              <div class="order-items">
                ${order.items.map(item => `
                  <div class="order-item-detail">
                    <span class="item-name">${item.productName}</span>
                    <span class="item-quantity">x${item.quantity}</span>
                    <span class="item-price">${Utils.formatPrice(item.price * item.quantity)}</span>
                  </div>
                `).join('')}
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" onclick="modal.hide()">Fermer</button>
          <button class="btn btn-primary" onclick="app.loadModule('orders')">Voir toutes les commandes</button>
        </div>
      `;
      
      modal.show(content);
      
    } catch (error) {
      console.error('Erreur lors du chargement des détails de la commande:', error);
      notifications.error('Erreur lors du chargement des détails');
    }
  }

  async openProductDetails(productId) {
    try {
      const response = await api.getProduct(productId);
      const product = response.data;
      
      const stockLevel = Utils.getStockLevel(product.currentStock, product.minStock, product.maxStock);
      const stockPercentage = Utils.calculateStockPercentage(product.currentStock, product.maxStock);
      
      const content = `
        <div class="modal-header">
          <h3 class="modal-title">Détails du produit ${product.productName}</h3>
          <button class="modal-close" onclick="modal.hide()">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="product-details">
            <div class="detail-row">
              <span class="detail-label">Catégorie:</span>
              <span class="category-badge ${product.category}">${Utils.translateCategory(product.category)}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Stock actuel:</span>
              <span class="detail-value">${Utils.formatQuantity(product.currentStock, product.unit)}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Stock minimum:</span>
              <span class="detail-value">${Utils.formatQuantity(product.minStock, product.unit)}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Statut:</span>
              <span class="status-badge ${product.status}">${Utils.translateStatus(product.status)}</span>
            </div>
            <div class="stock-levels">
              <div class="stock-bar">
                <div class="stock-bar-fill ${stockLevel}" style="width: ${stockPercentage}%"></div>
              </div>
              <span class="stock-quantity">${stockPercentage}%</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" onclick="modal.hide()">Fermer</button>
          <button class="btn btn-primary" onclick="app.loadModule('stock')">Gérer le stock</button>
        </div>
      `;
      
      modal.show(content);
      
    } catch (error) {
      console.error('Erreur lors du chargement des détails du produit:', error);
      notifications.error('Erreur lors du chargement des détails');
    }
  }

  async refresh() {
    console.log('Rafraîchissement du dashboard');
    await this.loadData();
    this.render();
    notifications.success('Dashboard mis à jour');
  }

  async checkUpdates() {
    // Vérifier s'il y a de nouvelles données
    try {
      const newOrderStats = await this.loadOrderStats();
      if (newOrderStats.pending > this.stats.orders) {
        notifications.info('Nouvelles commandes disponibles');
        await this.refresh();
      }
    } catch (error) {
      console.error('Erreur lors de la vérification des mises à jour:', error);
    }
  }
}

// Export pour utilisation globale
window.DashboardModule = DashboardModule;

