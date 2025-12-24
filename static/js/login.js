// 📦 Esperar a que el DOM cargue antes de ejecutar cualquier lógica
document.addEventListener("DOMContentLoaded", () => {
  // 🎯 Elementos clave del formulario y la UI
  const loginForm = document.getElementById("loginForm");            // Formulario de login
  const toggle = document.getElementById("togglePassword");          // Botón para mostrar/ocultar contraseña
  const pwd = document.getElementById("password");                   // Campo de contraseña
  const icon = document.getElementById("eyeIcon");                   // Ícono del ojo
  const toast = document.getElementById("toastLoginError");          // Contenedor del toast de error
  const toastMsg = document.getElementById("toastMessage");          // Texto dentro del toast

  // 👁️ Toggle de visibilidad de contraseña
  toggle.addEventListener("click", () => {
    const visible = pwd.type === "text";                             // ¿Está visible?
    pwd.type = visible ? "password" : "text";                        // Cambiar tipo
    icon.setAttribute("data-lucide", visible ? "eye" : "eye-off");   // Cambiar ícono
    lucide.createIcons();                                            // Volver a renderizar el ícono
  });

  // Nota: mostrarToast() ahora se importa desde /static/js/modal.js (cargado en layout.html)

  // 🔐 Validación de login al enviar el formulario
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();                                              // Evitar envío tradicional

    // 📥 Capturar valores de usuario y contraseña
    const user = document.getElementById("username").value.trim();
    const pass = document.getElementById("password").value.trim();

    // 🚫 Validación básica
    if (!user || !pass) {
      mostrarToast("Por favor, completá ambos campos.");
      return;
    }

    try {
      // 📡 Enviar solicitud al backend
      const response = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario: user, password: pass })
      });

      const result = await response.json();                          // Leer respuesta del backend

      // ✅ Si login fue exitoso, redirigir con el nombre del usuario
      if (response.ok && result.ok) {
        window.location.href = `/home?user=${encodeURIComponent(result.usuario)}`;
      } else {
        // ❌ Si el login falló, mostrar mensaje
        // El detail puede ser string o objeto con propiedad 'mensaje'
        let errorMsg = "Credenciales inválidas.";
        if (result.detail) {
          errorMsg = typeof result.detail === 'string' 
            ? result.detail 
            : (result.detail.mensaje || result.mensaje || "Credenciales inválidas.");
        } else if (result.mensaje) {
          errorMsg = result.mensaje;
        }
        mostrarToast(errorMsg);
      }
    } catch (error) {
      // ⚠️ Error de red u otra excepción
      console.error("Error al iniciar sesión:", error);
      mostrarToast("Error al conectar con el servidor.");
    }
  });
});