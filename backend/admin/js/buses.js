async function cargarChoferes() {
  const res = await fetch(apiBase + '/choferes');
  const data = await res.json();
  const select = document.getElementById('chofer_id');
  select.innerHTML = '<option value="">Seleccione un chofer</option>';

  data.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = c.nombre;
    select.appendChild(opt);
  });
}
document.getElementById('btnNuevo').onclick = async () => {
  await cargarChoferes();
  document.getElementById('busId').value='';
  document.getElementById('formBus').reset();
  modalBus.show();
}
await cargarChoferes();
document.getElementById('chofer_id').value = b.chofer_id ?? "";
