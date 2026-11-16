//console.log("HELPERS loaded");

let linkHP = document.createElement('link');
linkHP.rel = 'stylesheet';
linkHP.href = '/static/css/helpers.css';
document.head.appendChild(linkHP);

if (configDev && configDev.MS_SOY){
    window.thisRol = configDev.MS_SOY.rol;
}

function numMuestraVenta(prod){
    let i = 0;
    i+= prod.muestraUnidad;
    i+= prod.muestraPaquete;
    i+= prod.muestraKg;
    return i;
}

const tiposPago = {"E": "Efectivo", "R": "Transferencia", "T": "Tarjeta"}

let audioCtx;

function getAudioContext() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === "suspended") {
        audioCtx.resume();
    }
    return audioCtx;
}

// document.addEventListener("pointerdown", () => {
//     getAudioContext();
// }, { once: true });


// async function myfetch(route, requestObject = {}) {
//     try {
//         const res = await fetch(route, {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify(requestObject)
//         });

//         if (!res.ok) {
//             console.log("Server returned an error:", res.status);
//             return {"success": false, "error": "Server returned an error: "+res.status};
//         }

//         const data = await res.json();

//         if (!data.success) {
//             console.log(data.error);
//         }
//         return data;   // SUCCESS

//     } catch (err) {
//         console.error("Error al comunicarse con el servidor:", err);
//         return {"success": false, "error": "Error al comunicarse con el servidor: "+err};
//     }
// }

if (configDev && configDev["MS_SOY"]){
    window.thisRol=configDev["MS_SOY"]["rol"];
}

const isValidDate = (year, month, day) => {
    const date = new Date(parseInt(anios.value), parseInt(month)-1, parseInt(day));
    //console.log(date);
    return date.getFullYear() === parseInt(year) && 
        date.getMonth() === (parseInt(month)-1) && 
        date.getDate() === parseInt(day);
};

const getWeekdaySpanish = (year, month, day) => {
    const y = parseInt(year);
    const m = parseInt(month) - 1;
    const d = parseInt(day);
    const date = new Date(y, m, d);
    // Validate (prevents rollover like Feb 30 → Mar 2)
    if (
        date.getFullYear() !== y ||
        date.getMonth() !== m ||
        date.getDate() !== d
    ) {
        return "";
    }
    const weekdaysES = [
        "Domingo",   // 0
        "Lunes",     // 1
        "Martes",    // 2
        "Miércoles", // 3
        "Jueves",    // 4
        "Viernes",   // 5
        "Sábado"     // 6
    ];
    return weekdaysES[date.getDay()];
};

function nombreDispositivo(dispositivoId){
    if (!configDev){
        return;
    }
    if (configDev["MS_SOY"] && configDev["MS_SOY"]["dispositivoId"]){
        if (configDev["MS_SOY"]["dispositivoId"]==dispositivoId){
            return configDev["MS_SOY"]["nombre"];
        }
    }
    if (configDev["MS_ESCLAVOS"] && configDev["MS_ESCLAVOS"].length>0){
        for (let i=0; i<configDev["MS_ESCLAVOS"].length; i++){
            //console.log(configDev["MS_ESCLAVOS"][i]);
            //console.log(dispositivoId);
            if (configDev["MS_ESCLAVOS"][i]["dispositivoId"]==dispositivoId){
                //console.log("Lo econtro");
                return configDev["MS_ESCLAVOS"][i]["nombre"];
            }
        }
    }
    if (configDev["MS_MAESTROS"] && configDev["MS_MAESTROS"].length>0){
        for (let i=0; i<configDev["MS_MAESTROS"].length; i++){
            if (configDev["MS_MAESTROS"][i]["dispositivoId"]==dispositivoId){
                return configDev["MS_MAESTROS"][i]["nombre"];
            }
        }
    }
    return;
}

async function myfetch(route, requestObject = {}, timeoutMs = 30000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const res = await fetch(route, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestObject),
            signal: controller.signal
        });
        //alert(JSON.stringify(res));
        if (!res.ok) {
            console.log("Server returned an error:", res.status);
            return {
                success: false,
                error: "Server returned an error: " + res.status
            };
        }
        const data = await res.json();
        //alert("data "+JSON.stringify(data));
        if (!data.success) {
            console.log(data.error);
        }
        return data;
    } catch (err) {
        console.error("Error al comunicarse con el servidor:", err);
        if (err.name === "AbortError") {
            return {
                success: false,
                error: "Sin respuesta a los "+timeoutMs/1000+" segundos"
            };
        }
        return {
            success: false,
            error: "Network error: " + err.message
        };
    } finally {
        clearTimeout(timeoutId);
    }
}

async function getConfigDevice(){
    let res = await myfetch("/config/device");
    //console.log(res);
    if (res && res.success){
        return res.resultado
    } else {
        return null;
    }
}

function enableEnterCommit(input) {
    let committedValue = input.value;
    let enterPressed = false;

    // Prevent native change events from bubbling
    input.addEventListener("change", function (e) {
        // Stop it so TAB won't trigger your logic
        e.stopImmediatePropagation();
    }, true); // capture phase

    // Detect ENTER press
    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            enterPressed = true;
            committedValue = input.value;

            // Now we fire our OWN change event
            const event = new Event("committedchange", { bubbles: true });
            input.dispatchEvent(event);
        }
    });

    // On blur (TAB, click, etc.)
    input.addEventListener("blur", function () {
        if (!enterPressed) {
            // Restore original committed value
            input.value = committedValue;
        }
        enterPressed = false;
    });
}

function capitalizeWordsES(str) {
    return str.replace(/\b([a-záéíóúñü])/g, c => c.toUpperCase());
}

// function formatDate(inputDate){
//     const d = new Date(inputDate);

//     const fecha = d.toLocaleDateString('es-ES', {
//         weekday: 'short',
//         day: '2-digit',
//         month: 'short',
//         year: 'numeric',
//         timeZone: 'UTC'   // ⬅️ prevents shifting
//     });

//     const hora = d.toLocaleTimeString('es-ES', {
//         hour: '2-digit',
//         minute: '2-digit',
//         second: '2-digit',
//         hour12: false,
//         timeZone: 'UTC'   // ⬅️ prevents shifting
//     });

//     return `${capitalizeWordsES(fecha)} ${hora}`;
// }
    // harp

// function playScanSound() {
//     try {
//         navigator.vibrate?.(30);

//         const ctx = new (window.AudioContext || window.webkitAudioContext)();
//         const now = ctx.currentTime;

//         const osc = ctx.createOscillator();
//         const gain = ctx.createGain();

//         osc.type = "sine";          // smooth, not harsh
//         osc.frequency.value = 880;  // soft confirmation tone
//         // osc.frequency.setValueAtTime(900, now);
//         // osc.frequency.exponentialRampToValueAtTime(820, now + 0.1);

//         osc.frequency.value = 740;
//         gain.gain.exponentialRampToValueAtTime(0.18, now + 0.01);
//         gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.10);

//         //gain.gain.setValueAtTime(0.0001, now);
//         //gain.gain.exponentialRampToValueAtTime(0.25, now + 0.01);  // fast attack
//         //gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.12); // quick fade

//         osc.connect(gain);
//         gain.connect(ctx.destination);

//         osc.start(now);
//         osc.stop(now + 0.13);

//     } catch (e) {}
// }

function playInteractionSound() {
    try {
        navigator.vibrate?.(25);

        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const now = ctx.currentTime;

        const master = ctx.createGain();
        master.gain.setValueAtTime(0.3, now);
        master.connect(ctx.destination);

        const notes = [660, 880]; // E5 → A5 (clean upward feel)

        notes.forEach((freq, i) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = "square"; // softer than square, warmer than sine
            osc.frequency.setValueAtTime(freq, now + i * 0.06);

            gain.gain.setValueAtTime(0.0001, now + i * 0.06);
            gain.gain.exponentialRampToValueAtTime(0.22, now + i * 0.06 + 0.01);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.06 + 0.12);

            osc.connect(gain);
            gain.connect(master);

            osc.start(now + i * 0.06);
            osc.stop(now + i * 0.18);
        });

    } catch (e) {}
}

function playSuccessSound() {
    try {
        navigator.vibrate?.(50);

        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const now = ctx.currentTime;

        const master = ctx.createGain();
        master.gain.setValueAtTime(0.35, now);
        master.gain.exponentialRampToValueAtTime(0.0001, now + 1.5);
        master.connect(ctx.destination);

        const notes = [523.25, 659.25, 783.99]; // C–E–G

        notes.forEach((freq, i) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = "triangle";
            osc.frequency.setValueAtTime(freq, now + i * 0.05);

            gain.gain.setValueAtTime(0.6, now + i * 0.05);
            gain.gain.exponentialRampToValueAtTime(
                0.0001,
                now + 1.2
            );

            osc.connect(gain);
            gain.connect(master);

            osc.start(now + i * 0.05);
            osc.stop(now + 1.4);
        });
    } catch (e) {}
}

function playScanSound() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const o = ctx.createOscillator();
        const g = new GainNode(ctx, { gain: 0.5 });
        o.connect(g);
        g.connect(ctx.destination);
        o.start();
        o.stop(ctx.currentTime + 0.2);
    } catch (e) { }
}

// function playErrorSound(durationMs = 600) {
//     try {
//         // Stronger vibration pattern
//         navigator.vibrate?.([40, 40, 40]);

//         const ctx = new (window.AudioContext || window.webkitAudioContext)();
//         const now = ctx.currentTime;
//         const duration = durationMs / 1000;

//         const master = ctx.createGain();
//         master.gain.setValueAtTime(0.5, now);
//         master.gain.exponentialRampToValueAtTime(0.0001, now + duration);
//         master.connect(ctx.destination);

//         // Slightly dissonant interval (tritone-ish)
//         const freqs = [220, 233]; // A + small detune → error feel

//         freqs.forEach(freq => {
//             const osc = ctx.createOscillator();
//             const gain = ctx.createGain();

//             osc.type = "sawtooth"; // harsher than triangle
//             osc.frequency.setValueAtTime(freq, now);

//             gain.gain.setValueAtTime(0.7, now);
//             gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

//             osc.connect(gain);
//             gain.connect(master);

//             osc.start(now);
//             osc.stop(now + duration);
//         });

//     } catch (e) {}
// }

// function playErrorSound(durationMs = 700) {
//     try {
//         // Heavier vibration
//         navigator.vibrate?.([60, 40, 60]);

//         const ctx = new (window.AudioContext || window.webkitAudioContext)();
//         const now = ctx.currentTime;
//         const duration = durationMs / 1000;

//         const master = ctx.createGain();
//         master.gain.setValueAtTime(0.6, now);
//         master.gain.exponentialRampToValueAt(0.0001, now + duration);
//         master.connect(ctx.destination);

//         // Much lower frequencies
//         const freqs = [110, 124]; // A2 + detuned B♭2-ish

//         freqs.forEach(freq => {
//             const osc = ctx.createOscillator();
//             const gain = ctx.createGain();

//             osc.type = "sawtooth"; // gritty error tone
//             osc.frequency.setValueAtTime(freq, now);

//             gain.gain.setValueAtTime(0.8, now);
//             gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

//             osc.connect(gain);
//             gain.connect(master);

//             osc.start(now);
//             osc.stop(now + duration);
//         });

//     } catch (e) {}
// }

function playErrorSound(durationMs = 3000) {
    try {
        navigator.vibrate?.([80, 40, 80]);
        //navigator.vibrate?.([120, 60, 120]);

        const ctx = getAudioContext();
        const now = ctx.currentTime;
        const duration = durationMs / 1000;

        const master = ctx.createGain();
        master.gain.setValueAtTime(1.0, now); // LOUD
        master.gain.exponentialRampToValueAtTime(0.0001, now + duration);
        master.connect(ctx.destination);

        // Frequencies tablets can hear clearly
        //const freqs = [180, 220]; // low but audible
        const freqs = [140, 180]; // low but audible

        //const freqs = [40, 70]; // A1 + detuned B1

        freqs.forEach(freq => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = "triangle"; // strong presence "square"
            osc.frequency.setValueAtTime(freq, now);

            gain.gain.setValueAtTime(0.9, now);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

            osc.connect(gain);
            gain.connect(master);

            osc.start(now);
            osc.stop(now + duration);
        });

    } catch (e) {
        console.error("Error sound failed", e);
    }
}

function formatDate(inputDate){
    let myDate = new Date(inputDate);
    // Formato de fecha
    //const opcionesFecha = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
    const opcionesFecha = { weekday: 'short', day: '2-digit', month: '2-digit', year: '2-digit' };
    let fechaFormateada = myDate.toLocaleDateString('es-ES', opcionesFecha);
    fechaFormateada = fechaFormateada[0].toUpperCase()+fechaFormateada.slice(1);
    // Formato de hora
    const opcionesHora = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }; // second: '2-digit',
    const horaFormateada = myDate.toLocaleTimeString('es-ES', opcionesHora);
    return fechaFormateada+' '+horaFormateada;
}

function centerMessage(msg, mode=2, color="yellow") {

    let centerMessageTimeout = null;
    //font-size: 2em; 

    let myStyles = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        padding: 20px 30px;
        background: rgba(0, 0, 0, 0.85);
        color: ${color};
        font-size: 35px !important; 
        border-radius: 10px;
        z-index: 10000;
        opacity: 0;
        pointer-events: none; /* so it doesn't block page clicks */
        transition: opacity 0.3s ease-in-out;
    `;

    if (window.thisRol=="esclavo"){
        myStyles = `
        position: fixed;
        top: 70px;
        left: 50%;
        transform: translate(-50%);
        padding: 20px 30px;
        background: rgba(0, 0, 0, 0.85);
        color: ${color};
        font-size: 35px !important; 
        border-radius: 10px;
        z-index: 10000;
        opacity: 0;
        pointer-events: none; /* so it doesn't block page clicks */
        transition: opacity 0.3s ease-in-out;
        `;
    }

    let mydiv = document.getElementById("centerMessage");
    if (!mydiv){
        mydiv = document.createElement("div");
        mydiv.id = "centerMessage";
        mydiv.style.cssText = myStyles;
        document.body.appendChild(mydiv);
    }

    // Clear any existing timeout
    if (centerMessageTimeout) {
        clearTimeout(centerMessageTimeout);
        centerMessageTimeout = null;
    }

    // --- Hide mode ---
    if (mode === false) {
        mydiv.style.opacity = "0";
        mydiv.style.pointerEvents= "none";
        return;
    }

    // --- Show message ---
    mydiv.innerHTML = msg;
    mydiv.style.opacity = "1";
    mydiv.style.pointerEvents= "none";

    // --- Timed mode ---
    if (typeof mode === "number" && mode > 0) {
        centerMessageTimeout = setTimeout(() => {
            mydiv.style.opacity = "0";
            mydiv.style.pointerEvents= "none";
        }, mode * 1000);
    }

    // --- If mode === true → show indefinitely (no auto-hide) ---
}

// /* RENDER TABLES HELPERS */

// function getCell(tr, colKey) {
//   return tr.querySelector(`td[data-col="${colKey}"]`);
// }

// function getInput(tr, colKey) {
//   return getCell(tr, colKey)?.querySelector("input") || null;
// }

/* TICKET HELPERS */

const FULL_LINE_CHARS = 31;

async function loadIVA() {
    let res = await myfetch("/ajustes/sel", {"variable":"IVA"});
    if (res.success && res.resultado.length==1) {
        //console.log(res.resultado);
        window.IVA = parseFloat(res.resultado[0]["valor"]);
    }
}

function parseSmartNumber(str, numDecimals=2) {
    const n = Number(str);
    if (Number.isNaN(n)) return null; // or throw
    return Number.isInteger(n) ? n : Number(n.toFixed(numDecimals));
}

function wrapByWords(text, maxChars, breakWords = false) {
  const lines = [];

  if (!text) return lines;

  // ---- HARD BREAK MODE (ignore words) ----
  if (breakWords) {
    let i = 0;
    while (i < text.length) {
      lines.push(text.slice(i, i + maxChars));
      i += maxChars;
    }
    return lines;
  }

  // ---- WORD-AWARE MODE (default) ----
  const words = text.trim().split(/\s+/);
  let current = "";

  for (const word of words) {
    const test = current ? current + " " + word : word;

    if (test.length > maxChars) {
      if (current) lines.push(current);
      current = word;
    } else {
      current = test;
    }
  }

  if (current) lines.push(current);
  return lines;
}

function calculateTotal(productos) {
  return productos.reduce((sum, p) => {
    return sum + parseSmartNumber(p.subtotal ?? 0);
  }, 0);
}

function parseFecha(fecha) {
  if (fecha instanceof Date) return fecha;
  const d = new Date(fecha);
  return isNaN(d) ? new Date(0) : d; // fallback for bad dates
}

function groupAndSortByFechaVenta(productos) {
  const map = productos.reduce((acc, prod) => {
    const fecha = prod.fechaVenta || "SIN_FECHA";
    console.log(fecha);
    if (!acc[fecha]) acc[fecha] = [];
    acc[fecha].push(prod);
    return acc;
  }, {});

  // Convert to sortable array
  return Object.entries(map)
    .map(([fecha, productos]) => ({
      fecha,
      productos,
      fechaDate: parseFecha(fecha)
    }))
    .sort((a, b) => a.fechaDate - b.fechaDate); // chronological
}

// function generateTicket(productos, total, fechaVenta){
//     let divTicket = document.createElement("div");
//     divTicket.setAttribute("id", "ticket");
//     divTicket.classList.add("ticket");
//     //divTicket.style.alignItems="center";
//     divTicket.style.textAlign="center";
//     let printTicket = document.createElement("button");
//     printTicket.textContent="Imprimir";
//     printTicket.style.minHeight="25px";
//     printTicket.style.marginBottom="20px";    
//     let ticketInner = document.createElement("div");
//     ticketInner.classList.add("ticket-inner");
//     let ticketHeader = document.createElement("div");
//     ticketHeader.setAttribute("id", "ticketHeader");
//     ticketHeader.style.textAlign = "center";
//     ticketHeader.textContent="COMERCIALIZADORA TICOMAN";
//     let ticketDateTime = document.createElement("div");
//     ticketDateTime.setAttribute("id", "ticketDatetime");
//     ticketDateTime.style.textAlign = "center";
//     ticketDateTime.textContent = fechaVenta;
//     let prodsTicket = document.createElement("div");
//     prodsTicket.setAttribute("id", "ticketProductos");
//     let ticketLines = buildEscPosLines(productos);
//     prodsTicket.textContent = ticketLines.join("\n");
//     let ticketTotal = document.createElement("div");
//     ticketTotal.setAttribute("id", "ticketTotal");
//     ticketTotal.style.textAlign = "right";
//     ticketTotal.textContent='Total: $'+String(parseSmartNumber(total));
//     ticketInner.append(ticketHeader);
//     ticketInner.append(ticketDateTime);
//     ticketInner.append(prodsTicket);
//     ticketInner.append(ticketTotal);
//     divTicket.append(printTicket);
//     divTicket.append(ticketInner);
//     printTicket.addEventListener("click", async function(){
//         await printTicketEscPos(ticketInner);
//     });
//     divTicket.style.transform = "scale(1.4)";
//     return divTicket;
// }

async function generateTicket(productos) {
  let divTicket = document.createElement("div");
  divTicket.id = "ticket";
  divTicket.classList.add("ticket");
  divTicket.style.textAlign = "center";

  let printTicket = document.createElement("button");
  printTicket.textContent = "Imprimir";
  printTicket.style.minHeight = "25px";
  printTicket.style.marginBottom = "20px";

  let ticketInner = document.createElement("div");
  ticketInner.classList.add("ticket-inner");

  let ticketHeader = document.createElement("div");
  ticketHeader.id = "ticketHeader";
  ticketHeader.style.textAlign = "center";
  ticketHeader.textContent = "FERRETERIA\nCOMERCIALIZADORA TICOMAN";
  //ticketHeader.textContent = "COMERCIALIZADORA TICOMAN";
  ticketInner.append(ticketHeader);

  // 🔽 GROUP + SORT HERE
  const gruposOrdenados = groupAndSortByFechaVenta(productos);

  let totalesMultiplesVentas = [];

  console.log("gruposOrdenados "+gruposOrdenados);

  //gruposOrdenados.forEach(({ fecha, productos }) => function(){
  for (const {fecha, productos} of gruposOrdenados){
    // Fecha
    let ticketDateTime = document.createElement("div");
    ticketDateTime.classList.add("ticketDatetime");
    ticketDateTime.style.textAlign = "center";
    ticketDateTime.textContent = "\n"+formatDate(fecha);
    ticketInner.append(ticketDateTime);
    // if (productos.length<5){
    //     ticketInner.append(document.createElement("br"));
    // }
    
    let prodTitle = document.createElement("div");
    prodTitle.style.textAlign = "center";
    prodTitle.classList.add("ticketProdTitle");
    prodTitle.textContent = "\n"+printThreeValuesTicket("Cant", "Descripcion", "Subtotal")+"\n"+("=".repeat(FULL_LINE_CHARS));
    //prodTitle.append(document.createElement("br"));
    ticketInner.append(prodTitle);

    // Productos
    let prodsTicket = document.createElement("div");
    prodsTicket.classList.add("ticketProductos");
    prodsTicket.textContent = buildEscPosLines(productos).join("\n");
    ticketInner.append(prodsTicket);

    // Total
    let totalGrupo = calculateTotal(productos);
    let ticketTotal = document.createElement("div");
    ticketTotal.classList.add("ticketTotal");
    ticketTotal.style.textAlign = "center";
    let totalLine = printThreeValuesTicket(null, "#Arts: "+productos.length, "Total: $" + totalGrupo.toFixed(2));
    //ticketTotal.textContent = "Total: $" + totalGrupo.toFixed(2);
    ticketTotal.textContent = "\n"+totalLine;
    //ticketTotal.append(totalLine);
    

    console.log("productos grupo");
    console.log(JSON.stringify(productos));
    let infoPago = await myfetch("/vender/getPago", {"dispositivoId": productos[0]["dispositivoId"], "fechaVenta": fecha});
    console.log(JSON.stringify(infoPago));
    if (infoPago["success"] && infoPago["resultado"] && infoPago["resultado"].length==1){
        let pagoRes = infoPago["resultado"][0];
        let tipoPago = tiposPago[pagoRes["tipoPago"]];
        let pagoLine = printThreeValuesTicket(null, "Pagó: "+tipoPago, "$"+Number(pagoRes["pago"]).toFixed(2));
        console.log(pagoLine);
        ticketTotal.textContent += "\n"+pagoLine;
        pagoLine = pagoRes["tipoPago"]=="E" && (Number(pagoRes["cambio"])??0)>0 ? printThreeValuesTicket(null, "Cambio:",  "$"+Number(pagoRes["cambio"]??0).toFixed(2) ) : "";
        console.log(pagoLine);
        ticketTotal.textContent += "\n"+pagoLine;
    }
    ticketInner.append(ticketTotal);

    totalesMultiplesVentas.push(totalGrupo);

  };

  if (totalesMultiplesVentas.length>1){
    let ticketSummary = document.createElement("div");
    ticketSummary.style.textAlign = "center";
    ticketSummary.classList.add("ticketSummary");
    ticketSummary.textContent = "\n"+("=".repeat(FULL_LINE_CHARS))+"\nResumen de "+totalesMultiplesVentas.length+" ventas\n"+("=".repeat(FULL_LINE_CHARS))+"\n";
    let num_ven = 0;
    let gran_total = 0;
    totalesMultiplesVentas.forEach( tg => {
        num_ven = num_ven+1;
        let totalLine = printThreeValuesTicket(null, "Venta #"+num_ven+":",  "$" + tg.toFixed(2))+"\n";
        ticketSummary.textContent +=totalLine;
        gran_total+=tg;
        }
    );
    ticketSummary.textContent += "-".repeat(FULL_LINE_CHARS)+"\n"+printThreeValuesTicket(null, "Gran Total:",  "$" + gran_total.toFixed(2));
    ticketInner.append(ticketSummary);

  }

  let ticketFooter = document.createElement("div");
  ticketFooter.style.textAlign = "center";
  ticketFooter.classList.add("ticketFooter");
  ticketFooter.textContent="\nGRACIAS POR SU COMPRA\n";
  ticketInner.append(ticketFooter);
  divTicket.append(printTicket);
  divTicket.append(ticketInner);

  printTicket.addEventListener("click", async () => {
    console.log("CLICK imprimir");
    await printTicketEscPos(ticketInner);
  });

  divTicket.style.transform = "scale(1.4)";
  divTicket.style.transformOrigin = "top center";

  return divTicket;
}

function centerLine(text, width) {
    console.log("CENTER LINE: "+text);
    if (!text) return "";
    text = text.trim();
    const pad = Math.max(0, width - text.length);
    const left = Math.floor(pad / 2);
    return " ".repeat(left) + text;
}

function rightAlignLine(text, width) {
    if (!text) return "";
    return text.trim().padStart(width, " ");
}

function toTitleCase(str) {
  return str
    .replace(/_/g, " ")
    .replace(/\b\w/g, c => c.toUpperCase());
}

function pluralUnidad(unidad){
    return unidad=="unidad"?unidad+"es":unidad+"s";
}

function padLeft(str, len) {
    return str.padStart(len, " ");
}
function padRight(str, len) {
    return str.padEnd(len, " ");
}

function printThreeValuesTicket(valA, valB, valC){
    const valAwidth   = (valA? valA.length +1 : 0);     // + space
    const valCwidth = (valC? valC.length +1 : 0);     // + space
    const valBwidth = FULL_LINE_CHARS - valAwidth - valCwidth;
    const wrappedFirst = wrapByWords(valB, valBwidth, true);
    const firstLine = wrappedFirst[0] || "";
    return (valA? padLeft(valA, valAwidth - 1) + " ": "") +
            padRight(firstLine, valBwidth) +
           (valC? " "+padLeft(valC, valCwidth - 1): "");
}

function buildEscPosLines(productos, 
    columnaCantidad="cantidad",
    columnaDescripcion="descripcion",
    columnaSubtotal= "subtotal",
    printOverflow = false) {

    const lines = [];
    //const codigos = [];

    productos.forEach(prod => {
        const qty   = String(parseSmartNumber(prod[columnaCantidad]));
        const desc  = String(prod[columnaDescripcion]);
        const price = '$'+String(parseSmartNumber(prod[columnaSubtotal]));
        const qtyWidth   = qty.length + 1;     // + space
        const priceWidth = price.length + 1;   // + space

        const descFirstMax = FULL_LINE_CHARS - qtyWidth - priceWidth;

        // ---- wrap description ----
        const wrappedFirst = wrapByWords(desc, descFirstMax, true);
        const firstLine = wrappedFirst[0] || "";

        // if (prod.codigoNumerico){
        //     codigos.push(prod.codigoNumerico);
        // } else if (prod.claves){
        //     codigos.push(prod.claves);
        // }

        // ---- FIRST LINE ----
        lines.push(
            padLeft(qty, qtyWidth - 1) + " " +
            padRight(firstLine, descFirstMax) +
            padLeft(price, priceWidth)
        );

        // ---- OVERFLOW LINES (FULL WIDTH) ----
        if (printOverflow && desc.length > firstLine.length) {  
            const rest = desc.slice(firstLine.length).trim();
            const overflow = wrapByWords(rest, FULL_LINE_CHARS);
            overflow.forEach(line => lines.push(line));
        }

    });
    // let codigosLines = [];
    // if (codigos.length>0){
    //     const overflowCodigos = wrapByWords(codigos.join(","), FULL_LINE_CHARS);
    //     overflowCodigos.forEach(line => codigosLines.push(line));
    // }
    return lines; //codigosLines
}

// function extractTicketText(ticketInner) {
//   const lines = [];
//   const ticketHeader = ticketInner.querySelector("#ticketHeader")?.innerText.trim();
//   const ticketDatetime = ticketInner.querySelector("#ticketDatetime")?.innerText.trim();
//   const ticketProductos = ticketInner.querySelector("#ticketProductos")?.innerText;
//   const ticketTotal = ticketInner.querySelector("#ticketTotal")?.innerText.trim();
//   if (ticketHeader) lines.push(centerLine(ticketHeader, FULL_LINE_CHARS));
//   if (ticketDatetime) lines.push(centerLine(ticketDatetime, FULL_LINE_CHARS));
//   //lines.push(""); // spacing
//   if (ticketProductos) {
//     ticketProductos.split("\n").forEach(l => lines.push(l));
//   }
//   //lines.push(""); // spacing
//   if (ticketTotal) lines.push(rightAlignLine(ticketTotal, FULL_LINE_CHARS));

//   return lines;
// }

function descExistencia(producto){
    if (producto.tipoVentaId==-1){
        return parseSmartNumber(producto.existenciaUnidades)+" "+producto.unidadInv+"s";
    } else if (producto.tipoVentaId==-2){
        return parseSmartNumber(producto.existenciaPaquetes)+" paquetes";
    } else if (producto.tipoVentaId==-3){
        return parseSmartNumber(producto.existenciaKgs)+" kilos";
    }
    return "";
}

function extractTicketText(ticketInner) {
  console.log("extractTicketText");
  const lines = [];

  /* ───── HEADER (ONCE) ───── */
  const header = ticketInner.querySelector("#ticketHeader")?.innerText;
  if (header) {
    let headerLines = header.split(/\r?\n/);
    headerLines.forEach(line => {
        lines.push(centerLine(line, FULL_LINE_CHARS));
    });
    //lines.push(""); // spacing after header
  }

  /* ───── ITERATE BLOCKS IN ORDER ───── */
  const children = Array.from(ticketInner.children);

  for (let i = 0; i < children.length; i++) {
    const el = children[i];

    /* DATE */
    if (el.classList.contains("ticketDatetime")) {
      const dateText = el.innerText;
      let dateTextLines = dateText.split(/\r?\n/);
      dateTextLines.forEach(line => {
        lines.push(centerLine(line, FULL_LINE_CHARS));
      });
    }

      if (el.classList.contains("ticketProdTitle")) {
        const ticketProdTitleText = el.innerText;
        let ticketProdTitleTextLines = ticketProdTitleText.split(/\r?\n/);
        ticketProdTitleTextLines.forEach(line => {
            lines.push(centerLine(line, FULL_LINE_CHARS));
        });
      }

      /* PRODUCTS (next sibling) */
      //const productosEl = children[i + 1];
      //if (productosEl?.classList.contains("ticketProductos")) {
      if (el?.classList.contains("ticketProductos")) {
        el.innerText
          .split("\n")
          .map(l => l.trim())
          .filter(Boolean)
          .forEach(l => lines.push(l));
        //i++;
      }

      /* TOTAL (next sibling) */
      const totalEl = children[i + 1];
      //if (totalEl?.classList.contains("ticketTotal")) {
      if (el?.classList.contains("ticketTotal")) {
        const totalText = el.innerText;
        let totalTextLines = totalText.split(/\r?\n/);
        totalTextLines.forEach(line => {
            lines.push(line);
        });
      }
      //lines.push(""); // spacing between sales
    }

  const ticketSummary = ticketInner.querySelector(".ticketSummary")?.innerText;
  if (ticketSummary) {
    let ticketSummaryLines = ticketSummary.split(/\r?\n/);
    ticketSummaryLines.forEach(line => {
        lines.push(centerLine(line, FULL_LINE_CHARS));
    });
    //lines.push(""); // spacing after header
  }

  const ticketFooter = ticketInner.querySelector(".ticketFooter")?.innerText;
  if (ticketFooter) {
    let ticketFooterLines = ticketFooter.split(/\r?\n/);
    ticketFooterLines.forEach(line => {
        lines.push(centerLine(line, FULL_LINE_CHARS));
    });
    //lines.push(""); // spacing after header
  }
  return lines;
}

async function printTicketEscPos(ticketInner) {
  const lines = extractTicketText(ticketInner);
  console.log(lines);
  if (!window.thisRol || (window.thisRol && window.thisRol=="maestro")){
    await fetch("/print/ticket", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lines })
    });
  }
  if (window.thisRol && window.thisRol=="esclavo"){
    await fetch("/print/ticketEsclavo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lines })
    });
  }
}

async function openTicketModal(productos){
    console.log("openTicketModal")
    document.getElementById("ticketModal")?.remove();
    const ticketModal = document.createElement("div");
    ticketModal.classList.add("ticketModal");
    ticketModal.setAttribute("id","ticketModal");

    const ticketModalContent = document.createElement("div");
    ticketModalContent.classList.add("ticketModal-content");

    const ticketModalControls = document.createElement("div");
    ticketModalControls.classList.add("ticketModal-controls");
    const btnCerrarModal = document.createElement("button");
    btnCerrarModal.textContent="Cerrar";
    btnCerrarModal.style.fontSize="18px";
    btnCerrarModal.style.backgroundColor="orange";

    btnCerrarModal.addEventListener("click", function(){
        closeModal();
    })

    ticketModalControls.append(btnCerrarModal);

    /* body (scrollable) */
    const ticketBody = document.createElement("div");
    ticketBody.className = "ticketModal-body";

    const previewWrapper = document.createElement("div");
    previewWrapper.className = "ticketPreviewWrapper";

    const ticket = await generateTicket(productos);
    previewWrapper.append(ticket);
    ticketBody.append(previewWrapper);
    ticketModalContent.append(ticketModalControls, ticketBody);


    //ticketModalContent.append(ticketPreview);
    ticketModal.append(ticketModalContent);
    document.body.prepend(ticketModal);
    // ticketModal.style.display = "flex";
    // // 🔑 wait for layout
    requestAnimationFrame(() => {
        const w = ticketModalContent.scrollWidth;
        const h = ticketModalContent.scrollHeight;
        ticketModalContent.style.width  = (w * 1.2) + "px";
        ticketModalContent.style.height = (h * 1.2) + "px";
    });
    const styles = getComputedStyle(ticketModalContent);
    const w = parseFloat(styles.width);
    const h = parseFloat(styles.height);
    ticketModalContent.style.width  = (w * 1.5) + "px";
    //ticketModalContent.style.height = (h * 1.5) + "px";
}

function closeModal() {
  document.getElementById("ticketModal").style.display = "none";
  document.getElementById("ticketModal")?.remove();
}


async function creaImagenTruper(codigoNumerico) {
    return new Promise((resolve) => {

        if (!codigoNumerico) {
            resolve("");
            return;
        }

        let imgProd = document.createElement("img");

        imgProd.onload = function () {
            imgProd.style.width = "150px";
            imgProd.style.height = "150px";
            imgProd.alt = "Sin imagen";
            resolve(imgProd);
        };

        imgProd.onerror = function () {
            //resolve(imgProd.src);
        };

        imgProd.src = `/static/imagenes/truper/truper_${codigoNumerico}.jpg`;
    });
}

function openInWorkspace(route, label, addSequence=true) {
    const target = window.parent !== window ? window.parent : window;
    target.parent.postMessage({
        type: "OPEN_ADHOC_VIEW",
        payload: {
            groupId: "external",   // any logical group you want
            route: route,
            label: label,
            addSequence: addSequence
        }
    }, "*");
}

