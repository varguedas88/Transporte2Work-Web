document.addEventListener('DOMContentLoaded', function() {
  const guestMenu = document.getElementById('guest-menu');
  const userMenu = document.getElementById('user-menu');
  const logoutLink = document.getElementById('logout-link');

  // --- Lógica de Sesión y Menús ---

  // Verificar sesión al cargar
  fetch('/check-user')
    .then(res => res.json())
    .then(data => {
      if (data.logged_in && data.user.rol === 'usuario') {
        // Mostrar menú de usuario
        if (guestMenu) guestMenu.style.display = 'none';
        if (userMenu) userMenu.style.display = 'block';
      } else {
        // Mostrar menú de invitado por defecto
        if (guestMenu) guestMenu.style.display = 'block';
        if (userMenu) userMenu.style.display = 'none';
      }
    })
    .catch(err => {
      console.log('No se pudo verificar sesión:', err);
      // Asegurar que el menú de invitado esté visible si falla la verificación
      if (guestMenu) guestMenu.style.display = 'block';
    });

  // Cerrar sesión
  if (logoutLink) {
    logoutLink.addEventListener('click', async (e) => {
      e.preventDefault();
      try {
        await fetch('/logout-publico', { method: 'POST' });
        window.location.href = 'index.html';
      } catch (err) {
        alert('Error al cerrar sesión');
      }
    });
  }
});