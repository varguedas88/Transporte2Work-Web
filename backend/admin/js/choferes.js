async function cargarChoferes() {
    const res = await fetch("/admin/choferes");
    const data = await res.json();

    const tbody = document.getElementById("tablaChoferes");
    tbody.innerHTML = "";

    data.forEach(c => {
        tbody.innerHTML += `
            <tr>
                <td>${c.nombre}</td>
                <td>${c.telefono ?? ""}</td>
                <td>${c.cedula ?? ""}</td>
                <td>${c.licencia_tipo}</td>
                <td>${c.fecha_contratacion ?? ""}</td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editar(${c.id})">Editar</button>
                    <button class="btn btn-sm btn-danger" onclick="eliminar(${c.id})">Eliminar</button>
                </td>
            </tr>
        `;
    });
}

document.getElementById("formChofer").addEventListener("submit", async (e) => {
    e.preventDefault();

    let id = document.getElementById("id").value;

    let data = {
        nombre: document.getElementById("nombre").value,
        telefono: document.getElementById("telefono").value,
        cedula: document.getElementById("cedula").value,
        licencia_tipo: document.getElementById("licencia").value,
        fecha_contratacion: document.getElementById("fecha_contratacion").value
    };

    if (!id) {
        await fetch("/admin/choferes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
    } else {
        await fetch(`/admin/choferes/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
    }

    e.target.reset();
    cargarChoferes();
    document.getElementById("form-title").innerText = "Agregar Chofer";
    document.getElementById("id").value = "";
});

async function editar(id) {
    const res = await fetch("/admin/choferes");
    const choferes = await res.json();
    const c = choferes.find(x => x.id == id);

    document.getElementById("id").value = c.id;
    document.getElementById("nombre").value = c.nombre;
    document.getElementById("telefono").value = c.telefono;
    document.getElementById("cedula").value = c.cedula;
    document.getElementById("licencia").value = c.licencia_tipo;
    document.getElementById("fecha_contratacion").value = c.fecha_contratacion;

    document.getElementById("form-title").innerText = "Editar Chofer";
}

async function eliminar(id) {
    if (!confirm("¿Eliminar chofer?")) return;
    await fetch(`/admin/choferes/${id}`, { method: "DELETE" });
    cargarChoferes();
}

cargarChoferes();
