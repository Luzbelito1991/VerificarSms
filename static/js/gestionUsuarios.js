document.addEventListener("DOMContentLoaded", () => {
  iniciarBusqueda();
  iniciarFormulario();
  iniciarPaginacion();
  iniciarModal();
  lucide.createIcons();
});

/* ==================== 🔍 BÚSQUEDA ==================== */
function iniciarBusqueda() {
  const inputBusqueda = document.getElementById("buscarUsuarioTabla");
  if (!inputBusqueda) return;

  inputBusqueda.addEventListener("input", () => {
    const filtro = inputBusqueda.value.toLowerCase();
    const filas = document.querySelectorAll("#tablaUsuariosBody tr");

    filas.forEach((fila) => {
      const nombre = fila.querySelector(".nombre-usuario")?.textContent.toLowerCase() || "";
      fila.style.display = nombre.includes(filtro) ? "" : "none";
    });
  });
}

/* ==================== 🧾 FORMULARIO ==================== */
function iniciarFormulario() {
  const form = document.getElementById("userForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const modo = document.getElementById("modo").value;
    const nombre = document.getElementById("usuario").value.trim();
    const password = document.getElementById("password").value;
    const rol = document.getElementById("rol").value;
    const original = document.getElementById("originalUsuario").value;

    if (!nombre || !rol) {
      alert("Completá los campos requeridos.");
      return;
    }

    if (modo === "crear") {
      try {
        const response = await fetch("/crear-usuario", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ usuario: nombre, password, rol }),
        });

        const data = await response.json();

        if (response.ok && data.ok) {
          // ✅ Usa valores estructurados para evitar 'undefined'
          agregarFilaATabla({
            nombre: data.usuario,
            rol: data.rol
          });
          cerrarModal();
        } else {
          alert(data.detail || "Error al crear el usuario.");
        }
      } catch (err) {
        console.error("Error:", err);
        alert("Error al conectar con el servidor.");
      }
    } else if (modo === "editar") {
      try {
        const response = await fetch(`/editar-usuario/${encodeURIComponent(original)}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ password, rol }),
        });

        const data = await response.json();

        if (response.ok) {
          actualizarFilaDeTabla(nombre, rol);
          cerrarModal();
        } else {
          alert(data.detail || "Error al actualizar el usuario.");
        }
      } catch (err) {
        console.error("Error:", err);
        alert("Error al conectar con el servidor.");
      }
    }
  });
}

function reiniciarFormulario() {
  document.getElementById("modo").value = "crear";
  document.getElementById("submitLabel").textContent = "Crear";
  document.getElementById("usuario").value = "";
  document.getElementById("password").value = "";
  document.getElementById("rol").value = "";
  document.getElementById("originalUsuario").value = "";
}

/* ==================== 📋 ACCIONES DE TABLA ==================== */
function verUsuario(nombre) {
  alert(`👁️ Ver usuario: ${nombre}`);
}

function editarUsuario(nombre) {
  document.getElementById("modo").value = "editar";
  document.getElementById("submitLabel").textContent = "Actualizar";
  document.getElementById("usuario").value = nombre;
  document.getElementById("password").value = "";
  document.getElementById("rol").value = obtenerRolDeFila(nombre);
  document.getElementById("originalUsuario").value = nombre;

  abrirModal();
}

function eliminarUsuario(nombre) {
  if (!confirm(`¿Estás seguro que querés eliminar a "${nombre}"?`)) return;

  fetch(`/eliminar-usuario/${encodeURIComponent(nombre)}`, {
    method: "DELETE",
  })
    .then(async (res) => {
      const data = await res.json();
      if (res.ok) {
        eliminarFilaDeTabla(nombre);
      } else {
        alert(data.detail || "Error al eliminar el usuario.");
      }
    })
    .catch((err) => {
      console.error("Error:", err);
      alert("Error al conectar con el servidor.");
    });
}

function obtenerRolDeFila(nombre) {
  const filas = document.querySelectorAll("#tablaUsuariosBody tr");
  for (const fila of filas) {
    const celdaNombre = fila.querySelector(".nombre-usuario");
    const celdaRol = fila.querySelector("td:nth-child(2)");
    if (celdaNombre && celdaNombre.textContent === nombre) {
      return celdaRol.textContent;
    }
  }
  return "operador";
}

function actualizarFilaDeTabla(nombre, nuevoRol) {
  const filas = document.querySelectorAll("#tablaUsuariosBody tr");
  for (const fila of filas) {
    const celdaNombre = fila.querySelector(".nombre-usuario");
    const celdaRol = fila.querySelector("td:nth-child(2)");
    if (celdaNombre && celdaNombre.textContent === nombre) {
      celdaRol.textContent = nuevoRol;
      break;
    }
  }
}

function eliminarFilaDeTabla(nombre) {
  const filas = document.querySelectorAll("#tablaUsuariosBody tr");
  for (const fila of filas) {
    const celda = fila.querySelector(".nombre-usuario");
    if (celda && celda.textContent === nombre) {
      fila.remove();
      break;
    }
  }
}

/* ==================== 🔁 PAGINACIÓN ==================== */
function iniciarPaginacion() {
  const btnPrev = document.getElementById("prevPagina");
  const btnNext = document.getElementById("nextPagina");
  if (!btnPrev || !btnNext) return;

  let paginaActual = 1;

  btnPrev.addEventListener("click", () => {
    if (paginaActual > 1) {
      paginaActual--;
      actualizarPaginacion();
    }
  });

  btnNext.addEventListener("click", () => {
    paginaActual++;
    actualizarPaginacion();
  });

  function actualizarPaginacion() {
    document.getElementById("paginaActual").textContent = paginaActual;
    console.log(`Página actual: ${paginaActual}`);
  }
}

/* ==================== 💡 MODAL ALTA/EDICIÓN ==================== */
function iniciarModal() {
  const btnMostrar = document.getElementById("mostrarFormularioBtn");
  const modal = document.getElementById("modalUsuario");
  const cerrarBtn = modal?.querySelector("button[onclick*='cerrarModal']");

  btnMostrar?.addEventListener("click", () => {
    reiniciarFormulario();
    abrirModal();
  });

  cerrarBtn?.addEventListener("click", cerrarModal);
}

function abrirModal() {
  const modal = document.getElementById("modalUsuario");
  if (!modal) return;
  modal.classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

function cerrarModal() {
  const modal = document.getElementById("modalUsuario");
  if (!modal) return;
  modal.classList.add("hidden");
  document.body.style.overflow = "";
}

/* ==================== ➕ AGREGAR NUEVA FILA ==================== */
function agregarFilaATabla(usuario) {
  const tbody = document.getElementById("tablaUsuariosBody");

  const fila = document.createElement("tr");
  fila.className = "hover:bg-white/5 transition border-b border-white/5";

  fila.innerHTML = `
    <td class="px-4 py-2 font-medium nombre-usuario">${usuario.nombre}</td>
    <td class="px-4 py-2 text-emerald-300">${usuario.rol}</td>
    <td class="px-4 py-2">
      <div class="flex gap-3 text-sm items-center">
        <button onclick="verUsuario('${usuario.nombre}')" class="text-white hover:text-emerald-400 inline-flex items-center gap-1">
          <i data-lucide="eye" class="w-4 h-4"></i> Ver
        </button>
        <button onclick="editarUsuario('${usuario.nombre}')" class="text-white hover:text-blue-400 inline-flex items-center gap-1">
          <i data-lucide="edit-2" class="w-4 h-4"></i> Editar
        </button>
        <button onclick="eliminarUsuario('${usuario.nombre}')" class="text-white hover:text-red-400 inline-flex items-center gap-1">
          <i data-lucide="trash-2" class="w-4 h-4"></i> Eliminar
        </button>
      </div>
    </td>
  `;

    tbody.appendChild(fila);
  lucide.createIcons(); // Re-renderiza los íconos dinámicamente
}
