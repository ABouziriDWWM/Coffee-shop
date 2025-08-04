/**
 * Composants réutilisables pour Coffee Lab
 */

// Gestionnaire de modales
class ModalManager {
  constructor() {
    this.overlay = document.getElementById('modal-overlay');
    this.container = document.getElementById('modal-container');
    this.currentModal = null;
  }

  show(content, options = {}) {
    this.container.innerHTML = content;
    this.overlay.classList.add('active');
    this.currentModal = options;
    
    // Gérer la fermeture avec Escape
    document.addEventListener('keydown', this.handleKeydown.bind(this));
    
    // Gérer la fermeture en cliquant sur l'overlay
    this.overlay.addEventListener('click', this.handleOverlayClick.bind(this));
  }

  hide() {
    this.overlay.classList.remove('active');
    this.currentModal = null;
    document.removeEventListener('keydown', this.handleKeydown.bind(this));
    this.overlay.removeEventListener('click', this.handleOverlayClick.bind(this));
  }

  handleKeydown(e) {
    if (e.key === 'Escape') {
      this.hide();
    }
  }

  handleOverlayClick(e) {
    if (e.target === this.overlay) {
      this.hide();
    }
  }

  // Modales prédéfinies
  confirm(title, message, onConfirm, onCancel) {
    const content = `
      <div class="modal-header">
        <h3 class="modal-title">${title}</h3>
        <button class="modal-close" onclick="modal.hide()">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body">
        <p>${message}</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="modal.hide(); ${onCancel ? onCancel.name + '()' : ''}">
          Annuler
        </button>
        <button class="btn btn-danger" onclick="modal.hide(); ${onConfirm.name}()">
          Confirmer
        </button>
      </div>
    `;
    this.show(content);
  }

  form(title, fields, onSubmit, data = {}) {
    const formFields = fields.map(field => this.createFormField(field, data[field.name])).join('');
    
    const content = `
      <div class="modal-header">
        <h3 class="modal-title">${title}</h3>
        <button class="modal-close" onclick="modal.hide()">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <form id="modal-form" class="modal-body">
        ${formFields}
      </form>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" onclick="modal.hide()">
          Annuler
        </button>
        <button type="submit" form="modal-form" class="btn btn-primary">
          Enregistrer
        </button>
      </div>
    `;
    
    this.show(content);
    
    // Gérer la soumission du formulaire
    document.getElementById('modal-form').addEventListener('submit', (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const data = Object.fromEntries(formData.entries());
      onSubmit(data);
    });
  }

  createFormField(field, value = '') {
    const { name, label, type = 'text', required = false, options = [] } = field;
    
    let input = '';
    
    switch (type) {
      case 'select':
        const optionsList = options.map(opt => 
          `<option value="${opt.value}" ${opt.value === value ? 'selected' : ''}>${opt.label}</option>`
        ).join('');
        input = `<select name="${name}" class="form-select" ${required ? 'required' : ''}>${optionsList}</select>`;
        break;
      
      case 'textarea':
        input = `<textarea name="${name}" class="form-textarea" ${required ? 'required' : ''}>${value}</textarea>`;
        break;
      
      case 'number':
        input = `<input type="number" name="${name}" class="form-input" value="${value}" ${required ? 'required' : ''} ${field.min !== undefined ? `min="${field.min}"` : ''} ${field.max !== undefined ? `max="${field.max}"` : ''} ${field.step !== undefined ? `step="${field.step}"` : ''}>`;
        break;
      
      default:
        input = `<input type="${type}" name="${name}" class="form-input" value="${value}" ${required ? 'required' : ''}>`;
    }
    
    return `
      <div class="form-group">
        <label class="form-label">${label} ${required ? '*' : ''}</label>
        ${input}
      </div>
    `;
  }
}

// Composant de tableau de données
class DataTable {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.getElementById(container) : container;
    this.options = {
      columns: [],
      data: [],
      searchable: true,
      sortable: true,
      pagination: true,
      pageSize: 10,
      ...options
    };
    this.currentPage = 1;
    this.sortColumn = null;
    this.sortDirection = 'asc';
    this.searchTerm = '';
    this.filteredData = [];
  }

  render() {
    this.container.innerHTML = `
      ${this.options.searchable ? this.renderSearch() : ''}
      <div class="data-table-container">
        <table class="data-table">
          <thead>
            ${this.renderHeader()}
          </thead>
          <tbody>
            ${this.renderBody()}
          </tbody>
        </table>
      </div>
      ${this.options.pagination ? this.renderPagination() : ''}
    `;
    
    this.attachEvents();
  }

  renderSearch() {
    return `
      <div class="data-table-search">
        <input type="text" class="search-input" placeholder="Rechercher..." value="${this.searchTerm}">
        <i class="fas fa-search search-icon"></i>
      </div>
    `;
  }

  renderHeader() {
    return `
      <tr>
        ${this.options.columns.map(col => `
          <th class="data-table-header ${this.options.sortable && col.sortable !== false ? 'sortable' : ''}" 
              data-column="${col.key}">
            ${col.label}
            ${this.options.sortable && col.sortable !== false ? `
              <i class="fas fa-sort sort-icon ${this.sortColumn === col.key ? (this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down') : ''}"></i>
            ` : ''}
          </th>
        `).join('')}
      </tr>
    `;
  }

  renderBody() {
    const data = this.getPaginatedData();
    
    if (data.length === 0) {
      return `
        <tr>
          <td colspan="${this.options.columns.length}" class="data-table-empty">
            Aucune donnée disponible
          </td>
        </tr>
      `;
    }
    
    return data.map(row => `
      <tr class="data-table-row" data-id="${row._id || row.id}">
        ${this.options.columns.map(col => `
          <td class="data-table-cell">
            ${this.formatCellValue(row[col.key], col, row)}
          </td>
        `).join('')}
      </tr>
    `).join('');
  }

  formatCellValue(value, column, row) {
    if (column.render) {
      return column.render(value, row);
    }
    
    if (column.type === 'currency') {
      return Utils.formatPrice(value);
    }
    
    if (column.type === 'date') {
      return Utils.formatDate(value);
    }
    
    if (column.type === 'status') {
      return `<span class="status-badge ${value}">${Utils.translateStatus(value)}</span>`;
    }
    
    return value || '-';
  }

  renderPagination() {
    const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
    
    if (totalPages <= 1) return '';
    
    return `
      <div class="data-table-pagination">
        <button class="btn btn-secondary btn-sm" ${this.currentPage === 1 ? 'disabled' : ''} data-page="${this.currentPage - 1}">
          <i class="fas fa-chevron-left"></i>
        </button>
        <span class="pagination-info">
          Page ${this.currentPage} sur ${totalPages}
        </span>
        <button class="btn btn-secondary btn-sm" ${this.currentPage === totalPages ? 'disabled' : ''} data-page="${this.currentPage + 1}">
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    `;
  }

  attachEvents() {
    // Recherche
    if (this.options.searchable) {
      const searchInput = this.container.querySelector('.search-input');
      searchInput.addEventListener('input', Utils.debounce((e) => {
        this.searchTerm = e.target.value;
        this.currentPage = 1;
        this.filterAndSort();
        this.render();
      }, 300));
    }
    
    // Tri
    if (this.options.sortable) {
      this.container.querySelectorAll('.sortable').forEach(header => {
        header.addEventListener('click', () => {
          const column = header.dataset.column;
          if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
          } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
          }
          this.filterAndSort();
          this.render();
        });
      });
    }
    
    // Pagination
    if (this.options.pagination) {
      this.container.querySelectorAll('[data-page]').forEach(btn => {
        btn.addEventListener('click', () => {
          this.currentPage = parseInt(btn.dataset.page);
          this.render();
        });
      });
    }
    
    // Événements de ligne
    this.container.querySelectorAll('.data-table-row').forEach(row => {
      row.addEventListener('click', () => {
        if (this.options.onRowClick) {
          const id = row.dataset.id;
          const data = this.filteredData.find(item => (item._id || item.id) === id);
          this.options.onRowClick(data);
        }
      });
    });
  }

  filterAndSort() {
    let data = [...this.options.data];
    
    // Filtrage
    if (this.searchTerm) {
      data = data.filter(item => {
        return this.options.columns.some(col => {
          const value = item[col.key];
          return value && value.toString().toLowerCase().includes(this.searchTerm.toLowerCase());
        });
      });
    }
    
    // Tri
    if (this.sortColumn) {
      data.sort((a, b) => {
        const aVal = a[this.sortColumn];
        const bVal = b[this.sortColumn];
        
        if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
        return 0;
      });
    }
    
    this.filteredData = data;
  }

  getPaginatedData() {
    if (!this.options.pagination) return this.filteredData;
    
    const start = (this.currentPage - 1) * this.options.pageSize;
    const end = start + this.options.pageSize;
    return this.filteredData.slice(start, end);
  }

  updateData(newData) {
    this.options.data = newData;
    this.currentPage = 1;
    this.filterAndSort();
    this.render();
  }
}

// Composant de graphique simple
class SimpleChart {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.getElementById(container) : container;
    this.options = {
      type: 'bar',
      data: [],
      width: 300,
      height: 200,
      ...options
    };
  }

  render() {
    if (this.options.type === 'bar') {
      this.renderBarChart();
    } else if (this.options.type === 'line') {
      this.renderLineChart();
    }
  }

  renderBarChart() {
    const { data, width, height } = this.options;
    const maxValue = Math.max(...data.map(d => d.value));
    
    const bars = data.map((item, index) => {
      const barHeight = (item.value / maxValue) * (height - 40);
      const x = (index * (width / data.length)) + 10;
      
      return `
        <div class="chart-bar" style="
          left: ${x}px;
          bottom: 20px;
          width: ${(width / data.length) - 20}px;
          height: ${barHeight}px;
          background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
        ">
          <div class="chart-value">${item.value}</div>
        </div>
        <div class="chart-label" style="
          left: ${x}px;
          bottom: 0;
          width: ${(width / data.length) - 20}px;
        ">${item.label}</div>
      `;
    }).join('');
    
    this.container.innerHTML = `
      <div class="simple-chart" style="width: ${width}px; height: ${height}px; position: relative;">
        ${bars}
      </div>
    `;
  }
}

// Instances globales
const modal = new ModalManager();

// Export pour utilisation dans d'autres modules
window.modal = modal;
window.DataTable = DataTable;
window.SimpleChart = SimpleChart;

