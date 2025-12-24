/**
 * 🎨 Sistema de Modales Glassmorphism
 * Reemplaza los toasts por modales visuales elegantes
 */

// Variable para almacenar el callback del modal de confirmación
let modalConfirmCallback = null;

/**
 * Muestra un modal con mensaje (reemplaza mostrarToast)
 * @param {string} mensaje - Texto a mostrar
 * @param {string} tipo - Tipo: 'success', 'error', 'warning', 'info'
 * @param {number} duracion - Tiempo en ms antes de auto-cerrar (0 = no auto-cerrar)
 */
function mostrarModal(mensaje, tipo = 'info', duracion = 0) {
  // Asegurar que mensaje sea siempre un string
  if (typeof mensaje !== 'string') {
    if (mensaje && typeof mensaje === 'object') {
      // Si es un objeto con message, usar eso
      if (mensaje.message) mensaje = mensaje.message;
      else if (mensaje.detail) mensaje = mensaje.detail;
      else if (mensaje.mensaje) mensaje = mensaje.mensaje;
      else mensaje = JSON.stringify(mensaje);
    } else {
      mensaje = String(mensaje);
    }
  }
  
  const modal = crearModalMensaje(mensaje, tipo);
  document.body.appendChild(modal);
  
  // Mostrar con animación
  requestAnimationFrame(() => {
    modal.classList.remove('hidden');
    lucide.createIcons();
  });

  // Auto-cerrar si duracion > 0
  if (duracion > 0) {
    setTimeout(() => cerrarModalMensaje(modal), duracion);
  }

  return modal;
}

/**
 * Crea el elemento DOM del modal de mensaje
 */
function crearModalMensaje(mensaje, tipo) {
  const modal = document.createElement('div');
  modal.className = 'fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 hidden modal-mensaje';
  
  const config = obtenerConfigTipo(tipo);
  
  modal.innerHTML = `
    <div class="glass-effect border ${config.borderColor} rounded-2xl p-6 w-full max-w-md shadow-2xl relative animate-fade-in-up">
      <!-- Icono -->
      <div class="flex justify-center mb-4">
        <div class="w-16 h-16 rounded-full ${config.bgGradient} ${config.borderRing} flex items-center justify-center ${config.animation}">
          <i data-lucide="${config.icon}" class="w-8 h-8 ${config.iconColor}"></i>
        </div>
      </div>

      <!-- Mensaje -->
      <p class="text-white text-center text-base mb-6 leading-relaxed">
        ${mensaje}
      </p>

      <!-- Botón cerrar -->
      <div class="flex justify-center">
        <button
          onclick="cerrarModalMensaje(this.closest('.modal-mensaje'))"
          class="px-6 py-2.5 text-sm font-semibold rounded-xl
                 ${config.btnColor} text-white
                 transition-all duration-200 hover-lift inline-flex items-center gap-2">
          <i data-lucide="check" class="w-4 h-4"></i>
          <span>Entendido</span>
        </button>
      </div>
    </div>
  `;

  // No cerrar con click fuera - solo con el botón
  
  return modal;
}

/**
 * Obtiene la configuración visual según el tipo de modal
 */
function obtenerConfigTipo(tipo) {
  const configs = {
    success: {
      icon: 'check-circle',
      iconColor: 'text-emerald-300',
      bgGradient: 'bg-gradient-to-br from-emerald-500/20 to-emerald-600/20',
      borderRing: 'border-2 border-emerald-500/50',
      borderColor: 'border-emerald-500/30',
      btnColor: 'bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 shadow-lg hover:shadow-emerald-500/50',
      animation: ''
    },
    error: {
      icon: 'x-circle',
      iconColor: 'text-red-300',
      bgGradient: 'bg-gradient-to-br from-red-500/20 to-red-600/20',
      borderRing: 'border-2 border-red-500/50',
      borderColor: 'border-red-500/30',
      btnColor: 'bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 shadow-lg hover:shadow-red-500/50',
      animation: 'animate-pulse'
    },
    warning: {
      icon: 'alert-triangle',
      iconColor: 'text-yellow-300',
      bgGradient: 'bg-gradient-to-br from-yellow-500/20 to-yellow-600/20',
      borderRing: 'border-2 border-yellow-500/50',
      borderColor: 'border-yellow-500/30',
      btnColor: 'bg-gradient-to-r from-yellow-600 to-yellow-500 hover:from-yellow-500 hover:to-yellow-400 shadow-lg hover:shadow-yellow-500/50',
      animation: 'animate-pulse'
    },
    info: {
      icon: 'info',
      iconColor: 'text-blue-300',
      bgGradient: 'bg-gradient-to-br from-blue-500/20 to-blue-600/20',
      borderRing: 'border-2 border-blue-500/50',
      borderColor: 'border-blue-500/30',
      btnColor: 'bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 shadow-lg hover:shadow-blue-500/50',
      animation: ''
    }
  };

  return configs[tipo] || configs.info;
}

/**
 * Cierra un modal de mensaje
 */
function cerrarModalMensaje(modal) {
  if (!modal) return;
  
  modal.classList.add('opacity-0');
  setTimeout(() => {
    modal.remove();
  }, 300);
}

/**
 * Muestra un modal de confirmación (para reemplazar confirm())
 * @param {string} mensaje - Pregunta a mostrar
 * @param {Function} onConfirm - Callback si se confirma
 * @param {Function} onCancel - Callback si se cancela (opcional)
 * @param {Object} opciones - Configuración adicional
 */
function mostrarConfirmacion(mensaje, onConfirm, onCancel = null, opciones = {}) {
  const config = {
    titulo: opciones.titulo || '¿Confirmar acción?',
    textoConfirmar: opciones.textoConfirmar || 'Confirmar',
    textoCancelar: opciones.textoCancelar || 'Cancelar',
    tipo: opciones.tipo || 'warning',
    iconoConfirmar: opciones.iconoConfirmar || 'check',
    iconoCancelar: opciones.iconoCancelar || 'x',
    ...opciones
  };

  const modal = crearModalConfirmacion(mensaje, config, onConfirm, onCancel);
  document.body.appendChild(modal);
  
  requestAnimationFrame(() => {
    modal.classList.remove('hidden');
    lucide.createIcons();
  });

  return modal;
}

/**
 * Crea el elemento DOM del modal de confirmación
 */
function crearModalConfirmacion(mensaje, config, onConfirm, onCancel) {
  const modal = document.createElement('div');
  modal.className = 'fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 hidden modal-confirmacion';
  
  const tipoConfig = obtenerConfigTipo(config.tipo);
  
  modal.innerHTML = `
    <div class="glass-effect border ${tipoConfig.borderColor} rounded-2xl p-8 w-full max-w-md shadow-2xl relative animate-fade-in-up">
      <!-- Icono -->
      <div class="flex justify-center mb-6">
        <div class="w-16 h-16 rounded-full ${tipoConfig.bgGradient} ${tipoConfig.borderRing} flex items-center justify-center ${tipoConfig.animation}">
          <i data-lucide="${tipoConfig.icon}" class="w-8 h-8 ${tipoConfig.iconColor}"></i>
        </div>
      </div>

      <!-- Título -->
      <h3 class="text-white text-xl font-bold text-center mb-3">
        ${config.titulo}
      </h3>

      <!-- Mensaje -->
      <p class="text-gray-300 text-center mb-6 leading-relaxed">
        ${mensaje}
      </p>

      <!-- Botones -->
      <div class="flex gap-4 justify-center">
        <button
          class="btn-cancelar px-6 py-3 text-sm font-semibold rounded-xl
                 bg-gray-700 hover:bg-gray-600 text-white
                 transition-all duration-200 hover-lift inline-flex items-center gap-2">
          <i data-lucide="${config.iconoCancelar}" class="w-4 h-4"></i>
          <span>${config.textoCancelar}</span>
        </button>
        <button
          class="btn-confirmar px-6 py-3 text-sm font-semibold rounded-xl
                 ${tipoConfig.btnColor} text-white
                 transition-all duration-200 hover-lift inline-flex items-center gap-2">
          <i data-lucide="${config.iconoConfirmar}" class="w-4 h-4"></i>
          <span>${config.textoConfirmar}</span>
        </button>
      </div>
    </div>
  `;

  // Manejadores de eventos
  const btnConfirmar = modal.querySelector('.btn-confirmar');
  const btnCancelar = modal.querySelector('.btn-cancelar');

  btnConfirmar.addEventListener('click', () => {
    cerrarModalConfirmacion(modal);
    if (onConfirm) onConfirm();
  });

  btnCancelar.addEventListener('click', () => {
    cerrarModalConfirmacion(modal);
    if (onCancel) onCancel();
  });

  // Click fuera cierra y cancela
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      cerrarModalConfirmacion(modal);
      if (onCancel) onCancel();
    }
  });

  // Escape cierra y cancela
  const escapeHandler = (e) => {
    if (e.key === 'Escape') {
      cerrarModalConfirmacion(modal);
      if (onCancel) onCancel();
      document.removeEventListener('keydown', escapeHandler);
    }
  };
  document.addEventListener('keydown', escapeHandler);

  return modal;
}

/**
 * Cierra un modal de confirmación
 */
function cerrarModalConfirmacion(modal) {
  if (!modal) return;
  
  modal.classList.add('opacity-0');
  setTimeout(() => {
    modal.remove();
  }, 300);
}

// Alias para compatibilidad con código existente
function mostrarToast(mensaje, tipo = 'info') {
  // Mapear tipos de toast a modal
  const tiposMapeados = {
    'success': 'success',
    'error': 'error',
    'warning': 'warning',
    'info': 'info',
    'exito': 'success'
  };
  
  mostrarModal(mensaje, tiposMapeados[tipo] || 'info');
}

// Exportar funciones
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { mostrarModal, mostrarConfirmacion, mostrarToast };
}
