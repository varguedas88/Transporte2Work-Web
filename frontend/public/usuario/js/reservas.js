let currentUser = null;

// Mostrar notificación
function showNotification(message, type = 'success') {
  const notification = document.getElementById('notification');
  notification.textContent = message;
  notification.className = `notification ${type}`;
  notification.style.display = 'block';
  
  setTimeout(() => {
    notification.style.display = 'none';
  }, 3000);
}

// Cargar datos del usuario actual
async function loadUserData() {
  try {
    const res = await fetch('/check-user');
    const data = await res.json();
    
    if (!data.logged_in || data.user.rol !== 'usuario') {
      // Redirigir a login si no está logueado como usuario normal
      window.location.href = '../login.html';
      return;
    }
    currentUser = data.user;
  } catch (err) {
    showNotification('Error al cargar datos del usuario', 'error');
    window.location.href = '../login.html';
  }
}

// Cargar lista de buses
async function loadBuses() {
  try {
    const res = await fetch('/admin/buses');
    const buses = await res.json();
    
    const select = document.getElementById('bus');
    select.innerHTML = '<option value="">Seleccione un bus</option>';
    
    buses.forEach(bus => {
      const option = document.createElement('option');
      option.value = bus.id;
      option.textContent = `${bus.placa} - ${bus.modelo} (${bus.capacidad} pasajeros)`;
      select.appendChild(option);
    });
  } catch (err) {
    showNotification('Error al cargar buses', 'error');
  }
}

// Cargar reservas del usuario
async function loadReservas() {
  try {
    const res = await fetch('/admin/reservas');
    const reservas = await res.json();
    
    // Filtrar solo las reservas del usuario actual
    const userReservas = reservas.filter(r => r.usuario_id == currentUser.id);
    
    const container = document.getElementById('reservas-lista');
    
    if (userReservas.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <h3>No tienes reservas aún</h3>
          <p>Solicita tu primera reserva de transporte haciendo clic en el botón "Nueva Reserva".</p>
        </div>
      `;
      return;
    }
    
    let html = '';
    userReservas.forEach(reserva => {
      const fechaInicio = reserva.fecha_inicio ? new Date(reserva.fecha_inicio).toLocaleDateString('es-ES') : '—';
      const fechaFin = reserva.fecha_fin ? new Date(reserva.fecha_fin).toLocaleDateString('es-ES') : '—';
      const statusClass = reserva.estado === 'finalizado' ? 'status-finalizado' : 'status-en-curso';
      
      html += `
        <div class="reserva-card">
          <div class="reserva-header">
            <div>
              <h3>Reserva #${reserva.id}</h3>
              <div class="reserva-id">Bus: ${reserva.bus || '—'}</div>
            </div>
            <span class="reserva-status ${statusClass}">${reserva.estado === 'finalizado' ? 'Finalizado' : 'En curso'}</span>
          </div>
          <div class="reserva-details">
            <div class="detail-item">
              <span class="detail-label">Fecha de inicio</span>
              <div class="detail-value">${fechaInicio}</div>
            </div>
            <div class="detail-item">
              <span class="detail-label">Fecha de fin</span>
              <div class="detail-value">${fechaFin}</div>
            </div>
          </div>
        </div>
      `;
    });
    
    container.innerHTML = html;
  } catch (err) {
    showNotification('Error al cargar reservas', 'error');
    document.getElementById('reservas-lista').innerHTML = '<p>Error al cargar tus reservas. Por favor, intenta nuevamente.</p>';
  }
}

// Inicializar modal
function initModal() {
  const modal = document.getElementById('modal-reserva');
  const btnNueva = document.getElementById('btn-nueva-reserva');
  const closeBtn = document.getElementById('close-modal');
  const cancelBtn = document.getElementById('cancel-modal');
  
  // Abrir modal
  btnNueva.addEventListener('click', (e) => {
    e.preventDefault();
    modal.style.display = 'block';
    loadBuses();
  });
  
  // Cerrar modal
  function closeModal() {
    modal.style.display = 'none';
    document.getElementById('form-reserva').reset();
  }
  
  closeBtn.addEventListener('click', closeModal);
  cancelBtn.addEventListener('click', closeModal);
  
  // Cerrar al hacer clic fuera del modal
  window.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });
}

// Manejar envío del formulario de reserva
async function handleReservaSubmit(e) {
  e.preventDefault();
  
  const busId = document.getElementById('bus').value;
  const fechaInicio = document.getElementById('fecha_inicio').value;
  
  if (!busId || !fechaInicio) {
    showNotification('Por favor complete todos los campos requeridos', 'error');
    return;
  }
  
  try {
    const payload = {
      usuario_id: currentUser.id,
      bus_id: parseInt(busId),
      fecha_inicio: fechaInicio,
      fecha_fin: document.getElementById('fecha_fin').value || null,
      estado: 'en curso'
    };
    
    const res = await fetch('/admin/reservas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    if (res.ok) {
      showNotification('Reserva solicitada exitosamente', 'success');
      document.getElementById('modal-reserva').style.display = 'none';
      document.getElementById('form-reserva').reset();
      loadReservas(); // Recargar la lista
    } else {
      const data = await res.json();
      showNotification(data.error || 'Error al crear la reserva', 'error');
    }
  } catch (err) {
    showNotification('Error de conexión', 'error');
  }
}

// Inicializar la página
document.addEventListener('DOMContentLoaded', async () => {
  await loadUserData();
  await loadReservas();
  initModal();
  
  // Enlazar el formulario
  document.getElementById('form-reserva').addEventListener('submit', handleReservaSubmit);
});