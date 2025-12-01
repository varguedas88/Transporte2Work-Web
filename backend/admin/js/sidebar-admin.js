document.getElementById('btnLogout').addEventListener('click', async (e) => {
  e.preventDefault();
  if (!confirm('¿Estás seguro de que deseas cerrar sesión?')) return;

  try {
    const res = await fetch('/logout', { method: 'POST' });
    if (res.ok) {
      window.location.href = '/admin/dashboard.html';
    } else {
      alert('Error al cerrar sesión');
    }
  } catch (err) {
    alert('No se pudo conectar al servidor');
  }
});