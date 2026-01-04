/**
 * MONA Beach Club - Navigation Manager
 * Controle da sidebar de navegação por meses
 */

'use strict';

const NavigationManager = {
    // Elementos
    sidebar: null,
    overlay: null,
    toggleBtn: null,
    collapseBtn: null,

    /**
     * Inicializa o gerenciador de navegação
     */
    init() {
        this.sidebar = document.querySelector('.sidebar');
        this.overlay = document.getElementById('sidebar-overlay');
        this.toggleBtn = document.getElementById('btn-sidebar-toggle');
        this.collapseBtn = document.getElementById('btn-collapse-sidebar');

        if (!this.sidebar) return;

        this.bindEvents();
        this.highlightActiveMonth();
        this.restoreCollapseState();
    },

    /**
     * Bind dos eventos
     */
    bindEvents() {
        // Toggle button (mobile)
        if (this.toggleBtn) {
            this.toggleBtn.addEventListener('click', () => this.toggle());
        }

        // Collapse button (desktop)
        if (this.collapseBtn) {
            this.collapseBtn.addEventListener('click', () => this.toggleCollapse());
        }

        // Overlay click fecha sidebar
        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.close());
        }

        // ESC fecha sidebar
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });

        // Fechar ao clicar em link (mobile)
        this.sidebar.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                // Salvar posição do scroll antes de navegar
                this.saveScrollPosition();

                if (window.innerWidth < 992) {
                    this.close();
                }
            });
        });

        // Salvar scroll ao rolar a sidebar
        const sidebarNav = this.sidebar.querySelector('.sidebar-nav');
        if (sidebarNav) {
            sidebarNav.addEventListener('scroll', () => {
                sessionStorage.setItem('mona-sidebar-scroll', sidebarNav.scrollTop);
            });

            // Restaurar posição do scroll
            const savedScroll = sessionStorage.getItem('mona-sidebar-scroll');
            if (savedScroll) {
                sidebarNav.scrollTop = parseInt(savedScroll, 10);
            }
        }
    },

    /**
     * Salva a posição do scroll da sidebar
     */
    saveScrollPosition() {
        const sidebarNav = this.sidebar.querySelector('.sidebar-nav');
        if (sidebarNav) {
            sessionStorage.setItem('mona-sidebar-scroll', sidebarNav.scrollTop);
        }
    },

    /**
     * Toggle collapse da sidebar (desktop)
     */
    toggleCollapse() {
        const isCollapsed = this.sidebar.classList.toggle('collapsed');
        localStorage.setItem('mona-sidebar-collapsed', isCollapsed ? 'true' : 'false');

        // Atualiza ícone do botão
        if (this.collapseBtn) {
            const icon = this.collapseBtn.querySelector('i');
            if (icon) {
                icon.className = isCollapsed ? 'bi bi-list' : 'bi bi-list';
            }
        }
    },

    /**
     * Restaura estado de collapse do localStorage
     */
    restoreCollapseState() {
        const isCollapsed = localStorage.getItem('mona-sidebar-collapsed') === 'true';
        if (isCollapsed && window.innerWidth >= 992) {
            this.sidebar.classList.add('collapsed');
            if (this.collapseBtn) {
                const icon = this.collapseBtn.querySelector('i');
                if (icon) {
                    icon.className = 'bi bi-list';
                }
            }
        }
        // Remove classe inicial para permitir transições normais
        document.documentElement.classList.remove('sidebar-collapsed-initial');
    },

    /**
     * Abre a sidebar
     */
    open() {
        this.sidebar.classList.add('show');
        if (this.overlay) this.overlay.classList.add('show');
        document.body.style.overflow = 'hidden';

        // Atualiza ícone do botão
        if (this.toggleBtn) {
            this.toggleBtn.innerHTML = '<i class="bi bi-x-lg"></i>';
        }
    },

    /**
     * Fecha a sidebar
     */
    close() {
        this.sidebar.classList.remove('show');
        if (this.overlay) this.overlay.classList.remove('show');
        document.body.style.overflow = '';

        // Atualiza ícone do botão
        if (this.toggleBtn) {
            this.toggleBtn.innerHTML = '<i class="bi bi-calendar3"></i>';
        }
    },

    /**
     * Toggle da sidebar
     */
    toggle() {
        if (this.isOpen()) {
            this.close();
        } else {
            this.open();
        }
    },

    /**
     * Verifica se a sidebar está aberta
     */
    isOpen() {
        return this.sidebar.classList.contains('show');
    },

    /**
     * Destaca o mês ativo na navegação
     */
    highlightActiveMonth() {
        // Pega o mês atual da URL ou do data attribute
        const urlParams = new URLSearchParams(window.location.search);
        const currentMonth = urlParams.get('mes') || new Date().getMonth() + 1;
        const currentYear = urlParams.get('ano') || new Date().getFullYear();

        // Remove active de todos
        this.sidebar.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Adiciona active ao mês atual
        const activeLink = this.sidebar.querySelector(
            `.nav-link[data-mes="${currentMonth}"][data-ano="${currentYear}"]`
        );

        if (activeLink) {
            activeLink.classList.add('active');

            // Scroll para o item ativo (se necessário)
            activeLink.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    },

    /**
     * Navega para um mês específico
     */
    navigateToMonth(mes, ano) {
        const baseUrl = window.location.pathname;
        const url = new URL(baseUrl, window.location.origin);
        url.searchParams.set('mes', mes);
        url.searchParams.set('ano', ano);

        // Mantém outros parâmetros
        const currentParams = new URLSearchParams(window.location.search);
        ['aba', 'per_page'].forEach(param => {
            if (currentParams.has(param)) {
                url.searchParams.set(param, currentParams.get(param));
            }
        });

        window.location.href = url.toString();
    }
};

// Inicializa quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => NavigationManager.init());
} else {
    NavigationManager.init();
}

// Exporta para uso global
window.NavigationManager = NavigationManager;
