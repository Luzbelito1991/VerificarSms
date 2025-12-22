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
    
    if (sucursales.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="3" class="px-4 py-8 text-center text-gray-400">
            <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-3 opacity-50"></i>
            <p>No hay sucursales registradas</p>
          </td>
        </tr>
      `;
      lucide.createIcons();
      return;
    }
    
    tbody.innerHTML = sucursales.map(s => `
      <tr class="hover:bg-white/5 transition-colors">
        <td class="px-4 py-3">
          <span class="font-mono text-emerald-400 font-semibold">${s.codigo}</span>
        </td>
        <td class="px-4 py-3 text-gray-300">${s.nombre}</td>
        <td class="px-4 py-3">
          <div class="flex items-center justify-center gap-2">
            <button
              onclick="editarSucursal('${s.codigo}', '${s.nombre.replace(/'/g, "\\'")}')"
              class="p-1.5 hover:bg-blue-500/20 text-blue-400 rounded-lg transition-colors"
              title="Editar"
            >
              <i data-lucide="edit" class="w-4 h-4"></i>
            </button>
            <button
              onclick="eliminarSucursal('${s.codigo}')"
              class="p-1.5 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors"
              title="Eliminar"
            >
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
          </div>
        </td>
      </tr>
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
