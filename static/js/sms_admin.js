// 🌐 Variables de paginación -
let paginaActual = 1;
const registrosPorPagina = 5;

// 🥪 Filtros activos
let filtroUsuario = "";
let filtroSucursal = "";
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
  filtroSucursal    = document.getElementById("sucursalSelect").value;
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
    filtroSucursal    && `sucursal=${filtroSucursal}`,
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
  if (filtroSucursal)    url += `&sucursal=${filtroSucursal}`;
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

    const data = await res.json();
    const sms = data.sms || data; // Soportar ambos formatos

    // 🔃 Ordenar por fecha descendente (últimos arriba)
    sms.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));

    const fragment = document.createDocumentFragment();
    sms.forEach((s, index) => {
      const tr = document.createElement("tr");

      // ✨ Filas más compactas con hover suave
      tr.className = "hover:bg-gray-800/50 transition-colors duration-150";

      tr.innerHTML = `
        <td class="px-3 py-2.5 text-xs">${s.dni}</td>
        <td class="px-3 py-2.5 text-xs">${s.celular}</td>
        <td class="px-3 py-2.5 text-xs">
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/20 text-purple-300 font-medium">
            <i data-lucide="building-2" class="w-3 h-3"></i>
            ${s.sucursal}
          </span>
        </td>
        <td class="px-3 py-2.5 text-xs">
          <span class="font-mono font-semibold text-emerald-300">${s.codigo}</span>
        </td>
        <td class="px-3 py-2.5 text-xs">
          <span class="text-gray-200">${s.usuario_nombre}</span>
        </td>
        <td class="px-3 py-2.5 text-xs text-gray-300">
          ${new Date(s.fecha).toLocaleDateString()} ${new Date(s.fecha).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </td>
        <td class="px-3 py-2.5 text-center">${getEstadoBadge(s.estado)}</td>
      `;
      fragment.appendChild(tr);
    });

    tbody.innerHTML = "";
    tbody.appendChild(fragment);
    
    // Reiniciar iconos de Lucide
    lucide.createIcons();

    // 🔢 Actualización visual de controles de paginación
    const paginaActualEl   = document.getElementById("paginaActual");
    const prevPaginaBtn    = document.getElementById("prevPagina");
    const nextPaginaBtn    = document.getElementById("nextPagina");
    const rangoRegistrosEl = document.getElementById("rangoRegistros");

    if (paginaActualEl) paginaActualEl.textContent = paginaActual;
    if (prevPaginaBtn)  prevPaginaBtn.disabled = paginaActual === 1;
    if (nextPaginaBtn)  nextPaginaBtn.disabled = paginaActual * registrosPorPagina >= totalRegistros;

    const inicio = (paginaActual - 1) * registrosPorPagina + 1;
    const fin = Math.min(paginaActual * registrosPorPagina, totalRegistros);
    if (rangoRegistrosEl) rangoRegistrosEl.textContent = `Mostrando registros ${inicio}–${fin} de ${totalRegistros}`;
  } catch (error) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-red-500">Error inesperado: ${error.message}</td></tr>`;
    console.error("Error inesperado:", error);
  }
}

// 🎨 Función para generar badge de estado con color
function getEstadoBadge(estado) {
  const estadoLower = (estado || "").toLowerCase();
  
  if (estadoLower === "test") {
    return `<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold bg-yellow-500/20 text-yellow-300 border border-yellow-500/40">
      <span class="w-1.5 h-1.5 rounded-full bg-yellow-400"></span>
      Test
    </span>`;
  }
  
  if (estadoLower === "enviado") {
    return `<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold bg-green-500/20 text-green-300 border border-green-500/40">
      <span class="w-1.5 h-1.5 rounded-full bg-green-400"></span>
      Enviado
    </span>`;
  }
  
  if (estadoLower === "fallido") {
    return `<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold bg-red-500/20 text-red-300 border border-red-500/40">
      <span class="w-1.5 h-1.5 rounded-full bg-red-400"></span>
      Fallido
    </span>`;
  }
  
  // Estado desconocido
  return `<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold bg-gray-500/20 text-gray-300 border border-gray-500/40">
    <span class="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
    ${estado}
  </span>`;
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
    filtroSucursal    && `sucursal=${filtroSucursal}`,
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
            <td>${r.estado || 'N/A'}</td>
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


function limpiarFiltros() {
  // Reset visual de inputs
  document.getElementById("usuarioSelect").selectedIndex = 0;
  document.getElementById("sucursalSelect").selectedIndex = 0;
  document.getElementById("fechaInicio").value = "";
  document.getElementById("fechaFin").value = "";
  document.getElementById("estadoSelect").selectedIndex = 0;

  // Reset de variables globales
  filtroUsuario = "";
  filtroSucursal = "";
  filtroFechaInicio = "";
  filtroFechaFin = "";
  filtroEstado = "";

  // Actualizar visualmente tabla
  paginaActual = 1;
  obtenerTotalRegistros().then(() => {
    cargarPagina();
  });
}


// 📅 Consultar fecha de vencimiento del paquete prepago
async function consultarVencimiento() {
  const btnConsultar = document.getElementById("btnConsultarVencimiento");
  const fechaVencimientoEl = document.getElementById("fechaVencimiento");
  const diasRestantesEl = document.getElementById("diasRestantes");

  // Mostrar estado de carga
  btnConsultar.disabled = true;
  btnConsultar.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Consultando...';
  lucide.createIcons();
  
  fechaVencimientoEl.textContent = "Consultando...";
  diasRestantesEl.textContent = "Espere un momento...";

  try {
    const res = await fetch("/send-sms/obtener-vencimiento");
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Error al consultar vencimiento");
    }

    if (data.ok) {
      const fechaVencimiento = data.fecha_vencimiento;
      fechaVencimientoEl.textContent = formatearFecha(fechaVencimiento);
      
      // Calcular días restantes
      const diasRestantes = calcularDiasRestantes(fechaVencimiento);
      
      if (diasRestantes < 0) {
        diasRestantesEl.textContent = "⚠️ Paquete vencido";
        diasRestantesEl.className = "text-xs text-red-400 mt-1 font-semibold";
      } else if (diasRestantes <= 7) {
        diasRestantesEl.textContent = `⚠️ ${diasRestantes} días restantes`;
        diasRestantesEl.className = "text-xs text-yellow-400 mt-1 font-semibold";
      } else {
        diasRestantesEl.textContent = `✓ ${diasRestantes} días restantes`;
        diasRestantesEl.className = "text-xs text-gray-400 mt-1";
      }

      if (data.simulado) {
        diasRestantesEl.textContent += " (Simulado)";
      }
    } else {
      throw new Error(data.mensaje || "Error desconocido");
    }

  } catch (error) {
    console.error("Error al consultar vencimiento:", error);
    fechaVencimientoEl.textContent = "Error";
    diasRestantesEl.textContent = error.message;
    diasRestantesEl.className = "text-xs text-red-400 mt-1";
  } finally {
    // Restaurar botón
    btnConsultar.disabled = false;
    btnConsultar.innerHTML = '<i data-lucide="refresh-cw" class="w-4 h-4"></i> Consultar';
    lucide.createIcons();
  }
}


// 🔄 Formatear fecha en formato legible
function formatearFecha(fechaStr) {
  try {
    // Intentar parsear diferentes formatos de fecha
    const fecha = new Date(fechaStr);
    if (isNaN(fecha.getTime())) {
      // Si no es una fecha válida, devolver el texto tal cual
      return fechaStr;
    }
    
    const dia = fecha.getDate().toString().padStart(2, '0');
    const mes = (fecha.getMonth() + 1).toString().padStart(2, '0');
    const año = fecha.getFullYear();
    
    return `${dia}/${mes}/${año}`;
  } catch {
    return fechaStr;
  }
}


// 📊 Calcular días restantes hasta el vencimiento
function calcularDiasRestantes(fechaStr) {
  try {
    const fechaVencimiento = new Date(fechaStr);
    const hoy = new Date();
    
    // Resetear horas para comparar solo fechas
    fechaVencimiento.setHours(0, 0, 0, 0);
    hoy.setHours(0, 0, 0, 0);
    
    const diferencia = fechaVencimiento - hoy;
    const dias = Math.ceil(diferencia / (1000 * 60 * 60 * 24));
    
    return dias;
  } catch {
    return 0;
  }
}




