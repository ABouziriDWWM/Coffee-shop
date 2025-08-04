/**
 * Application principale Coffee Lab
 */

class CoffeeLabApp {
  constructor() {
    this.currentModule = 'dashboard';
    this.modules = new Map();
    this.initialized = false;
  }

  async init() {
    if (this.initialized) return;

    try {
      // Vérifier la santé de l'API
      await this.checkApiHealth();
      
      // Initialiser les modules
      this.initializeModules();
      
      // Configurer la navigation
      this.setupNavigation();
      
      // Charger le module par défaut
      await this.loadModule('dashboard');
      
      // Configurer les événements globaux
      this.setupGlobalEvents();
      
      this.initialized = true;
      console.log('Coffee Lab App initialisée avec succès');
      
    } catch (error) {
      console.error('Erreur lors de l\'initialisation:', error);
      notifications.error('Erreur lors de l\'initialisation de l\'application');
    }
  }

  async checkApiHealth() {
    try {
      const response = await api.healthCheck();
      if (response.success) {
        console.log('API Coffee Shop opérationnelle');
      }
    } catch (error) {
      console.warn('API non disponible, mode hors ligne');
      notifications.warning('API non disponible, certaines fonctionnalités peuvent être limitées');
    }
  }

  initializeModules() {
    // Enregistrer les modules disponibles
    this.modules.set('dashboard', {
      name: 'Dashboard',
      element: document.getElementById('dashboard-module'),
      instance: window.DashboardModule ? new window.DashboardModule() : null
    });
    
    this.modules.set('orders', {
      name: 'Commandes',
      element: document.getElementById('orders-module'),
      instance: window.OrdersModule ? new window.OrdersModule() : null
    });
    
    this.modules.set('bills', {
      name: 'Additions',
      element: document.getElementById('bills-module'),
      instance: window.BillsModule ? new window.BillsModule() : null
    });
    
    this.modules.set('stock', {
      name: 'Stock',
      element: document.getElementById('stock-module'),
      instance: window.StockModule ? new window.StockModule() : null
    });
  }

  setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item[data-module]');
    
    navItems.forEach(item => {
      item.addEventListener('click', async (e) => {
        e.preventDefault();
        const moduleId = item.dataset.module;
        await this.loadModule(moduleId);
      });
    });
  }

  async loadModule(moduleId) {
    if (!this.modules.has(moduleId)) {
      console.error(`Module ${moduleId} non trouvé`);
      return;
    }

    try {
      // Masquer tous les modules
      this.modules.forEach((module, id) => {
        module.element.classList.remove('active');
        document.querySelector(`[data-module="${id}"]`).classList.remove('active');
      });

      // Afficher le module sélectionné
      const module = this.modules.get(moduleId);
      module.element.classList.add('active');
      document.querySelector(`[data-module="${moduleId}"]`).classList.add('active');

      // Initialiser le module si nécessaire
      if (module.instance && typeof module.instance.init === 'function') {
        await module.instance.init();
      }

      this.currentModule = moduleId;
      
      // Mettre à jour l'URL sans recharger la page
      history.pushState({ module: moduleId }, '', `#${moduleId}`);
      
    } catch (error) {
      console.error(`Erreur lors du chargement du module ${moduleId}:`, error);
      notifications.error(`Erreur lors du chargement du module ${this.modules.get(moduleId).name}`);
    }
  }

  setupGlobalEvents() {
    // Gestion du bouton retour du navigateur
    window.addEventListener('popstate', (e) => {
      if (e.state && e.state.module) {
        this.loadModule(e.state.module);
      }
    });

    // Gestion de l'URL au chargement
    const hash = window.location.hash.substring(1);
    if (hash && this.modules.has(hash)) {
      this.loadModule(hash);
    }

    // Raccourcis clavier
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + K pour la recherche globale
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        this.openGlobalSearch();
      }
      
      // Échap pour fermer les modales
      if (e.key === 'Escape') {
        modal.hide();
      }
    });

    // Gestion des notifications de mise à jour
    this.setupUpdateNotifications();
    
    // Auto-refresh des données
    this.setupAutoRefresh();
  }

  openGlobalSearch() {
    // Implémentation de la recherche globale
    modal.form('Recherche Globale', [
      {
        name: 'query',
        label: 'Rechercher',
        type: 'text',
        required: true
      },
      {
        name: 'type',
        label: 'Type',
        type: 'select',
        options: [
          { value: 'all', label: 'Tout' },
          { value: 'orders', label: 'Commandes' },
          { value: 'bills', label: 'Additions' },
          { value: 'stock', label: 'Produits' }
        ]
      }
    ], async (data) => {
      await this.performGlobalSearch(data.query, data.type);
      modal.hide();
    });
  }

  async performGlobalSearch(query, type) {
    try {
      loading.show();
      
      const results = [];
      
      if (type === 'all' || type === 'orders') {
        const orders = await api.getOrders();
        const filteredOrders = orders.data.filter(order => 
          order.orderNumber.toLowerCase().includes(query.toLowerCase()) ||
          order.customerName.toLowerCase().includes(query.toLowerCase())
        );
        results.push(...filteredOrders.map(order => ({ ...order, type: 'order' })));
      }
      
      if (type === 'all' || type === 'bills') {
        const bills = await api.getBills();
        const filteredBills = bills.data.filter(bill => 
          bill.billNumber.toLowerCase().includes(query.toLowerCase()) ||
          bill.customerName.toLowerCase().includes(query.toLowerCase())
        );
        results.push(...filteredBills.map(bill => ({ ...bill, type: 'bill' })));
      }
      
      if (type === 'all' || type === 'stock') {
        const products = await api.getProducts();
        const filteredProducts = products.data.filter(product => 
          product.productName.toLowerCase().includes(query.toLowerCase()) ||
          product.productId.toLowerCase().includes(query.toLowerCase())
        );
        results.push(...filteredProducts.map(product => ({ ...product, type: 'product' })));
      }
      
      this.displaySearchResults(results, query);
      
    } catch (error) {
      console.error('Erreur lors de la recherche:', error);
      notifications.error('Erreur lors de la recherche');
    } finally {
      loading.hide();
    }
  }

  displaySearchResults(results, query) {
    const content = `
      <div class="modal-header">
        <h3 class="modal-title">Résultats de recherche pour "${query}"</h3>
        <button class="modal-close" onclick="modal.hide()">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body">
        ${results.length === 0 ? 
          '<p class="text-center text-muted">Aucun résultat trouvé</p>' :
          results.map(result => this.renderSearchResult(result)).join('')
        }
      </div>
    `;
    
    modal.show(content);
  }

  renderSearchResult(result) {
    const typeLabels = {
      order: 'Commande',
      bill: 'Addition',
      product: 'Produit'
    };
    
    const typeIcons = {
      order: 'fas fa-shopping-cart',
      bill: 'fas fa-receipt',
      product: 'fas fa-box'
    };
    
    return `
      <div class="search-result" onclick="app.openSearchResult('${result.type}', '${result._id}')">
        <div class="search-result-header">
          <i class="${typeIcons[result.type]}"></i>
          <span class="search-result-type">${typeLabels[result.type]}</span>
        </div>
        <div class="search-result-content">
          <h4>${result.orderNumber || result.billNumber || result.productName}</h4>
          <p>${result.customerName || result.category || ''}</p>
        </div>
      </div>
    `;
  }

  async openSearchResult(type, id) {
    modal.hide();
    
    const moduleMap = {
      order: 'orders',
      bill: 'bills',
      product: 'stock'
    };
    
    const moduleId = moduleMap[type];
    if (moduleId) {
      await this.loadModule(moduleId);
      
      // Notifier le module pour qu'il affiche l'élément spécifique
      const module = this.modules.get(moduleId);
      if (module.instance && typeof module.instance.showItem === 'function') {
        module.instance.showItem(id);
      }
    }
  }

  setupUpdateNotifications() {
    // Vérifier les mises à jour périodiquement
    setInterval(async () => {
      try {
        // Vérifier s'il y a de nouvelles commandes
        const currentModule = this.modules.get(this.currentModule);
        if (currentModule.instance && typeof currentModule.instance.checkUpdates === 'function') {
          await currentModule.instance.checkUpdates();
        }
      } catch (error) {
        console.error('Erreur lors de la vérification des mises à jour:', error);
      }
    }, 30000); // Toutes les 30 secondes
  }

  setupAutoRefresh() {
    // Auto-refresh des données toutes les 5 minutes
    setInterval(async () => {
      if (document.visibilityState === 'visible') {
        const currentModule = this.modules.get(this.currentModule);
        if (currentModule.instance && typeof currentModule.instance.refresh === 'function') {
          await currentModule.instance.refresh();
        }
      }
    }, 300000); // Toutes les 5 minutes
  }

  // Méthodes utilitaires
  getCurrentModule() {
    return this.currentModule;
  }

  getModule(moduleId) {
    return this.modules.get(moduleId);
  }

  async refreshCurrentModule() {
    const currentModule = this.modules.get(this.currentModule);
    if (currentModule.instance && typeof currentModule.instance.refresh === 'function') {
      await currentModule.instance.refresh();
    }
  }
}

// Initialisation de l'application
const app = new CoffeeLabApp();

// Démarrer l'application quand le DOM est prêt
document.addEventListener('DOMContentLoaded', async () => {
  try {
    await app.init();
  } catch (error) {
    console.error('Erreur fatale lors de l\'initialisation:', error);
    document.body.innerHTML = `
      <div class="error-container">
        <h1>Erreur d'initialisation</h1>
        <p>Une erreur s'est produite lors du chargement de l'application.</p>
        <button onclick="location.reload()" class="btn btn-primary">Recharger</button>
      </div>
    `;
  }
});

// Export pour utilisation globale
window.app = app;

