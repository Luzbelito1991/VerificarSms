// 🌐 Variables de paginación -
let paginaActual = 1;
const registrosPorPagina = 5;

// 🥪 Filtros activos
let filtroUsuario = "";
let filtroFechaInicio = "";
let filtroFechaFin = "";
let filtroEstado = "";

// 🔢 Total de registros según filtros
let totalRegistros = 0;

// 🟢 Iniciar todo al cargar la página
document.addEventListener("DOMContentLoaded", () => {
  cargarUsuarios();
  iniciarPaginacion();
  aplicarFiltros();
});

// 👤 Carga los usuarios en el filtro
async function cargarUsuarios() {
  const select = document.getElementById("usuarioSelect");
  try {
    const res = await fetch("/api/usuarios");
    const usuarios = await res.json();
    usuarios.forEach(u => {
      const opt = document.createElement("option");
      opt.value = u.id;
      opt.textContent = u.nombre;
      select.appendChild(opt);
    });
  } catch (error) {
    console.error("Error al cargar usuarios:", error);
  }
}

// 🔍 Aplica filtros y actualiza tabla desde página 1
function aplicarFiltros() {
  paginaActual = 1;
  filtroUsuario     = document.getElementById("usuarioSelect").value;
  filtroFechaInicio = document.getElementById("fechaInicio").value;
  filtroFechaFin    = document.getElementById("fechaFin").value;
  filtroEstado      = document.getElementById("estadoSelect").value;

  obtenerTotalRegistros().then(() => {
    cargarPagina();
  });
}

// 🔢 Obtener cantidad total de registros con filtros activos
async function obtenerTotalRegistros() {
  const filtroParams = [
    filtroUsuario     && `usuario_id=${filtroUsuario}`,
    filtroFechaInicio && `fecha_inicio=${filtroFechaInicio}`,
    filtroFechaFin    && `fecha_fin=${filtroFechaFin}`,
    filtroEstado      && `estado=${filtroEstado}`
  ].filter(Boolean).join("&");

  const url = `/api/admin/sms/total${filtroParams ? "?" + filtroParams : ""}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    totalRegistros = data.total;
  } catch (error) {
    console.error("Error al contar registros:", error);
    totalRegistros = 0;
  }
}

// 📄 Cargar registros paginados y mostrarlos en la tabla
async function cargarPagina() {
  let url = `/api/admin/sms?skip=${(paginaActual - 1) * registrosPorPagina}&limit=${registrosPorPagina}`;

  if (filtroUsuario)     url += `&usuario_id=${filtroUsuario}`;
  if (filtroFechaInicio) url += `&fecha_inicio=${filtroFechaInicio}`;
  if (filtroFechaFin)    url += `&fecha_fin=${filtroFechaFin}`;
  if (filtroEstado)      url += `&estado=${filtroEstado}`;

  const tbody = document.getElementById("tablaBody");

  try {
    const res = await fetch(url);
    if (!res.ok) {
      const msg = await res.text();
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-red-500">Error ${res.status}: ${msg}</td></tr>`;
      console.error("Error al cargar página:", res.status, msg);
      return;
    }

    const sms = await res.json();

    const fragment = document.createDocumentFragment();
    sms.forEach(s => {
      const tr = document.createElement("tr");
      tr.className = "hover:bg-gray-900 transition";
      tr.innerHTML = `
        <td class="px-4 py-2">${s.dni}</td>
        <td class="px-4 py-2">${s.celular}</td>
        <td class="px-4 py-2">${s.sucursal}</td>
        <td class="px-4 py-2">${s.codigo}</td>
        <td class="px-4 py-2">${s.usuario_nombre}</td>
        <td class="px-4 py-2">${new Date(s.fecha).toLocaleDateString()}</td>
        <td class="px-4 py-2 capitalize">${s.estado}</td>
      `;
      fragment.appendChild(tr);
    });

    tbody.innerHTML = "";
    tbody.appendChild(fragment);

    const paginaActualEl   = document.getElementById("paginaActual");
    const prevPaginaBtn    = document.getElementById("prevPagina");
    const nextPaginaBtn    = document.getElementById("nextPagina");
    const rangoRegistrosEl = document.getElementById("rangoRegistros");

    if (paginaActualEl)   paginaActualEl.textContent = paginaActual;
    if (prevPaginaBtn)    prevPaginaBtn.disabled = paginaActual === 1;
    if (nextPaginaBtn)    nextPaginaBtn.disabled = paginaActual * registrosPorPagina >= totalRegistros;

    const inicio = (paginaActual - 1) * registrosPorPagina + 1;
    const fin = Math.min(paginaActual * registrosPorPagina, totalRegistros);
    if (rangoRegistrosEl) rangoRegistrosEl.textContent = `Mostrando registros ${inicio}–${fin} de ${totalRegistros}`;
  } catch (error) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-red-500">Error inesperado: ${error.message}</td></tr>`;
    console.error("Error inesperado:", error);
  }
}

// ⏮️⏭️ Controlar botones de paginación
function iniciarPaginacion() {
  const btnPrev = document.getElementById("prevPagina");
  const btnNext = document.getElementById("nextPagina");

  if (btnPrev) {
    btnPrev.addEventListener("click", () => {
      if (paginaActual > 1) {
        paginaActual--;
        cargarPagina();
      }
    });
  }

  if (btnNext) {
    btnNext.addEventListener("click", () => {
      if (paginaActual * registrosPorPagina < totalRegistros) {
        paginaActual++;
        cargarPagina();
      }
    });
  }
}

// 📁 Exportar todos los registros filtrados (sin paginación)
async function exportarExcel() {
  const filtroParams = [
    filtroUsuario     && `usuario_id=${filtroUsuario}`,
    filtroFechaInicio && `fecha_inicio=${filtroFechaInicio}`,
    filtroFechaFin    && `fecha_fin=${filtroFechaFin}`,
    filtroEstado      && `estado=${filtroEstado}`
  ].filter(Boolean).join("&");

  const url = `/api/admin/sms/todos${filtroParams ? "?" + filtroParams : ""}`;

  try {
    const res = await fetch(url);
    if (!res.ok) {
      const msg = await res.text();
      throw new Error(`Error ${res.status}: ${msg}`);
    }

    const registros = await res.json();
    if (registros.length === 0) {
      alert("No hay registros para exportar con los filtros actuales.");
      return;
    }

    const tabla = document.createElement("table");
    tabla.innerHTML = `
      <thead>
        <tr><th>DNI</th><th>Celular</th><th>Sucursal</th><th>Código</th><th>Usuario</th><th>Fecha</th><th>Estado</th></tr>
      </thead>
      <tbody>
        ${registros.map(r => `
          <tr>
            <td>${r.dni}</td>
            <td>${r.celular}</td>
            <td>${r.sucursal}</td>
            <td>${r.codigo}</td>
            <td>${r.usuario_nombre}</td>
            <td>${r.fecha}</td>
            <td>${r.estado}</td>
          </tr>
        `).join("")}
      </tbody>
    `;

    const wb = XLSX.utils.table_to_book(tabla, { sheet: "SMS Admin" });
    XLSX.writeFile(wb, "sms_admin_completo.xlsx");

  } catch (error) {
    console.error("⚠️ Exportación fallida:", error.message);
    alert("Error al exportar registros. Detalle: " + error.message);
  }
}