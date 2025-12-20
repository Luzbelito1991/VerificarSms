// Lista completa de usuarios traídos del backend
let usuariosTotales = [];

// Número de página que se está mostrando actualmente
let paginaActual = 1;

// Cantidad de usuarios por página en la tabla
const usuariosPorPagina = 5;

// Si hay una búsqueda activa, acá se guardan esas coincidencias
let coincidenciasActivas = null;

// Flag para evitar lanzar varias búsquedas al mismo tiempo
let busquedaEnProgreso = false;

// Id incremental para descartar respuestas de búsquedas viejas (race condition)
let ultimaBusquedaId = 0;

// Nombre del usuario que tiene la sesión iniciada
let usuarioSesionActual = null;


// Cuando el DOM está listo, se inicializa toda la pantalla
document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 DOM cargado, iniciando aplicación...");

  // Detectar usuario logueado (DOM o API)
  obtenerUsuarioSesion();

  // Preparar búsqueda en el input
  iniciarBusqueda();

  // Preparar formulario (crear/editar usuario)
  iniciarFormulario();

  // Preparar botones de paginación
  iniciarPaginacion();

  // Preparar comportamiento del modal
  iniciarModal();

  // Cargar usuarios desde el backend y dibujarlos en la tabla
  cargarUsuariosEnTabla();

  // Dibujar iconos de Lucide
  lucide.createIcons();
});


/**
 * Obtiene el usuario de la sesión actual.
 * Primero lo busca en el DOM (data-usuario-sesion) y,
 * si no existe, hace un fetch a /usuario-actual.
 */
async function obtenerUsuarioSesion() {
  const elementoUsuario = document.querySelector('[data-usuario-sesion]');
  console.log("🔍 Elemento sesión:", elementoUsuario);
  
  // Caso 1: está en el DOM
  if (elementoUsuario) {
    usuarioSesionActual = elementoUsuario.dataset.usuarioSesion;
    console.log("✅ Usuario sesión actual:", usuarioSesionActual);
    return;
  }

  // Caso 2: intentar pedirlo a una API
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


/**
 * Devuelve el array que se debe usar como fuente:
 * - coincidencias de búsqueda si hay búsqueda activa
 * - sino, la lista completa de usuarios
 */
function obtenerFuenteActual() {
  return coincidenciasActivas || usuariosTotales;
}


/**
 * Escapa texto para prevenir XSS cuando se usa innerHTML
 * (acá lo tengas listo por si lo necesitás).
 */
function escaparHTML(texto) {
  const div = document.createElement('div');
  div.textContent = texto;
  return div.innerHTML;
}


/**
 * Configura el input de búsqueda con debounce y llamadas al backend.
 */
function iniciarBusqueda() {
  const input = document.getElementById("buscarUsuarioTabla");
  if (!input) return;

  let debounceTimeout;

  input.addEventListener("input", () => {
    // Limpiar timeout anterior (debounce)
    clearTimeout(debounceTimeout);

    const filtro = input.value.trim().toLowerCase();

    // Feedback visual: borde en verde cuando hay texto suficiente
    input.classList.toggle("ring-emerald-400", filtro.length >= 2);
    input.classList.toggle("ring-0", filtro.length < 2);

    // Esperar 300ms sin teclear antes de buscar
    debounceTimeout = setTimeout(async () => {
      // Si hay menos de 2 caracteres, se limpia la búsqueda
      if (filtro.length < 2) {
        coincidenciasActivas = null;
        paginaActual = 1;
        renderizarPagina(paginaActual);
        return;
      }

      // Id único para esta búsqueda (evita usar respuestas viejas)
      const busquedaId = ++ultimaBusquedaId;
      busquedaEnProgreso = true;

      try {
        const res = await fetch(`/usuarios?search=${encodeURIComponent(filtro)}`);
        
        // Si llegó una respuesta de una búsqueda anterior, la ignoramos
        if (busquedaId !== ultimaBusquedaId) return;

        if (!res.ok) {
          throw new Error(`Error HTTP: ${res.status}`);
        }

        const data = await res.json();
        coincidenciasActivas = data;
        paginaActual = 1;

        // Cuando hay búsqueda, se muestra sin paginar
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


/**
 * Carga todos los usuarios desde el backend y decide
 * si dibujar con paginación o usando coincidencias activas.
 */
async function cargarUsuariosEnTabla() {
  const tabla = document.getElementById("tablaUsuariosBody");
  if (!tabla) return;

  // Mensaje inicial mientras se carga
  tabla.innerHTML = `<tr><td colspan="3" class="text-center text-gray-400 italic py-3">Cargando usuarios...</td></tr>`;

  try {
    const res = await fetch("/usuarios");
    
    // Si la sesión cambió o no hay permisos
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
    
    // Si no hay búsqueda activa, renderizar con paginación
    if (!coincidenciasActivas) {
      paginaActual = 1;
      renderizarPagina(paginaActual);
    } else {
      // Si hay búsqueda activa, respetarla
      renderizarSinPaginacion();
    }
  } catch (error) {
    console.error("Error al cargar usuarios:", error);
    tabla.innerHTML = `<tr><td colspan="3" class="text-center text-red-500 italic py-3">Error al cargar usuarios</td></tr>`;
    mostrarToast("Error al cargar usuarios del servidor", "error");
  }
}


/**
 * Dibuja una página concreta de la tabla (paginación normal).
 */
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

  // Actualizar número de página visible
  const paginaActualEl = document.getElementById("paginaActual");
  if (paginaActualEl) paginaActualEl.textContent = pagina;

  // Volver a dibujar iconos de Lucide por las nuevas filas
  try { lucide.createIcons(); } catch (e) { console.warn('lucide.createIcons fallo:', e); }
  actualizarBotonesPaginacion();
}


/**
 * Crea y devuelve una fila <tr> del usuario, con sus acciones.
 */
function crearFilaUsuario(user) {
  const fila = document.createElement("tr");
  fila.className = "border-b border-white/5 hover:bg-white/5 transition";
  fila.dataset.usuario = user.usuario;

  // Columna: Usuario
  const tdNombre = document.createElement("td");
  tdNombre.className = "px-4 py-2 nombre-usuario";
  tdNombre.textContent = user.usuario;

  // Columna: Rol
  const tdRol = document.createElement("td");
  tdRol.className = "px-4 py-2 capitalize";
  tdRol.textContent = user.rol;

  // Columna: Acciones
  const tdAcciones = document.createElement("td");
  tdAcciones.className = "px-6 py-3 w-[180px]";

  const divAcciones = document.createElement("div");
  divAcciones.className = "flex justify-center gap-4";

  // Botón Editar
  const btnEditar = document.createElement("button");
  btnEditar.className = "text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center gap-2 px-2 py-1 rounded-md transition";
  btnEditar.innerHTML = '<i data-lucide="edit" class="w-4 h-4"></i><span>Editar</span>';
  btnEditar.addEventListener("click", () => editarUsuario(user.usuario));

  // Botón Eliminar
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


/**
 * Renderiza sin paginación (modo resultados de búsqueda).
 */
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
      // Arrancan transparentes para animación de fade-in
      fila.classList.add("opacity-0");
      fragmento.appendChild(fila);
    });

    tabla.appendChild(fragmento);
  }

  // En modo búsqueda, la paginación no aplica
  const paginaActualEl = document.getElementById("paginaActual");
  if (paginaActualEl) paginaActualEl.textContent = "-";

  setTimeout(() => { try { lucide.createIcons(); } catch(e){console.warn(e);} }, 0);
  actualizarBotonesPaginacion();

  // Animación de aparición
  requestAnimationFrame(() => {
    tabla.querySelectorAll("tr").forEach((tr) => {
      tr.style.transition = "opacity 0.25s ease";
      tr.style.opacity = "1";
    });
  });
}


/**
 * Configura eventos de los botones Anterior / Siguiente.
 */
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
    // Si hay búsqueda, no se permite avanzar página
    if (coincidenciasActivas) return;
    
    const fuente = obtenerFuenteActual();
    const totalPaginas = Math.ceil(fuente.length / usuariosPorPagina);
    if (paginaActual < totalPaginas) {
      paginaActual++;
      renderizarPagina(paginaActual);
    }
  });
}


/**
 * Actualiza estado visual y texto de la paginación
 * (botones deshabilitados y texto "Mostrando usuarios X–Y de Z").
 */
function actualizarBotonesPaginacion() {
  const fuente = obtenerFuenteActual();
  const totalPaginas = Math.ceil(fuente.length / usuariosPorPagina);
  const btnPrev = document.getElementById("prevPagina");
  const btnNext = document.getElementById("nextPagina");
  const infoLabel = document.getElementById("infoPaginacion");

  // Si hay búsqueda, se muestran solo resultados sin paginar
  if (coincidenciasActivas) {
    if (infoLabel) {
      infoLabel.textContent = `${fuente.length} resultado${fuente.length !== 1 ? 's' : ''} encontrado${fuente.length !== 1 ? 's' : ''}`;
    }
    if (btnPrev) { btnPrev.disabled = true; btnPrev.classList.add("opacity-50", "cursor-not-allowed"); }
    if (btnNext) { btnNext.disabled = true; btnNext.classList.add("opacity-50", "cursor-not-allowed"); }
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

  if (btnPrev) {
    btnPrev.disabled = prevDisabled;
    btnPrev.classList.toggle("opacity-50", prevDisabled);
    btnPrev.classList.toggle("cursor-not-allowed", prevDisabled);
  }
  if (btnNext) {
    btnNext.disabled = nextDisabled;
    btnNext.classList.toggle("opacity-50", nextDisabled);
    btnNext.classList.toggle("cursor-not-allowed", nextDisabled);
  }
}


/**
 * Configura comportamiento del formulario para crear/editar usuarios.
 */
function iniciarFormulario() {
  const form = document.getElementById("userForm");
  if (!form) return;

  // Flag para evitar doble envío
  let enviando = false;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("📝 Formulario enviado");
    
    if (enviando) {
      console.log("⚠️ Ya hay un envío en progreso");
      return;
    }

    // Validación básica de campos
    if (!validarCampos()) {
      mostrarToast("Completá todos los campos requeridos", "error");
      return;
    }

    enviando = true;
    const submitBtn = form.querySelector('button[type="submit"]');
    const textoOriginal = submitBtn?.textContent;
    if (submitBtn) submitBtn.textContent = "Procesando...";

    // Captura de elementos
    const modoEl = document.getElementById("modo");
    const usuarioEl = document.getElementById("usuario");
    const passwordEl = document.getElementById("password");
    const rolEl = document.getElementById("rol");
    const originalEl = document.getElementById("originalUsuario");

    // Valores normalizados
    const modo = modoEl?.value || "crear";
    const nombre = usuarioEl?.value.trim() || "";
    const password = passwordEl?.value || "";
    const rol = rolEl?.value || "";
    const original = originalEl?.value || "";

    console.log("📊 Datos del formulario:", { modo, nombre, rol, original });

    // Si se edita el nombre, verificar que no exista otro igual
    if (modo === "editar" && nombre !== original) {
      const existe = usuariosTotales.some(
        (u) => u.usuario.toLowerCase() === nombre.toLowerCase()
      );
      if (existe) {
        mostrarToast(`Ya existe un usuario llamado "${nombre}"`, "error");
        if (usuarioEl) usuarioEl.classList.add("border-red-500", "ring-red-500");
        enviando = false;
        if (submitBtn) submitBtn.textContent = textoOriginal;
        return;
      }
    }

    // Payloads separados para crear y editar
    const payloadCrear = JSON.stringify({ usuario: nombre, password, rol });
    const payloadEditar = JSON.stringify({ nuevo_usuario: nombre, password, rol });

    try {
      let res;
      
      if (modo === "crear") {
        // Alta de usuario
        res = await fetch("/crear-usuario", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: payloadCrear,
        });
      } else {
        // Edición de usuario existente
        const url = `/editar-usuario/${encodeURIComponent(original)}`;
        res = await fetch(url, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: payloadEditar,
        });
      }

      console.log("📡 Response status:", res.status);

      // Intentar parsear JSON de respuesta
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
        
        // Flag que indica si el usuario editado es el que está logueado
        const editoPropio = data?.editando_propio_usuario || false;
        console.log("🔍 ¿Editó su propio usuario?", editoPropio);
        
        // Toast de éxito
        if (editoPropio && nombre !== original) {
          console.log("🎯 Mostrando toast para edición propia");
          mostrarToast("Usuario actualizado. Tu nombre de sesión cambió correctamente", "success");
        } else {
          const mensajeBase = modo === "crear" ? "Usuario creado exitosamente" : "Usuario actualizado exitosamente";
          console.log("🎯 Mostrando toast:", mensajeBase);
          mostrarToast(mensajeBase, "success");
        }
        
        // Cerrar modal y limpiar formulario
        console.log("🚪 Cerrando modal...");
        reiniciarFormulario();
        cerrarModal();
        
        // Volver a cargar la tabla
        console.log("🔄 Recargando tabla...");
        await cargarUsuariosEnTabla();
        
        // Actualizar nombre en sidebar si editó su propio usuario
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
              // Se podría anteponer "👋 " si se quiere mantener el saludo
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
        // Manejo de distintos códigos de error HTTP
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
      // Errores de red u otros no controlados
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
      // Restaurar botón y flag
      enviando = false;
      if (submitBtn) submitBtn.textContent = textoOriginal;
    }
  });
}


/**
 * Validación básica de campos del formulario.
 */
function validarCampos() {
  const usuario = document.getElementById("usuario");
  const password = document.getElementById("password");
  const rol = document.getElementById("rol");
  const modoEl = document.getElementById("modo");
  const modo = modoEl?.value || "crear";
  let valido = true;

  // Usuario obligatorio
  if (!usuario || !usuario.value.trim()) {
    if (usuario) usuario.classList.add("border-red-500", "ring-red-500");
    valido = false;
  } else {
    usuario.classList.remove("border-red-500", "ring-red-500");
  }

  // Password obligatorio solo al crear
  if (modo === "crear" && (!password || !password.value)) {
    if (password) password.classList.add("border-red-500", "ring-red-500");
    valido = false;
  } else if (password) {
    password.classList.remove("border-red-500", "ring-red-500");
  }

  // Rol obligatorio
  if (!rol || !rol.value) {
    if (rol) rol.classList.add("border-red-500", "ring-red-500");
    valido = false;
  } else if (rol) {
    rol.classList.remove("border-red-500", "ring-red-500");
  }

  return valido;
}


/**
 * Pone el formulario en modo "Crear" y limpia todos los campos/estilos.
 */
function reiniciarFormulario() {
  const modoEl = document.getElementById("modo");
  const submitLabelEl = document.getElementById("submitLabel");
  const usuarioEl = document.getElementById("usuario");
  const passwordEl = document.getElementById("password");
  const rolEl = document.getElementById("rol");
  const originalUsuarioEl = document.getElementById("originalUsuario");

  if (modoEl) modoEl.value = "crear";
  if (submitLabelEl) submitLabelEl.textContent = "Crear";
  if (usuarioEl) {
    usuarioEl.disabled = false;
    usuarioEl.value = "";
  }
  if (passwordEl) {
    passwordEl.value = "";
    passwordEl.placeholder = "";
  }
  if (rolEl) rolEl.value = "";
  if (originalUsuarioEl) originalUsuarioEl.value = "";
  
  // Quitar marcas de error en los campos
  ["usuario", "password", "rol"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.remove("border-red-500", "ring-red-500");
  });
}


/**
 * Rellena el formulario con los datos de un usuario para editarlo.
 */
async function editarUsuario(nombre) {
  const modoEl = document.getElementById("modo");
  const submitLabelEl = document.getElementById("submitLabel");
  const usuarioEl = document.getElementById("usuario");
  const passwordEl = document.getElementById("password");
  const rolEl = document.getElementById("rol");

  if (modoEl) modoEl.value = "editar";
  if (submitLabelEl) submitLabelEl.textContent = "Actualizar";
  if (usuarioEl) {
    usuarioEl.disabled = false;
    usuarioEl.value = nombre;
  }
  if (passwordEl) passwordEl.value = "";
  if (passwordEl) passwordEl.placeholder = "Dejar vacío para mantener actual";

  try {
    // Obtener datos detallados del usuario
    const res = await fetch(`/usuario-detalle/${encodeURIComponent(nombre)}`);
    
    if (!res.ok) {
      throw new Error(`Error HTTP: ${res.status}`);
    }
    
    const data = await res.json();
    
    if (data.usuario) {
      if (rolEl) rolEl.value = data.rol || "";
    } else {
      mostrarToast("No se pudo cargar el rol del usuario", "warning");
      if (rolEl) rolEl.value = "";
    }
  } catch (error) {
    console.error("Error al cargar rol:", error);
    mostrarToast("Error al obtener datos del usuario", "error");
    if (rolEl) rolEl.value = "";
  }

  // Guardar usuario original para saber si cambió el nombre
  if (document.getElementById("originalUsuario")) document.getElementById("originalUsuario").value = nombre;
  abrirModal();
}


/**
 * Elimina un usuario, previniendo que se elimine la propia cuenta activa.
 */
async function eliminarUsuario(nombre) {
  // Protección: no permitir eliminar el usuario de la sesión actual
  if (usuarioSesionActual && nombre.toLowerCase() === usuarioSesionActual.toLowerCase()) {
    mostrarToast("No podés eliminar tu propio usuario mientras tenés la sesión activa", "error");
    return;
  }

  // Confirmación básica del navegador
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


/**
 * Inicializa eventos del modal (abrir/cerrar con botón, click fuera, Escape).
 */
function iniciarModal() {
  const btnMostrar = document.getElementById("mostrarFormularioBtn");
  const modal = document.getElementById("modalUsuario");
  
  if (!btnMostrar || !modal) return;

  // Botón "Nuevo usuario"
  btnMostrar.addEventListener("click", () => {
    reiniciarFormulario();
    abrirModal();
  });

  // Cerrar al hacer click fuera del contenido
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      cerrarModal();
    }
  });

  // Cerrar con tecla Escape
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
      cerrarModal();
    }
  });
}


/**
 * Muestra el modal y bloquea el scroll de fondo.
 */
function abrirModal() {
  const modal = document.getElementById("modalUsuario");
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";
  
  // Foco al input usuario
  setTimeout(() => {
    document.getElementById("usuario")?.focus();
  }, 100);
}


/**
 * Oculta el modal, restaura el scroll y limpia el formulario.
 */
function cerrarModal() {
  const modal = document.getElementById("modalUsuario");
  if (!modal) return;
  modal.classList.remove("flex");
  modal.classList.add("hidden");
  document.body.style.overflow = "";
  reiniciarFormulario();
}


/**
 * Muestra un toast flotante en la parte superior derecha.
 */
function mostrarToast(mensaje, tipo = "info") {
  console.log(`🍞 mostrarToast llamado: "${mensaje}" (${tipo})`);
  
  const container = document.getElementById("toastContainer");
  console.log("🔍 Toast container:", container);
  
  if (!container) {
    console.error("❌ ERROR: Toast container no encontrado!");
    alert(mensaje); // Fallback para ver el mensaje
    return;
  }

  // Colores por tipo
  const colores = {
    success: "bg-emerald-600",
    error: "bg-red-600",
    info: "bg-blue-600",
    warning: "bg-yellow-500",
  };

  // Iconos por tipo
  const iconos = {
    success: "✓",
    error: "✕",
    info: "ℹ",
    warning: "⚠",
  };

  // Contenedor del toast
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

  // Animación de salida y eliminación
  setTimeout(() => {
    toast.classList.add("opacity-0", "scale-95");
    setTimeout(() => {
      toast.remove();
      console.log("🗑️ Toast removido");
    }, 300);
  }, 3000);
}
