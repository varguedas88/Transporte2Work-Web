/**
 * Carga dinámicamente el contenido de un archivo HTML en un contenedor del DOM.
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

        // ⭐️ Importante: LLAMAMOS A LA FUNCIÓN DESPUÉS DE CADA CARGA ⭐️
        // Esto asegura que los eventos se adjunten inmediatamente después de insertar el HTML.
        if (containerId === 'sidebar-container' || containerId === 'navbar-container') {
             initializeAuthEvents();
        }

        // Si es el sidebar, re-ejecutamos la lógica de menús/sesión (si existe y es global)
        if (containerId === 'sidebar-container' && window.checkSessionAndMenus) {
             window.checkSessionAndMenus();
        }
    } catch (error) {
        console.error(`Error al cargar el componente ${url}:`, error);
    }
}

// ⭐️ FUNCIÓN AJUSTADA: Busca TODOS los enlaces de logout y les adjunta el evento ⭐️
function initializeAuthEvents() {
    // Usamos querySelectorAll con el selector de atributo [id="..."] para buscar
    // todas las instancias con ese ID (Navbar y Sidebar), a pesar de la duplicidad.
    const logoutLinks = document.querySelectorAll('[id="btnLogout"]');

    logoutLinks.forEach(logoutLink => {
        // La forma más limpia de resetear listeners en un DOM dinámico:
        // Clonar el nodo y reemplazarlo para eliminar cualquier evento anterior.
        const newLogoutLink = logoutLink.cloneNode(true);
        logoutLink.parentNode.replaceChild(newLogoutLink, logoutLink);

        // Ahora adjuntamos el evento al nuevo elemento, garantizando que el listener solo exista una vez
        newLogoutLink.addEventListener('click', async (e) => {
            e.preventDefault();

            // Lógica de cierre de sesión
            try {
                // Ajusta esta URL si tu endpoint de logout es diferente
                await fetch('/logout', { method: 'POST' });
                // Redirigir al inicio de la aplicación
                window.location.href = 'http://localhost:5000/index.html';
            } catch (err) {
                console.error('Error al cerrar sesión:', err);
                alert('Ocurrió un error al intentar cerrar la sesión.');
            }
        });
    });
}


// Carga los componentes usando la ruta 'components/' cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // 1. Cargar Navbar desde components/
    loadHtmlComponent('components/navbar_admin.html', 'navbar-container');
    // 2. Cargar Sidebar desde components/ (Asegúrate de cargar el que corresponda: sidebar.html o sidebar_admin.html)
    loadHtmlComponent('components/sidebar_admin.html', 'sidebar-container');
});