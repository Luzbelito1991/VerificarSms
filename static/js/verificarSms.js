document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("smsForm");
  const personId = document.getElementById("personId");
  const phoneNumber = document.getElementById("phoneNumber");
  const merchantCode = document.getElementById("merchantCode");
  const verificationCode = document.getElementById("verificationCode");
  const codeDisplay = document.getElementById("codeDisplay");
  const generateBtn = document.getElementById("generateBtn");
  const rotateIcon = document.getElementById("rotateIcon");
  const submitBtn = document.getElementById("submitBtn");
  const submitText = document.getElementById("submitText");
  const loader = document.getElementById("loader");
  const cancelBtn = document.getElementById("cancelBtn");
  const addBranchBtn = document.getElementById("addBranchBtn");

  const sucursales = {
    "389": "Rincon Deportivo",
    "561": "Oregon Jeans",
    "776": "Alberdi",
    "777": "Lules",
    "778": "Famaillá",
    "779": "Alderetes",
    "781": "Banda de Río Salí"
  };

  // 💾 Cargar sucursales personalizadas desde localStorage
  function cargarSucursalesPersonalizadas() {
    const guardadas = localStorage.getItem("sucursalesPersonalizadas");
    if (guardadas) {
      try {
        const personalizadas = JSON.parse(guardadas);
        Object.keys(personalizadas).forEach(codigo => {
          sucursales[codigo] = personalizadas[codigo];
          // Agregar al select si no existe
          const existe = Array.from(merchantCode.options).find(opt => opt.value === codigo);
          if (!existe) {
            const option = document.createElement("option");
            option.value = codigo;
            option.textContent = `${codigo} - Limite Deportes ${personalizadas[codigo]}`;
            merchantCode.appendChild(option);
          }
        });
      } catch (e) {
        console.error("Error al cargar sucursales:", e);
      }
    }
  }

  // Cargar sucursales al iniciar
  cargarSucursalesPersonalizadas();

  personId.addEventListener("input", () => {
    personId.value = personId.value.replace(/\D/g, "").slice(0, 8);
  });

  phoneNumber.addEventListener("input", () => {
    phoneNumber.value = phoneNumber.value.replace(/\D/g, "").slice(0, 10);
  });

  if (generateBtn) {
    generateBtn.addEventListener("click", () => {
      const code = Math.floor(1000 + Math.random() * 9000).toString();
      verificationCode.value = code;
      codeDisplay.textContent = code;
      submitBtn.disabled = false;
      validarFormulario();

      if (rotateIcon) {
        rotateIcon.classList.add("rotate-[360deg]");
        setTimeout(() => rotateIcon.classList.remove("rotate-[360deg]"), 300);
      }
    });
  }

  function validarFormulario() {
    const dni = personId.value.trim();
    const phone = phoneNumber.value.trim();
    const isDniValid = /^\d{8}$/.test(dni);
    const isPhoneValid = /^\d{10}$/.test(phone);
    const isSucursalSelected = merchantCode.value !== "";
    const isCodeGenerated = verificationCode.value !== "";

    document.querySelector("#dniError span").classList.toggle("invisible", isDniValid || dni === "");
    document.querySelector("#phoneError span").classList.toggle("invisible", isPhoneValid || phone === "");

    submitBtn.disabled = !(isDniValid && isPhoneValid && isSucursalSelected && isCodeGenerated);
  }

  [personId, phoneNumber, merchantCode].forEach(input => {
    input.addEventListener("input", validarFormulario);
    input.addEventListener("change", validarFormulario);
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    submitText.textContent = "Enviando...";
    loader.classList.remove("hidden");
    submitBtn.disabled = true;

    const data = {
      personId: personId.value.trim(),
      phoneNumber: phoneNumber.value.trim(),
      merchantCode: merchantCode.value,
      merchantName: sucursales[merchantCode.value] || null,  // 🏪 Enviar nombre de sucursal
      verificationCode: verificationCode.value,
    };

    const msgPlano = `${data.merchantCode} Limite Deportes ${sucursales[data.merchantCode]} - DNI: ${data.personId} - Código: ${data.verificationCode}`;

    try {
      const res = await fetch("/send-sms", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      const result = await res.json();

      if (res.ok) {
        mostrarResultadoEnvio(true, msgPlano);
        mostrarToast("SMS enviado correctamente", "success");
      } else {
        mostrarResultadoEnvio(false, msgPlano);
        mostrarToast("No se pudo enviar el SMS. Verificá los datos.", "error");
      }

    } catch (error) {
      mostrarResultadoEnvio(false, msgPlano);
      mostrarToast("Error de red al enviar el SMS", "error");
    } finally {
      submitText.textContent = "Enviar";
      loader.classList.add("hidden");
      verificationCode.value = "";
      codeDisplay.textContent = "----";
      submitBtn.disabled = true;

      personId.value = "";
      phoneNumber.value = "";
      merchantCode.value = "";
      merchantCode.selectedIndex = 0;

      validarFormulario();
    }
  });

  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      personId.value = "";
      phoneNumber.value = "";
      merchantCode.value = "";
      merchantCode.selectedIndex = 0;
      verificationCode.value = "";
      codeDisplay.textContent = "----";
      submitBtn.disabled = true;

      document.querySelector("#dniError span").classList.add("invisible");
      document.querySelector("#phoneError span").classList.add("invisible");

      mostrarResultadoEnvio(false, "No hay mensajes aún");
      validarFormulario();
    });
  }

  function mostrarResultadoEnvio(exito, mensajePlano) {
    const container = document.getElementById("lastMessageContainer");
    const mensaje = document.getElementById("lastMessage");
    const icono = document.getElementById("statusIcon");

    container.classList.remove("bg-green-900", "border-green-700", "bg-red-900", "border-red-700");
    icono.classList.remove("text-green-400", "text-red-400");

    if (exito) {
      container.classList.add("bg-green-900", "border-green-700");
      icono.setAttribute("data-lucide", "check-circle");
      icono.classList.add("text-green-400");
      mensaje.textContent = `Mensaje Enviado Correctamente:\n${mensajePlano}`;
    } else {
      container.classList.add("bg-red-900", "border-red-700");
      icono.setAttribute("data-lucide", "x-circle");
      icono.classList.add("text-red-400");
      mensaje.textContent = `Mensaje no enviado:\n${mensajePlano}`;
    }

    lucide.createIcons();
  }

  function mostrarToast(mensaje, tipo = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const div = document.createElement('div');

    const base = "animate-fade-in-up transition-opacity duration-300 px-4 py-2 rounded-md shadow-lg text-sm flex items-center gap-2 max-w-md w-full mx-auto";
    const variantes = {
      success: "bg-emerald-700/90 text-white",
      error: "bg-red-700/90 text-white",
      info: "bg-blue-700/90 text-white"
    };
    const iconos = {
      success: "check",
      error: "x",
      info: "info"
    };

    div.className = `${base} ${variantes[tipo] || variantes.info}`;
    div.innerHTML = `
      <i data-lucide="${iconos[tipo] || iconos.info}" class="w-4 h-4 text-white/80 shrink-0"></i>
      <span class="flex-1">${mensaje}</span>
    `;

    toastContainer.appendChild(div);
    lucide.createIcons({ icons: [div] });

    setTimeout(() => {
      div.classList.add("opacity-0");
      setTimeout(() => div.remove(), 300);
    }, 4000);
  }

  // 🏪 Elementos del modal de sucursales
  const modalSucursal = document.getElementById("modalSucursal");
  const sucursalForm = document.getElementById("sucursalForm");
  const codigoSucursal = document.getElementById("codigoSucursal");
  const nombreSucursal = document.getElementById("nombreSucursal");

  // 🔓 Abrir modal al hacer click en botón agregar
  if (addBranchBtn) {
    addBranchBtn.addEventListener("click", (e) => {
      e.preventDefault();
      console.log("🏪 Abriendo modal de sucursal...");
      if (modalSucursal) {
        modalSucursal.classList.remove("hidden");
        if (codigoSucursal) {
          setTimeout(() => codigoSucursal.focus(), 100);
        }
        lucide.createIcons();
      }
    });
  } else {
    console.error("❌ No se encontró el botón addBranchBtn");
  }

  // Validar solo números en código
  if (codigoSucursal) {
    codigoSucursal.addEventListener("input", () => {
      codigoSucursal.value = codigoSucursal.value.replace(/\D/g, "").slice(0, 3);
    });
  }

  // Agregar sucursal
  if (sucursalForm) {
    sucursalForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const codigo = codigoSucursal.value.trim();
      const nombre = nombreSucursal.value.trim();

      if (codigo.length !== 3) {
        mostrarToast("El código debe tener 3 dígitos", "error");
        return;
      }

      if (!nombre) {
        mostrarToast("El nombre de sucursal es requerido", "error");
        return;
      }

      // Verificar si ya existe
      const opcionExistente = Array.from(merchantCode.options).find(
        opt => opt.value === codigo
      );

      if (opcionExistente) {
        mostrarToast("Ya existe una sucursal con ese código", "error");
        return;
      }

      // Agregar al diccionario y al select
      sucursales[codigo] = nombre;
      const nuevaOpcion = document.createElement("option");
      nuevaOpcion.value = codigo;
      nuevaOpcion.textContent = `${codigo} - Limite Deportes ${nombre}`;
      merchantCode.appendChild(nuevaOpcion);

      // 💾 Guardar en localStorage
      const guardadas = localStorage.getItem("sucursalesPersonalizadas");
      const personalizadas = guardadas ? JSON.parse(guardadas) : {};
      personalizadas[codigo] = nombre;
      localStorage.setItem("sucursalesPersonalizadas", JSON.stringify(personalizadas));

      // Seleccionar la nueva opción
      merchantCode.value = codigo;

      mostrarToast(`Sucursal ${codigo} agregada correctamente`, "success");
      cerrarModalSucursal();
      validarFormulario();
    });
  }
});

// 🚪 Funciones globales para cerrar modal (llamadas desde onclick en HTML)
function cerrarModalSucursal() {
  const modalSucursal = document.getElementById("modalSucursal");
  const sucursalForm = document.getElementById("sucursalForm");
  
  if (modalSucursal) modalSucursal.classList.add("hidden");
  if (sucursalForm) sucursalForm.reset();
}