/**
 * MONA Beach Club - Theme Manager
 * Gerencia alternância entre light/dark mode com persistência em localStorage
 */

'use strict';

const ThemeManager = {
    // Chave para localStorage
    STORAGE_KEY: 'mona-theme',

    // Temas disponíveis
    THEMES: {
        LIGHT: 'light',
        DARK: 'dark',
        AUTO: 'auto'
    },

    /**
     * Inicializa o gerenciador de tema
     */
    init() {
        // Aplica tema salvo ou detecta do sistema
        this.applyTheme(this.getSavedTheme());

        // Listener para mudanças de preferência do sistema
        this.watchSystemPreference();

        // Bind do toggle button (se existir)
        this.bindToggle();
    },

    /**
     * Obtém tema salvo no localStorage ou 'auto' como padrão
     */
    getSavedTheme() {
        return localStorage.getItem(this.STORAGE_KEY) || this.THEMES.LIGHT;
    },

    /**
     * Salva tema no localStorage
     */
    saveTheme(theme) {
        localStorage.setItem(this.STORAGE_KEY, theme);
    },

    /**
     * Aplica tema ao documento
     */
    applyTheme(theme) {
        const html = document.documentElement;

        // Remove qualquer tema anterior
        html.removeAttribute('data-theme');

        // Aplica novo tema
        if (theme === this.THEMES.DARK) {
            html.setAttribute('data-theme', 'dark');
        } else if (theme === this.THEMES.AUTO) {
            html.setAttribute('data-theme', 'auto');
        }
        // Light mode = sem atributo (padrão)

        // Salva preferência
        this.saveTheme(theme);

        // Atualiza ícone do toggle
        this.updateToggleIcon(theme);

        // Dispara evento customizado
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme, isDark: this.isDarkMode() }
        }));
    },

    /**
     * Alterna entre light e dark mode
     */
    toggle() {
        const currentTheme = this.getSavedTheme();
        const newTheme = currentTheme === this.THEMES.DARK
            ? this.THEMES.LIGHT
            : this.THEMES.DARK;

        this.applyTheme(newTheme);
    },

    /**
     * Verifica se está em dark mode (considerando 'auto')
     */
    isDarkMode() {
        const theme = this.getSavedTheme();

        if (theme === this.THEMES.DARK) {
            return true;
        }

        if (theme === this.THEMES.AUTO) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches;
        }

        return false;
    },

    /**
     * Observa mudanças na preferência do sistema
     */
    watchSystemPreference() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

        mediaQuery.addEventListener('change', (e) => {
            if (this.getSavedTheme() === this.THEMES.AUTO) {
                // Re-aplica para atualizar
                this.applyTheme(this.THEMES.AUTO);
            }
        });
    },

    /**
     * Conecta evento ao botão de toggle
     */
    bindToggle() {
        const toggleBtn = document.getElementById('theme-toggle');

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());

            // Atualiza ícone inicial
            this.updateToggleIcon(this.getSavedTheme());
        }
    },

    /**
     * Atualiza ícone do botão toggle
     */
    updateToggleIcon(theme) {
        const toggleBtn = document.getElementById('theme-toggle');
        if (!toggleBtn) return;

        const icon = toggleBtn.querySelector('i');
        if (!icon) return;

        // Remove classes antigas
        icon.className = '';

        // Aplica nova classe baseada no tema
        if (theme === this.THEMES.DARK) {
            icon.className = 'bi bi-sun-fill';
            toggleBtn.setAttribute('title', 'Mudar para modo claro');
        } else {
            icon.className = 'bi bi-moon-fill';
            toggleBtn.setAttribute('title', 'Mudar para modo escuro');
        }
    },

    /**
     * Retorna cores para charts baseado no tema atual
     */
    getChartColors() {
        const isDark = this.isDarkMode();

        return {
            textColor: isDark ? '#e6edf3' : '#212529',
            gridColor: isDark ? '#30363d' : '#dee2e6',
            backgroundColor: isDark ? '#161b22' : '#ffffff',
            tooltipBg: isDark ? '#21262d' : '#ffffff',
            tooltipBorder: isDark ? '#484f58' : '#dee2e6'
        };
    }
};

// Inicializa quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
} else {
    ThemeManager.init();
}

// Exporta para uso global
window.ThemeManager = ThemeManager;
