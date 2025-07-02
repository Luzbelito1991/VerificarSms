// 🔁 Esperamos a que todo el DOM esté cargado antes de ejecutar lógica
document.addEventListener("DOMContentLoaded", () => {
  // 🔗 Obtenemos referencias a los elementos del formulario
  const userForm = document.getElementById("userForm");
  const usuario = document.getElementById("usuario");
  const password = document.getElementById("password");
  const rol = document.getElementById("rol");
  const msg = document.getElementById("msg");
  const submitLabel = document.getElementById("submitLabel");

  // 🌍 URL base del backend
  const API = "http://localhost:8000";

  // ⚙️ Variables internas para controlar si estamos editando
  let modoEditar = false;
  let usuarioActual = "";

  // 💬 Función para mostrar mensajes en pantalla con distintos colores
  function mostrarMensaje(texto, tipo = "info") {
    const colores = {
      info: "text-gray-300",
      success: "text-green-400",
      error: "text-red-400",
      warning: "text-yellow-400"
    };
    msg.textContent = texto;
    msg.className = `${colores[tipo] || "text-gray-300"} text-sm mt-2 text-center`;
  }

  // 🔍 Buscar un usuario por su nombre (desde input de búsqueda)
  window.buscarUsuario = async function () {
    const nombre = document.getElementById("buscar").value.trim();
    if (!nombre) return;

    try {
      // Llamamos al backend para obtener todos los usuarios
      const res = await fetch(`${API}/usuarios`);
      const usuarios = await res.json();

      // Buscamos al usuario ingresado por nombre
      const encontrado = usuarios.find(u => u.usuario === nombre);

      if (encontrado) {
        // Si se encuentra, activamos modo edición y llenamos el formulario
        modoEditar = true;
        usuarioActual = encontrado.usuario;
        usuario.value = encontrado.usuario;
        usuario.disabled = true;
        rol.value = encontrado.rol;
        password.placeholder = "Nueva contraseña (opcional)";
        submitLabel.textContent = "Guardar cambios";
        mostrarMensaje(`✏️ Editando usuario: ${encontrado.usuario}`, "warning");
        usuario.focus();
      } else {
        mostrarMensaje("❌ Usuario no encontrado", "error");
      }
    } catch {
      mostrarMensaje("❌ Error al buscar usuario", "error");
    }
  };

  // 💾 Evento para crear o editar usuario al enviar el formulario
  userForm.addEventListener("submit", async (e) => {
    e.preventDefault(); // Evitamos comportamiento por defecto

    // Obtenemos los datos del formulario
    const data = {
      usuario: usuario.value.trim(),
      password: password.value.trim(),
      rol: rol.value
    };

    // Validamos campos requeridos
    if (!data.usuario || !data.rol || (!modoEditar && !data.password)) {
      mostrarMensaje("Completá todos los campos obligatorios", "error");
      return;
    }

    // Elegimos URL y método según si creamos o editamos
    const url = modoEditar
      ? `${API}/editar-usuario/${usuarioActual}`
      : `${API}/crear-usuario`;
    const method = modoEditar ? "PUT" : "POST";

    // Desactivamos botón para evitar doble envío
    const boton = submitLabel.closest("button");
    boton.disabled = true;

    try {
      // Enviamos los datos al backend
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      const resultado = await res.json();

      if (res.ok) {
        // Si todo sale bien, mostramos mensaje y recargamos lista
        mostrarMensaje("✅ " + resultado.mensaje, "success");
        reiniciarFormulario();
        cargarUsuariosEnTabla();
      } else {
        // Si hay error, lo mostramos
        mostrarMensaje("❌ " + (resultado.detail || resultado.mensaje || "Error"), "error");
      }
    } catch {
      mostrarMensaje("❌ Error de red", "error");
    } finally {
      // Rehabilitamos el botón
      boton.disabled = false;
    }
  });

  // 🗑️ Eliminar al usuario actualmente cargado
  window.eliminarUsuarioManual = async function () {
    if (!usuarioActual) {
      mostrarMensaje("Buscá un usuario primero para eliminarlo", "warning");
      return;
    }

    // Confirmación antes de eliminar
    if (!confirm(`¿Eliminar al usuario "${usuarioActual}"?`)) return;

    try {
      const res = await fetch(`${API}/eliminar-usuario/${usuarioActual}`, {
        method: "DELETE"
      });

      const data = await res.json();
      mostrarMensaje("🗑️ " + data.mensaje, "success");
      reiniciarFormulario();
      cargarUsuariosEnTabla();
    } catch {
      mostrarMensaje("❌ Error al eliminar usuario", "error");
    }
  };

  // 🔄 Restaurar el formulario a su estado inicial
  window.reiniciarFormulario = function () {
    modoEditar = false;
    usuarioActual = "";
    userForm.reset();
    usuario.disabled = false;
    password.placeholder = "";
    submitLabel.textContent = "Crear usuario";
    msg.textContent = "";
    usuario.focus();
  };

  // 🖊️ Función que se llama desde la tabla para cargar un usuario directo
  window.editarDesdeTabla = async function (nombre) {
    document.getElementById("buscar").value = nombre;
    await buscarUsuario(); // Usamos la misma función de búsqueda
  };

  // 📊 Cargar usuarios y mostrarlos en tabla
  async function cargarUsuariosEnTabla() {
    const tabla = document.getElementById("tablaUsuariosBody");
    tabla.innerHTML = `<tr><td class="px-4 py-2 text-gray-400 italic" colspan="3">Cargando usuarios...</td></tr>`;

    try {
      const res = await fetch(`${API}/usuarios`);
      const usuarios = await res.json();

      if (!usuarios.length) {
        tabla.innerHTML = `<tr><td class="px-4 py-2 text-gray-400 italic" colspan="3">No hay usuarios registrados</td></tr>`;
        return;
      }

      // Construimos filas de tabla dinámicamente
      tabla.innerHTML = usuarios.map(user => `
        <tr class="border-b border-white/5 hover:bg-white/5 transition">
          <td class="px-4 py-2">${user.usuario}</td>
          <td class="px-4 py-2 capitalize">${user.rol}</td>
          <td class="px-4 py-2">
            <button onclick="editarDesdeTabla('${user.usuario}')" 
                    class="text-emerald-400 hover:text-emerald-300 text-xs font-medium transition inline-flex items-center gap-1">
              <i data-lucide="edit" class="w-4 h-4"></i> Editar
            </button>
          </td>
        </tr>
      `).join("");

      // Renderizamos íconos SVG
      lucide.createIcons();
    } catch {
      tabla.innerHTML = `<tr><td class="px-4 py-2 text-red-500 italic" colspan="3">Error al cargar usuarios</td></tr>`;
    }
  }

  // 🚀 Al cargar la página, mostramos la tabla y damos foco inicial
  cargarUsuariosEnTabla();
  usuario.focus();
});