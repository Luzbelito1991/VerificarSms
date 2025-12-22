// ✅ Este archivo ahora redirige a modal.js para mantener compatibilidad
// La función mostrarToast() está definida en /static/js/modal.js

// Exportar para compatibilidad con módulos ES6
export function mostrarToast(mensaje, tipo = 'success') {
  // Mapear tipos antiguos a nuevos
  const tiposMapeados = {
    'success': 'success',
    'error': 'error',
    'warning': 'warning',
    'info': 'info',
    'exito': 'success'
  };
  
  // Llamar a la función global del modal.js
  if (typeof window.mostrarModal !== 'undefined') {
    window.mostrarModal(mensaje, tiposMapeados[tipo] || 'info');
  } else if (typeof window.mostrarToast !== 'undefined') {
    window.mostrarToast(mensaje, tipo);
  } else {
    console.error('Sistema de modales no disponible');
    alert(mensaje);
  }
}
