let usuariosTotales = [];
let paginaActual = 1;
const usuariosPorPagina = 5;
let coincidenciasActivas = null;
let busquedaEnProgreso = false;
let ultimaBusquedaId = 0;
let usuarioSesionActual = null;

document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 DOM cargado, iniciando aplicación...");
  obtenerUsuarioSesion();
  iniciarBusqueda();
  iniciarFormulario();
  iniciarPaginacion();
  iniciarModal();
  cargarUsuariosEnTabla();
  lucide.createIcons();
});

async function obtenerUsuarioSesion() {
  const elementoUsuario = document.querySelector('[data-usuario-sesion]');
  console.log("🔍 Elemento sesión:", elementoUsuario);
  
  if (elementoUsuario) {
    usuarioSesionActual = elementoUsuario.dataset.usuarioSesion;
    console.log("✅ Usuario sesión actual:", usuarioSesionActual);
    return;
  }

  try {
    const res = await fetch('/usuario-actual');
    if (res.ok) {
      const data = await res.json();
      usuarioSesionActual = data.usuario;
      console.log("✅ Usuario desde API:", usuarioSesionActual);
    }
  } catch (error) {
    console.log('⚠️ No se pudo obtener usuario de sesión');
  }
}

function obtenerFuenteActual() {
  return coincidenciasActivas || usuariosTotales;
}

function escaparHTML(texto) {
  const div = document.createElement('div');
  div.textContent = texto;
  return div.innerHTML;
}

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

      const busquedaId = ++ultimaBusquedaId;
      busquedaEnProgreso = true;

      try {
        const res = await fetch(`/usuarios?search=${encodeURIComponent(filtro)}`);
        
        if (busquedaId !== ultimaBusquedaId) return;

        if (!res.ok) {
          throw new Error(`Error HTTP: ${res.status}`);
        }

        const data = await res.json();
        coincidenciasActivas = data;
        paginaActual = 1;
        renderizarSinPaginacion();
      } catch (error) {
        console.error("Error en búsqueda:", error);
        mostrarToast("Error al buscar usuarios", "error");
      } finally {
        busquedaEnProgreso = false;
      }
    }, 300);
  });
}

async function cargarUsuariosEnTabla() {
  const tabla = document.getElementById("tablaUsuariosBody");
  if (!tabla) return;

  tabla.innerHTML = `<tr><td colspan="3" class="text-center text-gray-400 italic py-3">Cargando usuarios...</td></tr>`;

  try {
    const res = await fetch("/usuarios");
    
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        tabla.innerHTML = `<tr><td colspan="3" class="text-center text-yellow-500 italic py-3">
          Tu sesión se actualizó. <a href="/logout" class="underline hover:text-yellow-300">Volvé a iniciar sesión</a>
        </td></tr>`;
        mostrarToast("Tu usuario cambió. Por favor, volvé a iniciar sesión", "warning");
        return;
      }
      throw new Error(`Error HTTP: ${res.status}`);
    }

    const data = await res.json();
    usuariosTotales = data;
    
    if (!coincidenciasActivas) {
      paginaActual = 1;
      renderizarPagina(paginaActual);
    } else {
      renderizarSinPaginacion();
    }
  } catch (error) {
    console.error("Error al cargar usuarios:", error);
    tabla.innerHTML = `<tr><td colspan="3" class="text-center text-red-500 italic py-3">Error al cargar usuarios</td></tr>`;
    mostrarToast("Error al cargar usuarios del servidor", "error");
  }
}

function renderizarPagina(pagina) {
  const tabla = document.getElementById("tablaUsuariosBody");
  if (!tabla) return;

  const fuente = obtenerFuenteActual();
  const inicio = (pagina - 1) * usuariosPorPagina;
  const fin = inicio + usuariosPorPagina;
  const usuariosPagina = fuente.slice(inicio, fin);

  if (!usuariosPagina.length) {
    tabla.innerHTML = `<tr><td colspan="3" class="text-center text-gray-400 italic py-3">No hay usuarios registrados</td></tr>`;
  } else {
    const fragmento = document.createDocumentFragment();
    
    usuariosPagina.forEach((user) => {
      const fila = crearFilaUsuario(user);
      fragmento.appendChild(fila);
    });
    
    tabla.innerHTML = '';
    tabla.appendChild(fragmento);
  }

  document.getElementById("paginaActual").textContent = pagina;
  lucide.createIcons();
  actualizarBotonesPaginacion();
}

function crearFilaUsuario(user) {
  const fila = document.createElement("tr");
  fila.className = "border-b border-white/5 hover:bg-white/5 transition";
  fila.dataset.usuario = user.usuario;

  const tdNombre = document.createElement("td");
  tdNombre.className = "px-4 py-2 nombre-usuario";
  tdNombre.textContent = user.usuario;

  const tdRol = document.createElement("td");
  tdRol.className = "px-4 py-2 capitalize";
  tdRol.textContent = user.rol;

  const tdAcciones = document.createElement("td");
  tdAcciones.className = "px-6 py-3 w-[180px]";

  const divAcciones = document.createElement("div");
  divAcciones.className = "flex justify-center gap-4";

  const btnEditar = document.createElement("button");
  btnEditar.className = "text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center gap-2 px-2 py-1 rounded-md transition";
  btnEditar.innerHTML = '<i data-lucide="edit" class="w-4 h-4"></i><span>Editar</span>';
  btnEditar.addEventListener("click", () => editarUsuario(user.usuario));

  const btnEliminar = document.createElement("button");
  btnEliminar.className = "text-red-500 hover:text-red-400 text-sm font-medium flex items-center gap-2 px-2 py-1 rounded-md transition";
  btnEliminar.innerHTML = '<i data-lucide="trash-2" class="w-4 h-4"></i><span>Eliminar</span>';
  btnEliminar.addEventListener("click", () => eliminarUsuario(user.usuario));

  divAcciones.appendChild(btnEditar);
  divAcciones.appendChild(btnEliminar);
  tdAcciones.appendChild(divAcciones);

  fila.appendChild(tdNombre);
  fila.appendChild(tdRol);
  fila.appendChild(tdAcciones);

  return fila;
}

function renderizarSinPaginacion() {
  const tabla = document.getElementById("tablaUsuariosBody");
  if (!tabla) return;

  const fuente = obtenerFuenteActual();
  tabla.innerHTML = "";

  if (!fuente.length) {
    tabla.innerHTML = `<tr><td colspan="3" class="text-center text-gray-400 italic py-3">No hay coincidencias</td></tr>`;
  } else {
    const fragmento = document.createDocumentFragment();

    fuente.forEach((user) => {
      const fila = crearFilaUsuario(user);
      fila.classList.add("opacity-0");
      fragmento.appendChild(fila);
    });

    tabla.appendChild(fragmento);
  }

  document.getElementById("paginaActual").textContent = "-";
  setTimeout(() => lucide.createIcons(), 0);
  actualizarBotonesPaginacion();

  requestAnimationFrame(() => {
    tabla.querySelectorAll("tr").forEach((tr) => {
      tr.style.transition = "opacity 0.25s ease";
      tr.style.opacity = "1";
    });
  });
}

function iniciarPaginacion() {
  const btnPrev = document.getElementById("prevPagina");
  const btnNext = document.getElementById("nextPagina");
  if (!btnPrev || !btnNext) return;

  btnPrev.addEventListener("click", () => {
    if (paginaActual > 1 && !coincidenciasActivas) {
      paginaActual--;
      renderizarPagina(paginaActual);
    }
  });

  btnNext.addEventListener("click", () => {
    if (coincidenciasActivas) return;
    
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

  if (coincidenciasActivas) {
    if (infoLabel) {
      infoLabel.textContent = `${fuente.length} resultado${fuente.length !== 1 ? 's' : ''} encontrado${fuente.length !== 1 ? 's' : ''}`;
    }
    btnPrev.disabled = true;
    btnNext.disabled = true;
    btnPrev.classList.add("opacity-50", "cursor-not-allowed");
    btnNext.classList.add("opacity-50", "cursor-not-allowed");
    return;
  }

  const inicio = fuente.length > 0 ? (paginaActual - 1) * usuariosPorPagina + 1 : 0;
  const fin = Math.min(inicio + usuariosPorPagina - 1, fuente.length);

  if (infoLabel) {
    infoLabel.textContent = fuente.length > 0 
      ? `Mostrando usuarios ${inicio}–${fin} de ${fuente.length}`
      : 'No hay usuarios';
  }

  const prevDisabled = paginaActual === 1;
  const nextDisabled = paginaActual >= totalPaginas || fuente.length === 0;

  btnPrev.disabled = prevDisabled;
  btnNext.disabled = nextDisabled;

  btnPrev.classList.toggle("opacity-50", prevDisabled);
  btnPrev.classList.toggle("cursor-not-allowed", prevDisabled);
  btnNext.classList.toggle("opacity-50", nextDisabled);
  btnNext.classList.toggle("cursor-not-allowed", nextDisabled);
}

function iniciarFormulario() {
  const form = document.getElementById("userForm");
  if (!form) return;

  let enviando = false;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("📝 Formulario enviado");
    
    if (enviando) {
      console.log("⚠️ Ya hay un envío en progreso");
      return;
    }

    if (!validarCampos()) {
      mostrarToast("Completá todos los campos requeridos", "error");
      return;
    }

    enviando = true;
    const submitBtn = form.querySelector('button[type="submit"]');
    const textoOriginal = submitBtn?.textContent;
    if (submitBtn) submitBtn.textContent = "Procesando...";

    const modo = document.getElementById("modo").value;
    const nombre = document.getElementById("usuario").value.trim();
    const password = document.getElementById("password").value;
    const rol = document.getElementById("rol").value;
    const original = document.getElementById("originalUsuario").value;

    console.log("📊 Datos del formulario:", { modo, nombre, rol, original });

    if (modo === "editar" && nombre !== original) {
      const existe = usuariosTotales.some(
        (u) => u.usuario.toLowerCase() === nombre.toLowerCase()
      );
      if (existe) {
        mostrarToast(`Ya existe un usuario llamado "${nombre}"`, "error");
        document.getElementById("usuario").classList.add("border-red-500", "ring-red-500");
        enviando = false;
        if (submitBtn) submitBtn.textContent = textoOriginal;
        return;
      }
    }

    const payloadCrear = JSON.stringify({ usuario: nombre, password, rol });
    const payloadEditar = JSON.stringify({ nuevo_usuario: nombre, password, rol });

    try {
      let res;
      
      if (modo === "crear") {
        res = await fetch("/crear-usuario", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: payloadCrear,
        });
      } else {
        const url = `/editar-usuario/${encodeURIComponent(original)}`;
        res = await fetch(url, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: payloadEditar,
        });
      }

      console.log("📡 Response status:", res.status);

      let data;
      const contentType = res.headers.get("content-type");
      
      if (contentType && contentType.includes("application/json")) {
        data = await res.json();
        console.log("📦 Response data:", data);
      } else {
        console.error("❌ Respuesta no es JSON");
        data = {};
      }

      if (res.ok) {
        console.log("✅ Respuesta exitosa del servidor");
        
        const editoPropio = data?.editando_propio_usuario || false;
        console.log("🔍 ¿Editó su propio usuario?", editoPropio);
        
        // MOSTRAR TOAST PRIMERO
        if (editoPropio && nombre !== original) {
          console.log("🎯 Mostrando toast para edición propia");
          mostrarToast("Usuario actualizado. Tu nombre de sesión cambió correctamente", "success");
        } else {
          const mensajeBase = modo === "crear" ? "Usuario creado exitosamente" : "Usuario actualizado exitosamente";
          console.log("🎯 Mostrando toast:", mensajeBase);
          mostrarToast(mensajeBase, "success");
        }
        
        // CERRAR MODAL
        console.log("🚪 Cerrando modal...");
        reiniciarFormulario();
        cerrarModal();
        
        // RECARGAR TABLA
        console.log("🔄 Recargando tabla...");
        await cargarUsuariosEnTabla();
        
        // ACTUALIZAR SIDEBAR (si corresponde)
        if (editoPropio && nombre !== original) {
          console.log("🎨 Actualizando sidebar...");
          
          const elementoUsuario = document.querySelector('[data-usuario-sesion]');
          console.log("🔍 Elemento data-usuario-sesion:", elementoUsuario);
          
          if (elementoUsuario) {
            elementoUsuario.dataset.usuarioSesion = nombre;
            usuarioSesionActual = nombre;
            console.log("✅ Actualizado data-usuario-sesion");
          }
          
          try {
            const nombreSidebar = document.getElementById('nombreUsuarioSidebar');
            console.log("🔍 Elemento nombreUsuarioSidebar:", nombreSidebar);
            
            if (nombreSidebar) {
              nombreSidebar.textContent = nombre;
              console.log("✅ Actualizado nombreUsuarioSidebar");
            } else {
              console.warn("⚠️ No se encontró nombreUsuarioSidebar");
            }
          } catch (sidebarError) {
            console.error("❌ Error al actualizar sidebar:", sidebarError);
          }
        }
        
        console.log("✅ Proceso completado exitosamente");
      } else {
        let errorMsg = "Error al procesar usuario";
        
        if (res.status === 400) errorMsg = "Datos inválidos";
        else if (res.status === 404) errorMsg = "Usuario no encontrado";
        else if (res.status === 409) errorMsg = "El usuario ya existe";
        else if (res.status === 500) errorMsg = "Error del servidor";
        
        if (data?.detail) errorMsg = data.detail;
        else if (data?.mensaje) errorMsg = data.mensaje;
        
        mostrarToast(errorMsg, "error");
      }
    } catch (err) {
      console.error("❌ Error completo:", err);
      console.error("Stack trace:", err.stack);
      
      let mensajeError = "Error de conexión con el servidor";
      
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        mensajeError = "No se pudo conectar al servidor. Verificá tu conexión.";
      } else if (err.message) {
        mensajeError = `Error: ${err.message}`;
      }
      
      mostrarToast(mensajeError, "error");
    } finally {
      enviando = false;
      if (submitBtn) submitBtn.textContent = textoOriginal;
    }
  });
}

function validarCampos() {
  const usuario = document.getElementById("usuario");
  const password = document.getElementById("password");
  const rol = document.getElementById("rol");
  const modo = document.getElementById("modo").value;
  let valido = true;

  if (!usuario.value.trim()) {
    usuario.classList.add("border-red-500", "ring-red-500");
    valido = false;
  } else {
    usuario.classList.remove("border-red-500", "ring-red-500");
  }

  if (modo === "crear" && !password.value) {
    password.classList.add("border-red-500", "ring-red-500");
    valido = false;
  } else {
    password.classList.remove("border-red-500", "ring-red-500");
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
  document.getElementById("password").placeholder = "";
  document.getElementById("rol").value = "";
  document.getElementById("originalUsuario").value = "";
  
  ["usuario", "password", "rol"].forEach(id => {
    document.getElementById(id)?.classList.remove("border-red-500", "ring-red-500");
  });
}

async function editarUsuario(nombre) {
  document.getElementById("modo").value = "editar";
  document.getElementById("submitLabel").textContent = "Actualizar";
  document.getElementById("usuario").disabled = false;
  document.getElementById("usuario").value = nombre;
  document.getElementById("password").value = "";
  document.getElementById("password").placeholder = "Dejar vacío para mantener actual";

  try {
    const res = await fetch(`/usuario-detalle/${encodeURIComponent(nombre)}`);
    
    if (!res.ok) {
      throw new Error(`Error HTTP: ${res.status}`);
    }
    
    const data = await res.json();
    
    if (data.usuario) {
      document.getElementById("rol").value = data.rol || "";
    } else {
      mostrarToast("No se pudo cargar el rol del usuario", "warning");
      document.getElementById("rol").value = "";
    }
  } catch (error) {
    console.error("Error al cargar rol:", error);
    mostrarToast("Error al obtener datos del usuario", "error");
    document.getElementById("rol").value = "";
  }

  document.getElementById("originalUsuario").value = nombre;
  abrirModal();
}

async function eliminarUsuario(nombre) {
  if (usuarioSesionActual && nombre.toLowerCase() === usuarioSesionActual.toLowerCase()) {
    mostrarToast("No podés eliminar tu propio usuario mientras tenés la sesión activa", "error");
    return;
  }

  const confirmado = confirm(
    `¿Estás seguro de eliminar al usuario "${nombre}"?\n\nEsta acción no se puede deshacer.`
  );
  if (!confirmado) return;

  try {
    const res = await fetch(
      `/eliminar-usuario/${encodeURIComponent(nombre)}`,
      { method: "DELETE" }
    );
    
    let data;
    try {
      data = await res.json();
    } catch {
      data = {};
    }

    if (res.ok && data.ok) {
      mostrarToast(`Usuario "${nombre}" eliminado exitosamente`, "success");
      await cargarUsuariosEnTabla();
    } else {
      let errorMsg = `No se pudo eliminar el usuario "${nombre}"`;
      
      if (res.status === 404) errorMsg = "Usuario no encontrado";
      else if (res.status === 403) errorMsg = "No tenés permisos para eliminar este usuario";
      else if (data?.detail) errorMsg = data.detail;
      
      mostrarToast(errorMsg, "error");
    }
  } catch (error) {
    console.error("Error eliminando usuario:", error);
    mostrarToast("Error de conexión al intentar eliminar el usuario", "error");
  }
}

function iniciarModal() {
  const btnMostrar = document.getElementById("mostrarFormularioBtn");
  const modal = document.getElementById("modalUsuario");
  
  if (!btnMostrar || !modal) return;

  btnMostrar.addEventListener("click", () => {
    reiniciarFormulario();
    abrirModal();
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      cerrarModal();
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
      cerrarModal();
    }
  });
}

function abrirModal() {
  const modal = document.getElementById("modalUsuario");
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";
  
  setTimeout(() => {
    document.getElementById("usuario")?.focus();
  }, 100);
}

function cerrarModal() {
  const modal = document.getElementById("modalUsuario");
  if (!modal) return;
  modal.classList.remove("flex");
  modal.classList.add("hidden");
  document.body.style.overflow = "";
  reiniciarFormulario();
}

function mostrarToast(mensaje, tipo = "info") {
  console.log(`🍞 mostrarToast llamado: "${mensaje}" (${tipo})`);
  
  const container = document.getElementById("toastContainer");
  console.log("🔍 Toast container:", container);
  
  if (!container) {
    console.error("❌ ERROR: Toast container no encontrado!");
    alert(mensaje); // Fallback para ver el mensaje
    return;
  }

  const colores = {
    success: "bg-emerald-600",
    error: "bg-red-600",
    info: "bg-blue-600",
    warning: "bg-yellow-500",
  };

  const iconos = {
    success: "✓",
    error: "✕",
    info: "ℹ",
    warning: "⚠",
  };

  const toast = document.createElement("div");
  toast.className = `${
    colores[tipo] || colores.info
  } text-white text-sm font-medium rounded-md px-4 py-2 shadow-lg animate-fade-in-down transition duration-300 pointer-events-auto flex items-center gap-2`;
  
  const icono = document.createElement("span");
  icono.textContent = iconos[tipo] || iconos.info;
  icono.className = "font-bold text-base";
  
  const texto = document.createElement("span");
  texto.textContent = mensaje;
  
  toast.appendChild(icono);
  toast.appendChild(texto);

  container.appendChild(toast);
  console.log("✅ Toast agregado al DOM");

  setTimeout(() => {
    toast.classList.add("opacity-0", "scale-95");
    setTimeout(() => {
      toast.remove();
      console.log("🗑️ Toast removido");
    }, 300);
  }, 3000);
}