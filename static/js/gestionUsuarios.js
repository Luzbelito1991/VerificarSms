let usuariosTotales = [];
let paginaActual = 1;
const usuariosPorPagina = 5;
let coincidenciasActivas = null;
let ultimoRenderizado = "";

document.addEventListener("DOMContentLoaded", () => {
  iniciarBusqueda();
  iniciarFormulario();
  iniciarPaginacion();
  iniciarModal();
  cargarUsuariosEnTabla();
  lucide.createIcons();
});

function obtenerFuenteActual() {
  return coincidenciasActivas || usuariosTotales;
}

/* 🔍 BÚSQUEDA desde backend con debounce */
function iniciarBusqueda() {
  const input = document.getElementById("buscarUsuarioTabla");
  if (!input) return;

  let debounceTimeout;

  input.addEventListener("input", () => {
    clearTimeout(debounceTimeout);

    const filtro = input.value.trim().toLowerCase();

    input.classList.toggle("ring-emerald-400", filtro.length >= 2);
    input.classList.toggle("ring-0", filtro.length < 2);

    debounceTimeout = setTimeout(async () => {
      if (filtro.length < 2) {
        coincidenciasActivas = null;
        paginaActual = 1;
        renderizarPagina(paginaActual);
        return;
      }

      try {
        const res = await fetch(`/usuarios?search=${encodeURIComponent(filtro)}`);
        const data = await res.json();
        coincidenciasActivas = data;
        paginaActual = 1;
        renderizarSinPaginacion();
      } catch (error) {
        console.error("Error en búsqueda:", error);
      }
    }, 200);
  });
}

/* ✅ Render sin parpadeo */
function renderizarSinPaginacion() {
  const tabla = document.getElementById("tablaUsuariosBody");
  if (!tabla) return;

  const fuente = obtenerFuenteActual();
  tabla.innerHTML = "";

  if (!fuente.length) {
    tabla.innerHTML = `<tr><td colspan="3" class="text-center text-gray-400 italic py-3">No hay coincidencias</td></tr>`;
  } else {
    const fragmento = document.createDocumentFragment();

    fuente.forEach(user => {
      const fila = document.createElement("tr");
      fila.className = "fila-usuario border-b border-white/5 hover:bg-white/5 transition opacity-0";
      fila.dataset.usuario = user.usuario;

      fila.innerHTML = `
        <td class="px-4 py-2 nombre-usuario">${user.usuario}</td>
        <td class="px-4 py-2 capitalize">${user.rol}</td>
        <td class="px-6 py-3 w-[180px]">
          <div class="flex justify-center gap-4">
            <button onclick="editarUsuario('${user.usuario}')" class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center gap-2 px-2 py-1 rounded-md transition">
              <i data-lucide="edit" class="w-4 h-4"></i><span>Editar</span>
            </button>
            <button onclick="eliminarUsuario('${user.usuario}')" class="text-red-500 hover:text-red-400 text-sm font-medium flex items-center gap-2 px-2 py-1 rounded-md transition">
              <i data-lucide="trash-2" class="w-4 h-4"></i><span>Eliminar</span>
            </button>
          </div>
        </td>
      `;
      fragmento.appendChild(fila);
    });

    tabla.appendChild(fragmento);
  }

  document.getElementById("paginaActual").textContent = "-";
  setTimeout(() => lucide.createIcons(), 0);
  actualizarBotonesPaginacion();

  requestAnimationFrame(() => {
    tabla.querySelectorAll(".fila-usuario").forEach(tr => {
      tr.style.transition = "opacity 0.25s ease";
      tr.style.opacity = "1";
    });
  });
}

/* 🧮 Render por página */
function renderizarPagina(pagina) {
  const tabla = document.getElementById("tablaUsuariosBody");
  if (!tabla) return;

  const fuente = obtenerFuenteActual();
  const inicio = (pagina - 1) * usuariosPorPagina;
  const fin = inicio + usuariosPorPagina;
  const usuariosPagina = fuente.slice(inicio, fin);

  tabla.innerHTML = usuariosPagina.length
    ? usuariosPagina.map(user => `
      <tr data-usuario="${user.usuario}" class="border-b border-white/5 hover:bg-white/5 transition">
        <td class="px-4 py-2 nombre-usuario">${user.usuario}</td>
        <td class="px-4 py-2 capitalize">${user.rol}</td>
        <td class="px-6 py-3 w-[180px]">
          <div class="flex justify-center gap-4">
            <button onclick="editarUsuario('${user.usuario}')" class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center gap-2 px-2 py-1 rounded-md transition">
              <i data-lucide="edit" class="w-4 h-4"></i><span>Editar</span>
            </button>
            <button onclick="eliminarUsuario('${user.usuario}')" class="text-red-500 hover:text-red-400 text-sm font-medium flex items-center gap-2 px-2 py-1 rounded-md transition">
              <i data-lucide="trash-2" class="w-4 h-4"></i><span>Eliminar</span>
            </button>
          </div>
        </td>
      </tr>
    `).join("")
    : `<tr><td colspan="3" class="text-center text-gray-400 italic py-3">No hay coincidencias</td></tr>`;

  document.getElementById("paginaActual").textContent = pagina;
  lucide.createIcons();
  actualizarBotonesPaginacion();
}

/* 🔁 Paginación básica */
function iniciarPaginacion() {
  const btnPrev = document.getElementById("prevPagina");
  const btnNext = document.getElementById("nextPagina");
  if (!btnPrev || !btnNext) return;

  btnPrev.addEventListener("click", () => {
    if (paginaActual > 1) {
      paginaActual--;
      renderizarPagina(paginaActual);
    }
  });

  btnNext.addEventListener("click", () => {
    const fuente = obtenerFuenteActual();
    const totalPaginas = Math.ceil(fuente.length / usuariosPorPagina);
    if (paginaActual < totalPaginas) {
      paginaActual++;
      renderizarPagina(paginaActual);
    }
  });
}

function actualizarBotonesPaginacion() {
  const fuente = obtenerFuenteActual();
  const totalPaginas = Math.ceil(fuente.length / usuariosPorPagina);
  const btnPrev = document.getElementById("prevPagina");
  const btnNext = document.getElementById("nextPagina");
  const infoLabel = document.getElementById("infoPaginacion");
  const inicio = (paginaActual - 1) * usuariosPorPagina + 1;
  const fin = Math.min(inicio + usuariosPorPagina - 1, fuente.length);

  if (infoLabel) {
    infoLabel.textContent = `Mostrando registros ${inicio}–${fin} de ${fuente.length}`;
  }

  if (!btnPrev || !btnNext || coincidenciasActivas) {
    btnPrev.disabled = true;
    btnNext.disabled = true;
    return;
  }

  btnPrev.disabled = paginaActual === 1;
  btnNext.disabled = paginaActual >= totalPaginas;
}

/* 📦 Cargar todos los usuarios */
async function cargarUsuariosEnTabla() {
  const tabla = document.getElementById("tablaUsuariosBody");
  if (!tabla || coincidenciasActivas) return;

  tabla.innerHTML = `<tr><td colspan="3" class="text-center text-gray-400 italic py-3">Cargando usuarios...</td></tr>`;

  try {
    const res = await fetch("/usuarios");
    const data = await res.json();
    usuariosTotales = data;
    coincidenciasActivas = null;
    paginaActual = 1;
    renderizarPagina(paginaActual);
  } catch (error) {
    console.error("Error al cargar usuarios:", error);
    tabla.innerHTML = `<tr><td colspan="3" class="text-center text-red-500 italic py-3">Error al cargar usuarios</td></tr>`;
  }
}

/* ✏️ Formulario Crear/Editar */
function iniciarFormulario() {
  const form = document.getElementById("userForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!validarCampos()) {
      mostrarToast("Completá los campos requeridos.", "error");
      return;
    }

        const modo = document.getElementById("modo").value;
    const nombre = document.getElementById("usuario").value.trim();
    const password = document.getElementById("password").value;
    const rol = document.getElementById("rol").value;
    const original = document.getElementById("originalUsuario").value;

    // 🔎 Validar duplicado al editar
    if (modo === "editar" && nombre !== original) {
      const existe = usuariosTotales.some(u => u.usuario.toLowerCase() === nombre.toLowerCase());
      if (existe) {
        mostrarToast(`❌ Ya existe un usuario llamado "${nombre}"`, "error");
        document.getElementById("usuario").classList.add("border-red-500", "ring-red-500");
        return;
      }
    }

    const payload = JSON.stringify({
      nuevo_usuario: nombre,
      password,
      rol
    });

    try {
      let res;
      if (modo === "crear") {
        res = await fetch("/crear-usuario", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: payload
        });
      } else {
        res = await fetch(`/editar-usuario/${encodeURIComponent(original)}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: payload
        });
      }

      const data = await res.json();

      if (res.ok) {
        mostrarToast(modo === "crear" ? "✅ Usuario creado" : "✅ Usuario actualizado", "success");
        reiniciarFormulario();
        cerrarModal();
        cargarUsuariosEnTabla();
      } else {
        const errorMsg = data?.detail || data?.mensaje || "Error al procesar usuario";
        mostrarToast(errorMsg, "error");
      }
    } catch (err) {
      console.error("Error:", err);
      mostrarToast("Error de conexión con el servidor", "error");
    }
  });
}

function validarCampos() {
  const usuario = document.getElementById("usuario");
  const rol = document.getElementById("rol");
  let valido = true;

  if (!usuario.value.trim()) {
    usuario.classList.add("border-red-500", "ring-red-500");
    valido = false;
  } else {
    usuario.classList.remove("border-red-500", "ring-red-500");
  }

  if (!rol.value) {
    rol.classList.add("border-red-500", "ring-red-500");
    valido = false;
  } else {
    rol.classList.remove("border-red-500", "ring-red-500");
  }

  return valido;
}

function reiniciarFormulario() {
  document.getElementById("modo").value = "crear";
  document.getElementById("submitLabel").textContent = "Crear";
  document.getElementById("usuario").disabled = false;
  document.getElementById("usuario").value = "";
  document.getElementById("password").value = "";
  document.getElementById("rol").value = "";
  document.getElementById("originalUsuario").value = "";
  document.getElementById("usuario").classList.remove("border-red-500", "ring-red-500");
  document.getElementById("rol").classList.remove("border-red-500", "ring-red-500");
}

async function editarUsuario(nombre) {
  document.getElementById("modo").value = "editar";
  document.getElementById("submitLabel").textContent = "Actualizar";
  document.getElementById("usuario").disabled = false;
  document.getElementById("usuario").value = nombre;
  document.getElementById("password").value = "";

  try {
    const res = await fetch(`/usuario-detalle/${encodeURIComponent(nombre)}`);
    const data = await res.json();
    if (res.ok && data.usuario) {
      document.getElementById("rol").value = data.rol || "";
    } else {
      mostrarToast(data.detail || "No se pudo cargar el rol del usuario", "warning");
      document.getElementById("rol").value = "";
    }
  } catch (error) {
    console.error("Error al cargar rol:", error);
    mostrarToast("Error de conexión al obtener datos del usuario", "error");
    document.getElementById("rol").value = "";
  }

  document.getElementById("originalUsuario").value = nombre;
  abrirModal();
}



async function eliminarUsuario(nombre) {
  const confirmado = confirm(`¿Querés eliminar al usuario "${nombre}"? Esta acción no se puede deshacer.`);
  if (!confirmado) return;

  try {
    const res = await fetch(`/eliminar-usuario/${encodeURIComponent(nombre)}`, {
      method: "DELETE"
    });
    const data = await res.json();

    if (res.ok && data.ok) {
      mostrarToast(`✅ Usuario "${nombre}" eliminado`, "success");
      cargarUsuariosEnTabla();
    } else {
      mostrarToast(data.detail || `❌ No se pudo eliminar el usuario "${nombre}"`, "error");
    }
  } catch (error) {
    console.error("Error eliminando usuario:", error);
    mostrarToast("❌ Error de conexión al intentar eliminar el usuario", "error");
  }
}

function iniciarModal() {
  const btnMostrar = document.getElementById("mostrarFormularioBtn");
  if (!btnMostrar) return;

  btnMostrar.addEventListener("click", () => {
    reiniciarFormulario();
    abrirModal();
  });
}

function abrirModal() {
  const modal = document.getElementById("modalUsuario");
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";
}

function cerrarModal() {
  const modal = document.getElementById("modalUsuario");
  if (!modal) return;
  modal.classList.remove("flex");
  modal.classList.add("hidden");
  document.body.style.overflow = "";
}

function mostrarToast(mensaje, tipo = "info") {
  const colores = {
    success: "bg-emerald-600",
    error: "bg-red-600",
    info: "bg-blue-600",
    warning: "bg-yellow-500"
  };

  const toast = document.createElement("div");
  toast.className = `${colores[tipo] || colores.info} text-white text-sm font-medium rounded-md px-4 py-2 shadow-lg animate-fade-in-down transition duration-300 pointer-events-auto`;
  toast.textContent = mensaje;

  const container = document.getElementById("toastContainer");
  container?.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("opacity-0", "scale-95");
    setTimeout(() => toast.remove(), 300);
  }, 2800);
}