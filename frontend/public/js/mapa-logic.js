document.addEventListener('DOMContentLoaded', function() {
  // Lógica del Mapa (OpenStreetMap/Leaflet)
  const lat = 9.935;   // Coordenadas de ejemplo (San José, Costa Rica)
  const lng = -84.090;

  // Inicializa el mapa en el elemento con id 'map' y establece la vista.
  const map = L.map('map').setView([lat, lng], 13);

  // Agrega las capas de OpenStreetMap.
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  // Agrega un marcador en la ubicación y muestra un popup.
  L.marker([lat, lng]).addTo(map)
    .bindPopup('Oficinas 2Work')
    .openPopup();
});