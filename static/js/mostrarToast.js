function mostrarToast(mensaje, tipo = 'success') {
  const toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) return;

  const div = document.createElement('div');

  // 🎨 Estilo base snopi: centrado, refinado, sin ícono
  const base = `
    transition-opacity duration-300 ease-in-out 
    px-6 py-3 rounded-lg border shadow-md text-sm font-medium text-white 
    bg-opacity-90 backdrop-blur-md max-w-md w-full mx-auto
  `;

  // 🎨 Variantes de color según tipo
  const variantes = {
    success: "bg-emerald-600 border-emerald-500",
    error: "bg-red-600 border-red-500",
    info: "bg-blue-600 border-blue-500"
  };

  // 🧱 Aplicamos clases combinadas
  div.className = `${base} ${variantes[tipo] || variantes.info}`.replace(/\s+/g, ' ').trim();

  // 💬 Contenido del mensaje
  div.innerHTML = `
    <div class="text-center">${mensaje}</div>
  `;

  toastContainer.appendChild(div);

  // ⏳ Desaparece automáticamente después de 5 segundos
  setTimeout(() => {
    div.classList.add("opacity-0");
    setTimeout(() => div.remove(), 300);
  }, 5000);
}