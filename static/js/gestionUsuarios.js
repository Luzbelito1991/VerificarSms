document.addEventListener("DOMContentLoaded", () => {
  iniciarBusqueda();
  iniciarFormulario();
  iniciarPaginacion();
  iniciarModal();
  cargarUsuariosEnTabla();
  lucide.createIcons();
});

/* ==================== 🔍 BÚSQUEDA ==================== */
function iniciarBusqueda() {
  const input = document.getElementById("buscarUsuarioTabla");
  if (!input) return;

  input.addEventListener("input", () => {
    const filtro = input.value.toLowerCase();
    document.querySelectorAll("#tablaUsuariosBody tr").forEach((fila) => {
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

    if (!validarCampos()) {
      mostrarToast("Completá los campos requeridos.", "error");
      return;
    }

    const modo = document.getElementById("modo").value;
    const nombre = document.getElementById("usuario").value.trim();
    const password = document.getElementById("password").value;
    const rol = document.getElementById("rol").value;
    const original = document.getElementById("originalUsuario").value;

    if (modo === "crear") {
      try {
        const res = await fetch("/crear-usuario", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ usuario: nombre, password, rol })
        });
        const data = await res.json();

        if (res.ok) {
          mostrarToast("✅ Usuario creado con éxito", "success");
          reiniciarFormulario();
          cerrarModal();
          cargarUsuariosEnTabla();
        } else {
          mostrarToast(data.detail || "Error al crear el usuario", "error");
        }
      } catch (err) {
        console.error("Error:", err);
        mostrarToast("Error al conectar con el servidor", "error");
      }
    }

    if (modo === "editar") {
      try {
        const res = await fetch(`/editar-usuario/${encodeURIComponent(original)}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ nuevo_usuario: nombre, password, rol })
        });
        const data = await res.json();

        if (res.ok) {
          mostrarToast(data.mensaje || "✅ Usuario actualizado", "success");
          reiniciarFormulario();
          cerrarModal();
          cargarUsuariosEnTabla();
        } else {
          mostrarToast(data.detail || "Error al actualizar el usuario", "error");
        }
      } catch (err) {
        console.error("Error:", err);
        mostrarToast("Error al conectar con el servidor", "error");
      }
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

/* ==================== 📊 CARGA DE TABLA ==================== */
async function cargarUsuariosEnTabla() {
  const tabla = document.getElementById("tablaUsuariosBody");
  if (!tabla) return;

  tabla.innerHTML = `<tr><td colspan="3" class="text-center text-gray-400 italic py-3">Cargando usuarios...</td></tr>`;

  try {
    const res = await fetch("/usuarios");
    const usuarios = await res.json();

    if (!usuarios.length) {
      tabla.innerHTML = `<tr><td colspan="3" class="text-center text-gray-400 italic py-3">No hay usuarios registrados</td></tr>`;
      return;
    }

    tabla.innerHTML = usuarios.map(user => `
      <tr class="border-b border-white/5 hover:bg-white/5 transition" data-usuario="${user.usuario}">
        <td class="px-4 py-2 nombre-usuario">${user.usuario}</td>
        <td class="px-4 py-2 capitalize">${user.rol}</td>
        <td class="px-4 py-2">
          <button onclick="editarUsuario('${user.usuario}')" class="text-emerald-400 hover:text-emerald-300 text-xs font-medium inline-flex items-center gap-1">
            <i data-lucide="edit" class="w-4 h-4"></i> Editar
          </button>
          <button onclick="eliminarUsuario('${user.usuario}')" class="text-red-500 hover:text-red-400 text-xs font-medium inline-flex items-center gap-1 ml-2">
            <i data-lucide="trash-2" class="w-4 h-4"></i> Eliminar
          </button>
        </td>
      </tr>
    `).join("");

    lucide.createIcons();
  } catch {
    tabla.innerHTML = `<tr><td colspan="3" class="text-center text-red-500 italic py-3">Error al cargar usuarios</td></tr>`;
  }
}

/* ==================== ✏️ EDITAR USUARIO ==================== */
function editarUsuario(nombre) {
  document.getElementById("modo").value = "editar";
  document.getElementById("submitLabel").textContent = "Actualizar";
  document.getElementById("usuario").disabled = false;
  document.getElementById("usuario").value = nombre;
  document.getElementById("password").value = "";
  document.getElementById("rol").value = obtenerRolDeFila(nombre);
  document.getElementById("originalUsuario").value = nombre;
  abrirModal();
}

function obtenerRolDeFila(nombre) {
  const fila = document.querySelector(`tr[data-usuario="${nombre}"]`);
  return fila?.querySelector("td:nth-child(2)")?.textContent || "";
}

function actualizarFilaDeTabla(originalNombre, nuevoNombre, nuevoRol) {
  const fila = document.querySelector(`tr[data-usuario="${originalNombre}"]`);
  if (fila) {
    fila.setAttribute("data-usuario", nuevoNombre);
    fila.querySelector(".nombre-usuario").textContent = nuevoNombre;
    fila.querySelector("td:nth-child(2)").textContent = nuevoRol;
    fila.querySelector("button[onclick^='editarUsuario']").setAttribute("onclick", `editarUsuario('${nuevoNombre}')`);
    fila.querySelector("button[onclick^='eliminarUsuario']").setAttribute("onclick", `eliminarUsuario('${nuevoNombre}')`);
    resaltarFila(fila);
  }
}

function resaltarFila(fila) {
  fila.classList.add("bg-emerald-900");
  setTimeout(() => fila.classList.remove("bg-emerald-900"), 2000);
}

/* ==================== 🗑️ ELIMINAR USUARIO ==================== */

/* ==================== 🔁 PAGINACIÓN ==================== */
function iniciarPaginacion() {
  const btnPrev = document.getElementById("prevPagina");
  const btnNext = document.getElementById("nextPagina");
  if (!btnPrev || !btnNext) return;

  let pagina = 1;
  btnPrev.addEventListener("click", () => {
    if (pagina > 1) pagina--;
    document.getElementById("paginaActual").textContent = pagina;
  });

  btnNext.addEventListener("click", () => {
    pagina++;
    document.getElementById("paginaActual").textContent = pagina;
  });
}

/* ==================== 💡 MODAL ==================== */
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

/* ==================== 🔔 TOASTS ==================== */
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