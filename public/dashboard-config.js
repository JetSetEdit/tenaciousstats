/**
 * White-label / client branding — edit this file for a new company (after you fork or copy the repo).
 * GA4 property ID and Google credentials stay on the server: env PROPERTY_ID, credentials.json, etc.
 * See SETUP.md and HANDOVER.md.
 */
(function () {
    window.DASHBOARD_CONFIG = {
        pageTitle: 'Tenacious Stats Dashboard',
        dashboardHeading: '📊 Tenacious Stats Dashboard',
        headerSubtitle: 'Website stats for Tenacious Tapes — adhesive tapes for every application',
        glossaryPrintTagline: 'Tenacious Tapes - Adhesive Tapes for every application',
        logoAlt: 'Tenacious Tapes logo',
        /** Used on login modal, reports, glossary print — full-colour mark */
        logoUrl: 'https://www.tenacioustapes.com.au/wp-content/uploads/2025/12/tenacious-tapes-logo-scaled.png',
        /** Optional narrower header mark; falls back to logoUrl */
        logoUrlHeader: 'https://www.tenacioustapes.com.au/wp-content/uploads/2025/08/logo-1-scaled.png',
        colors: {
            accent: '#ff5800',
            accentHover: '#d43d00',
            headerBackground: '#000000',
            bodyText: '#2c3e50',
            pageBackground: '#f8f9fa',
        },
        /** Client-side gate only; not secret — use real auth for sensitive data */
        password: 'Tenacious2025',
        filenames: {
            pdfReportPrefix: 'Tenacious_Stats_Report',
            pngReportPrefix: 'Tenacious_Stats_Report',
            comparisonPng: 'Tenacious-Stats-Comparison',
        },
        /** Footer lines (HTML allowed, e.g. <strong>) */
        footerLines: [
            '<strong>Tenacious Tapes</strong> - Adhesive Tapes for every application',
            '📞 +61 (0)3 9580 5573 | ✉️ customerservice@tenacioustapes.com.au',
        ],
        /** Featured-story links on the Sales stats tab (no trailing slash) */
        sitePublicBaseUrl: 'https://www.tenacioustapes.com.au',
    };

    function applyCssVars() {
        var c = window.DASHBOARD_CONFIG;
        var col = c.colors || {};
        var root = document.documentElement;
        if (col.accent) root.style.setProperty('--brand-accent', col.accent);
        if (col.accentHover) root.style.setProperty('--brand-accent-hover', col.accentHover);
        if (col.headerBackground) root.style.setProperty('--brand-header-bg', col.headerBackground);
        if (col.bodyText) root.style.setProperty('--brand-body-text', col.bodyText);
        if (col.pageBackground) root.style.setProperty('--brand-page-bg', col.pageBackground);
    }

    function applyDom() {
        var c = window.DASHBOARD_CONFIG;
        if (c.pageTitle) document.title = c.pageTitle;

        document.querySelectorAll('[data-brand-logo]').forEach(function (el) {
            el.src = c.logoUrl;
            el.alt = c.logoAlt || '';
        });
        document.querySelectorAll('[data-brand-logo-header]').forEach(function (el) {
            el.src = c.logoUrlHeader || c.logoUrl;
            el.alt = c.logoAlt || '';
        });

        var h1 = document.querySelector('[data-brand-dashboard-heading]');
        if (h1 && c.dashboardHeading) h1.textContent = c.dashboardHeading;

        var sub = document.querySelector('[data-brand-header-subtitle]');
        if (sub && c.headerSubtitle) sub.textContent = c.headerSubtitle;

        var gph = document.querySelector('[data-brand-glossary-tagline]');
        if (gph && c.glossaryPrintTagline) gph.textContent = c.glossaryPrintTagline;

        var foot = document.getElementById('brand-footer-lines');
        if (foot && c.footerLines && c.footerLines.length) {
            foot.innerHTML = c.footerLines.map(function (line) {
                return '<p>' + line + '</p>';
            }).join('');
        }
    }

    applyCssVars();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyDom);
    } else {
        applyDom();
    }
})();
