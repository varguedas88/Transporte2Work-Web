function highlightActiveLink() {
    // Obtiene la ruta de la página actual (ej: /mapa.html)
    const currentPath = window.location.pathname.split('/').pop();

    // Si la ruta es vacía (p. ej., página de inicio, index.html por defecto), la tratamos como 'index.html'
    const activePage = currentPath || 'index.html';

    // Selecciona todos los enlaces dentro de los menús (invitado y usuario)
    const menuLinks = document.querySelectorAll('#guest-menu .nav-link, #user-menu .nav-link');

    menuLinks.forEach(link => {
        // Obtiene la ruta del enlace del menú (ej: mapa.html)
        const linkPath = link.getAttribute('href').split('/').pop();

        // 1. Quitar la clase activa de todos los enlaces
        link.classList.remove('bg-primary', 'text-white', 'rounded-3', 'active');
        link.classList.add('text-dark'); // Asegura que el color base sea oscuro
        link.removeAttribute('aria-current');

        // 2. Comprobar si la ruta del enlace coincide con la página actual
        if (linkPath === activePage) {
            // Aplicar las clases de activo (Bootstrap)
            link.classList.add('bg-primary', 'text-white', 'rounded-3', 'active');
            link.classList.remove('text-dark');
            link.setAttribute('aria-current', 'page');
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    // 1. Cargar Navbar
    loadHtmlComponent('components/navbar.html', 'navbar-container');

    // 2. Cargar Sidebar
    // **IMPORTANTE:** Llama a la función de resaltado después de cargar el sidebar
    loadHtmlComponent('components/sidebar.html', 'sidebar-container').then(() => {
        // Ejecutar el resaltado después de que el sidebar se ha inyectado en el DOM
        highlightActiveLink();

        // También puedes llamar aquí a la lógica de sesión (si existe)
        if (window.checkSessionAndMenus) {
             window.checkSessionAndMenus();
        }
    });
});