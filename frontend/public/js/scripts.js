/**
 * Carga dinámicamente el contenido de un archivo HTML en un contenedor del DOM.
 * La ruta ahora incluye la carpeta 'components/'.
 * @param {string} url - La ruta del archivo HTML (ej: 'components/navbar.html').
 * @param {string} containerId - El ID del elemento donde se insertará el contenido.
 */
async function loadHtmlComponent(url, containerId) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status} loading ${url}`);
        }
        const html = await response.text();
        document.getElementById(containerId).innerHTML = html;

        // Si es el sidebar, re-ejecutamos la lógica de menús/sesión (si existe y es global)
        if (containerId === 'sidebar-container' && window.checkSessionAndMenus) {
             window.checkSessionAndMenus();
        }
    } catch (error) {
        console.error(`Error al cargar el componente ${url}:`, error);
    }
}

// Carga los componentes usando la ruta 'components/' cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // 1. Cargar Navbar desde components/
    loadHtmlComponent('components/navbar.html', 'navbar-container');
    // 2. Cargar Sidebar desde components/
    loadHtmlComponent('components/sidebar.html', 'sidebar-container');
});

// ... (Código de loadHtmlComponent aquí) ...

