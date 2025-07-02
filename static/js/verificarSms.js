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

  const sucursales = {
    "776": "Alberdi",
    "777": "Lules",
    "778": "Famaillá",
    "779": "Alderetes",
    "781": "Banda de Río Salí"
  };

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
});