document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");

  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const user = document.getElementById("username").value.trim();
    const pass = document.getElementById("password").value.trim();

    if (user && pass) {
      window.location.href = "/verificar"; // Podés cambiar esta ruta al destino real
    } else {
      alert("Por favor, completá ambos campos.");
    }
  });
});