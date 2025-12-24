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

  // Preview elements
  const previewCode = document.getElementById("previewCode");
  const previewPhone = document.getElementById("previewPhone");
  const previewSucursalFull = document.getElementById("previewSucursalFull");
  const previewStatus = document.getElementById("previewStatus");
  const previewStatusText = document.getElementById("previewStatusText");

  let sucursales = {}; // Se cargará desde la BD
  let saldoDisponible = null; // Se verificará al cargar

  // 💰 Verificar saldo disponible
  async function verificarSaldo() {
    try {
      const res = await fetch('/obtener-saldo');
      if (res.ok) {
        const data = await res.json();
        saldoDisponible = data.saldo;
        
        // Si no hay saldo, mostrar advertencia y deshabilitar envío
        if (saldoDisponible === 0) {
          mostrarToast('⚠️ Sin crédito disponible. No se pueden enviar SMS hasta recargar.', 'warning');
          // Deshabilitar botón de generar código
          if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.classList.add('opacity-50', 'cursor-not-allowed');
          }
        }
      }
    } catch (error) {
      console.warn('No se pudo verificar saldo:', error);
    }
  }

  // 🔄 Actualizar preview en tiempo real
  function actualizarPreview() {
    // Actualizar teléfono
    previewPhone.textContent = phoneNumber.value || "----------";
    
    // Actualizar código
    if (codeDisplay.textContent !== "----") {
      previewCode.textContent = codeDisplay.textContent;
    }
    
    // Actualizar línea de sucursal con formato: "782 - Limite Deportes BV - DNI: 36049884"
    const dni = personId.value || "--------";
    if (merchantCode.value) {
      const codigoSuc = merchantCode.value;
      const nombreSuc = sucursales[merchantCode.value] || "Sucursal";
      previewSucursalFull.textContent = `${codigoSuc} - ${nombreSuc} - DNI: ${dni}`;
    } else {
      previewSucursalFull.textContent = `Sucursal - DNI: ${dni}`;
    }
    
    // Actualizar estado visual
    const allFilled = personId.value.length === 8 && 
                      phoneNumber.value.length === 10 && 
                      merchantCode.value && 
                      codeDisplay.textContent !== "----";
    
    if (allFilled) {
      previewStatus.className = "w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse";
      previewStatusText.textContent = "Listo para enviar";
    } else {
      previewStatus.className = "w-1.5 h-1.5 bg-gray-600 rounded-full";
      previewStatusText.textContent = "En espera";
    }
  }

  // 🔄 Cargar sucursales desde la base de datos
  async function cargarSucursales() {
    try {
      const res = await fetch('/api/sucursales');
      const data = await res.json();
      
      // Limpiar el select
      merchantCode.innerHTML = '<option value="">Seleccionar sucursal</option>';
      
      // Llenar objeto de sucursales y select
      data.forEach(s => {
        sucursales[s.codigo] = s.nombre;
        const option = document.createElement('option');
        option.value = s.codigo;
        option.textContent = `${s.codigo} - ${s.nombre}`;
        merchantCode.appendChild(option);
      });
      
      console.log(`✅ ${data.length} sucursales cargadas desde BD`);
    } catch (error) {
      console.error('❌ Error al cargar sucursales:', error);
      mostrarToast('Error al cargar sucursales', 'error');
    }
  }

  // Cargar sucursales al iniciar
  cargarSucursales();
  
  // 💰 Verificar saldo al iniciar
  verificarSaldo();

  personId.addEventListener("input", () => {
    personId.value = personId.value.replace(/\D/g, "").slice(0, 8);
    actualizarPreview();
  });

  phoneNumber.addEventListener("input", () => {
    phoneNumber.value = phoneNumber.value.replace(/\D/g, "").slice(0, 10);
    actualizarPreview();
  });

  merchantCode.addEventListener("change", () => {
    actualizarPreview();
  });

  if (generateBtn) {
    generateBtn.addEventListener("click", () => {
      const code = Math.floor(1000 + Math.random() * 9000).toString();
      verificationCode.value = code;
      codeDisplay.textContent = code;
      previewCode.textContent = code; // Actualizar preview
      submitBtn.disabled = false;
      validarFormulario();
      actualizarPreview();

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

    // Mostrar error solo si hay texto pero no es válido
    document.querySelector("#dniError p").classList.toggle("invisible", isDniValid || dni === "");
    document.querySelector("#phoneError p").classList.toggle("invisible", isPhoneValid || phone === "");

    submitBtn.disabled = !(isDniValid && isPhoneValid && isSucursalSelected && isCodeGenerated);
  }

  [personId, phoneNumber, merchantCode].forEach(input => {
    input.addEventListener("input", validarFormulario);
    input.addEventListener("change", validarFormulario);
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // 🚫 Prevenir envío si no hay saldo
    if (saldoDisponible === 0) {
      mostrarToast('🔴 Sin crédito disponible. No se puede enviar SMS.', 'error');
      return;
    }

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
        
        // Si es modo test, mostrar toast amarillo
        if (result.esTest || result.modoSimulado) {
          mostrarToast("⚠️ SMS Test enviado correctamente", "warning");
        } else {
          mostrarToast("✅ SMS enviado correctamente", "success");
        }
      } else {
        mostrarResultadoEnvio(false, msgPlano);
        
        // Extraer mensaje de error garantizando que sea string
        let errorMsg = "No se pudo enviar el SMS";
        
        // 🚦 Manejo especial para rate limit (429)
        if (res.status === 429) {
          errorMsg = "⏱️ Límite de envíos alcanzado. Esperá un momento antes de intentar nuevamente.";
        } 
        // 💳 Manejo especial para sin saldo (402)
        else if (res.status === 402) {
          errorMsg = result.detail || "Saldo insuficiente. Contacte con su proveedor para recargar.";
        }
        // Otros errores
        else if (result.detail) {
          errorMsg = typeof result.detail === 'string' ? result.detail : JSON.stringify(result.detail);
        } else if (result.mensaje) {
          errorMsg = typeof result.mensaje === 'string' ? result.mensaje : JSON.stringify(result.mensaje);
        } else if (result.message) {
          errorMsg = typeof result.message === 'string' ? result.message : JSON.stringify(result.message);
        }
        
        console.log("🔴 Error recibido:", errorMsg, "Status:", res.status);
        
        // Mostrar en ROJO con el mensaje específico
        mostrarToast(`🔴 ${errorMsg}`, "error");
      }

    } catch (error) {
      mostrarResultadoEnvio(false, msgPlano);
      console.error("🔴 Error catch:", error);
      
      let errorMsg = "Error de red al enviar el SMS";
      if (error && typeof error === 'object') {
        if (error.message) errorMsg = error.message;
        else errorMsg = String(error);
      }
      
      mostrarToast(`🔴 ${errorMsg}`, "error");
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

  // Nota: mostrarToast() ahora se importa desde /static/js/modal.js (cargado en layout.html)
});