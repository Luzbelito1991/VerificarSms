// 🏢 Gestión de Sucursales
lucide.createIcons();

let modoEdicion = false;
let codigoOriginal = null;

// Cargar sucursales al inicio
document.addEventListener('DOMContentLoaded', cargarSucursales);

async function cargarSucursales() {
  try {
    const res = await fetch('/api/sucursales');
    const sucursales = await res.json();
    
    const tbody = document.getElementById('tablaSucursales');
    const listaMobile = document.getElementById('listaSucursalesMobile');
    
    if (sucursales.length === 0) {
      // Vista vacía para desktop
      tbody.innerHTML = `
        <tr>
          <td colspan="3" class="px-4 py-8 text-center text-gray-400">
            <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-3 opacity-50"></i>
            <p>No hay sucursales registradas</p>
          </td>
        </tr>
      `;
      // Vista vacía para mobile
      listaMobile.innerHTML = `
        <div class="px-4 py-8 text-center text-gray-400">
          <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-3 opacity-50"></i>
          <p class="text-sm">No hay sucursales registradas</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }
    
// Renderizar tabla desktop (más compacta y moderna)
    tbody.innerHTML = sucursales.map(s => `
      <tr class="hover:bg-gray-800/50 transition-colors duration-150">
        <td class="px-4 py-2.5 text-sm">
          <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-gradient-to-r from-purple-500/20 to-purple-600/20 border border-purple-500/30">
            <i data-lucide="hash" class="w-3 h-3 text-purple-300"></i>
            <span class="font-mono text-purple-300 font-semibold text-xs">${s.codigo}</span>
          </div>
        </td>
        <td class="px-4 py-2.5 text-sm">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 border border-emerald-500/30 flex items-center justify-center flex-shrink-0">
              <i data-lucide="building-2" class="w-4 h-4 text-emerald-400"></i>
            </div>
            <span class="text-gray-100 font-medium">${s.nombre}</span>
          </div>
        </td>
        <td class="px-4 py-2.5">
          <div class="flex items-center justify-center gap-2">
            <button
              onclick="editarSucursal('${s.codigo}', '${s.nombre.replace(/'/g, "\\'")}')" 
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 transition-all duration-200 hover:scale-105"
              title="Editar"
            >
              <i data-lucide="edit-2" class="w-3.5 h-3.5"></i>
              <span>Editar</span>
            </button>
            <button
              onclick="eliminarSucursal('${s.codigo}')"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-red-600/20 hover:bg-red-600/30 text-red-300 border border-red-500/30 transition-all duration-200 hover:scale-105"
              title="Eliminar"
            >
              <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
              <span>Eliminar</span>
            </button>
          </div>
        </td>
      </tr>
    `).join('');
    
    // Renderizar cards mobile (mejorados)
    listaMobile.innerHTML = sucursales.map(s => `
      <div class="p-3 hover:bg-gray-800/50 transition-colors">
        <div class="flex items-center justify-between gap-3">
          <div class="flex-1 min-w-0">
            <div class="inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-gradient-to-r from-purple-500/20 to-purple-600/20 border border-purple-500/30 mb-2">
              <i data-lucide="hash" class="w-3 h-3 text-purple-300"></i>
              <span class="font-mono text-purple-300 font-semibold text-xs">${s.codigo}</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-6 h-6 rounded-full bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 border border-emerald-500/30 flex items-center justify-center flex-shrink-0">
                <i data-lucide="building-2" class="w-3 h-3 text-emerald-400"></i>
              </div>
              <p class="text-gray-100 text-sm font-medium truncate">${s.nombre}</p>
            </div>
          </div>
          <div class="flex flex-col gap-1 flex-shrink-0">
            <button
              onclick="editarSucursal('${s.codigo}', '${s.nombre.replace(/'/g, "\\'")}')" 
              class="p-2 hover:bg-blue-500/20 text-blue-400 rounded-lg transition-colors"
            >
              <i data-lucide="edit-2" class="w-4 h-4"></i>
            </button>
            <button
              onclick="eliminarSucursal('${s.codigo}')"
              class="p-2 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors"
            >
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
          </div>
        </div>
      </div>
    `).join('');
    
    lucide.createIcons();
  } catch (error) {
    console.error('Error:', error);
    mostrarToast('Error al cargar sucursales', 'error');
  }
}

function abrirModalCrear() {
  modoEdicion = false;
  codigoOriginal = null;
  document.getElementById('modalTitulo').textContent = 'Nueva Sucursal';
  document.getElementById('inputCodigo').value = '';
  document.getElementById('inputNombre').value = '';
  document.getElementById('inputCodigo').disabled = false;
  document.getElementById('modalSucursal').classList.remove('hidden');
}

function editarSucursal(codigo, nombre) {
  modoEdicion = true;
  codigoOriginal = codigo;
  document.getElementById('modalTitulo').textContent = 'Editar Sucursal';
  document.getElementById('inputCodigo').value = codigo;
  document.getElementById('inputNombre').value = nombre;
  document.getElementById('inputCodigo').disabled = true; // No se puede cambiar el código
  document.getElementById('modalSucursal').classList.remove('hidden');
}

function cerrarModal() {
  document.getElementById('modalSucursal').classList.add('hidden');
}

document.getElementById('formSucursal').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const codigo = document.getElementById('inputCodigo').value.trim();
  const nombre = document.getElementById('inputNombre').value.trim();
  
  if (!codigo || !nombre) {
    mostrarToast('Completá todos los campos', 'error');
    return;
  }
  
  try {
    let res;
    
    if (modoEdicion) {
      // Editar
      res = await fetch(`/api/sucursales/${codigoOriginal}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre })
      });
    } else {
      // Crear
      res = await fetch('/api/sucursales', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codigo, nombre })
      });
    }
    
    const data = await res.json();
    
    if (res.ok) {
      mostrarToast(data.mensaje, 'exito');
      cerrarModal();
      cargarSucursales();
    } else {
      mostrarToast(data.detail || 'Error al guardar sucursal', 'error');
    }
  } catch (error) {
    console.error('Error:', error);
    mostrarToast('Error de conexión', 'error');
  }
});

async function eliminarSucursal(codigo) {
  if (!confirm(`¿Estás seguro de eliminar la sucursal ${codigo}?`)) {
    return;
  }
  
  try {
    const res = await fetch(`/api/sucursales/${codigo}`, {
      method: 'DELETE'
    });
    
    const data = await res.json();
    
    if (res.ok) {
      mostrarToast(data.mensaje, 'exito');
      cargarSucursales();
    } else {
      mostrarToast(data.detail || 'Error al eliminar sucursal', 'error');
    }
  } catch (error) {
    console.error('Error:', error);
    mostrarToast('Error de conexión', 'error');
  }
}
