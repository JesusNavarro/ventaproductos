// main.js

window.SCAN_DELAY = 2000;
window.scanningEnabled = true;

let barcodeBuffer = "";
let lastKeyTime = Date.now();

document.addEventListener("DOMContentLoaded", async () => {

  //logDebug("context.APP_DEVICE: "+context.APP_DEVICE);

  const device = (typeof context.APP_DEVICE !== "undefined" && context.APP_DEVICE) || 
             (/Android/i.test(navigator.userAgent) ? "Tablet" : "Mac");

  // if (device=== "Tablet") {
  //   let zoom_value = 1.5;
  //   document.body.style.zoom = zoom_value;
  //   const link = document.getElementById("ventasLink");
  //   link.href = "/ventas/ventas_viewer.html?dias=7&zoom=" + zoom_value;
  // }
  
  //const APP_DEVICE = "{{ app_device }}" || (/Android/i.test(navigator.userAgent) ? "Tablet" : "Mac");

  const btnEscanear = document.getElementById("btn-escanear");
  const btnGuardar = document.getElementById("btn-guardar");
  const divScanner = document.getElementById("scanner");
  const estado = document.getElementById("estado");
  const mensaje = document.getElementById("mensaje");
  let tabla = document.querySelector("#tabla-productos");
  let tabla_tbody = document.querySelector("#tabla-productos tbody");
  let tabla_thead = document.querySelector("#thead");
  let tabla_tfoot = document.querySelector("#tfoot");
  const total = document.getElementById("total");
  const debugDiv = document.getElementById("debug");
  const toggleBtn = document.getElementById("toggleBtn");
  let mostrarCeldasOcultas = true;


  const valoresMenoresUno = [0.1, 0.2, 0.25, 0.3, 0.333, 0.4, 0.5, 0.6, 0.666, 0.7, 0.75, 0.8, 0.9];

  // Controles de la tabla de productos

  const btn_toggle_columnas = document.getElementById("btn-toggle-columnas");
  const btn_eliminar_venta = document.getElementById("btn-eliminar-venta");

  if (context.AMBIENTE==="Dev"){
      debugDiv.style.display="block";
  }

  // --- Show/hide "Guardar Venta" button dynamically ---
  function updateGuardarButtonVisibility() {
    if (productosVenta.length > 0) {
      btnGuardar.style.display = "block";
      btn_toggle_columnas.style.display = "block";
      btn_eliminar_venta.style.display = "block";
    } else {
      btnGuardar.style.display = "none";
      btn_toggle_columnas.style.display = "none";
      btn_eliminar_venta.style.display = "none";
    }
  }

  let productosVenta = [];
  //let scanner;
  logDebug('device', device);
  logDebug('context.app_device', context.APP_DEVICE);


  /* Si las camaras estan encendidas creamos su logic */

  if (context.CAMERAS_ON){

      btnEscanear.style.display = "block";
      estado.style.display = "block";

      if (device === "Tablet") {
          // ✅ Load ZXing dynamically only for tablet
          logDebug('Camara JS', 'Tablet');
          //await loadScript("/static/js/zxing.min.js"); /// THIS FOR XZING
          await loadScript("/static/js/html5-qrcode.min.js");
          // Then dynamically import the TabletScanner module
          //const module = await import("/static/js/tablet_scanner.js");
          //ScannerModule = module.TabletScanner;
              //scanner = TabletScanner(divScanner, estado, onBarcodeDetected, logDebug);
          toggleBtn.style.display = "block";

                      // Toggle front/back dynamically
          toggleBtn.addEventListener("click", () => {
              logDebug('Click on ', 'toggleBtn');
              let newCameraType = toggleBtn.innerText;
              logDebug('To start new camera', newCameraType);
              if (scanner.isActive()) {
                  scanner.stop().then(() => {
                      //if (newCameraType) 
                      scanner.start(newCameraType);
                  });
              } else {
                  //if (newCameraType) 
                  scanner.start(newCameraType);
              }
              toggleBtn.innerText = newCameraType === "back" ? "front" : "back";
              logDebug('Changed button to ', toggleBtn.innerText);
          });

      } else if (device === "Mac"){
          // ✅ Load Html5Qrcode dynamically only for Mac
          logDebug('Camara JS', 'Mac');
          await loadScript("/static/js/html5-qrcode.min.js");
          // Then dynamically import the MacScanner module
          //const module = await import("/static/js/mac_scanner.js");
          //ScannerModule = module.MacScanner;
              //scanner = MacScanner(divScanner, estado, onBarcodeDetected, logDebug);
      }

      let ScannerModule = null;

      let scannerFn = null;

      // Debugging Loading JS as modules
      try {
        const modulePath =
          device === "Tablet"
            ? "/static/js/tablet_scanner.js"
            : "/static/js/mac_scanner.js";

        logDebug("[DEBUG] Importing scanner module from", modulePath);
        ScannerModule = await import(modulePath);
        logDebug("[DEBUG] ScannerModule loaded:", ScannerModule);

        scannerFn =
          device === "Tablet"
            ? ScannerModule.TabletScanner
            : ScannerModule.MacScanner;
        //logDebug("[DEBUG] Selected scanner function:", scannerFn);

        if (typeof scannerFn !== "function") {
          logDebug("❌ ScannerFn is not a function. Module:", ScannerModule);
        }
      } catch (err) {
        logDebug("❌ Failed to import scanner module:", err);
      }

       // Now create and use your scanner safely
      const scanner = scannerFn(
        document.getElementById("scanner"),
        document.getElementById("estado"),
        onBarcodeDetected, // callback for barcode results
        logDebug,               // callback for internal logging
        btnEscanear
        );

      btnEscanear.addEventListener("click", () => {
          if (scanner.isActive()) scanner.stop();
          else scanner.start(toggleBtn.innerText === "back" ? "front" : "back");
      });

                     // --- Common scanning callback ---
      function onBarcodeDetected(barCode) {
          playScanBeep();
          buscarProducto(barCode);
          scanner.resetTimer();
          logDebug("Barcode detected", barCode);
      }

  }

  function logDebug(label, data) {
    if (context.AMBIENTE==="Dev"){
      try {
          if (debugDiv) {
            const pretty = typeof data === "object" ? JSON.stringify(data, null, 2) : data;
            debugDiv.innerText += `[DEBUG] ${label}: ${pretty}\n`;
            debugDiv.scrollTop = debugDiv.scrollHeight;
          }
      } catch {
        debugDiv.innerText += `[DEBUG] ${label}: (unprintable)\n`;
      }
    }
  }

  // --- Audio feedback ---
  function playScanBeep() {
      try {
          navigator.vibrate?.(100); // vibrate for 100ms
          const ctx = new (window.AudioContext || window.webkitAudioContext)();
          const o = ctx.createOscillator();
          const g = ctx.createGain();
          o.type = "sine";
          o.frequency.setValueAtTime(1000, ctx.currentTime);
          g.gain.setValueAtTime(0.5, ctx.currentTime);
          o.connect(g);
          g.connect(ctx.destination);
          o.start();
          o.stop(ctx.currentTime + 0.15);
      } catch (e) {}
  }

  function playSuccessSound() {
      try {
          logDebug("playSuccessSound", "inside")
          navigator.vibrate?.(100); // vibrate for 100ms
          const ctx = new (window.AudioContext || window.webkitAudioContext)();
          const g = new GainNode(ctx, { gain: 0.5 });
          g.connect(ctx.destination);
          [600, 800, 1000].forEach((f, i) => {
              const o = ctx.createOscillator();
              o.type = "triangle";
              o.frequency.setValueAtTime(f, ctx.currentTime);
              o.connect(g);
              o.start(ctx.currentTime + i * 0.05);
              o.stop(ctx.currentTime + 1);
          });
      } catch (e) {}
  }

  function playErrorSound() {
      try {
          const ctx = new (window.AudioContext || window.webkitAudioContext)();
          const o = ctx.createOscillator();
          const g = new GainNode(ctx, { gain: 0.5 });
          o.connect(g);
          g.connect(ctx.destination);
          o.start();
          o.stop(ctx.currentTime + 0.2);
      } catch (e) {}
  }

  btnGuardar.addEventListener("click", guardarVenta);

  // --- Product lookup and table logic ---
  function buscarProducto(barCode) {
      logDebug("Dentro de buscarProducto: ", barCode);
      fetch("/buscar_producto", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ barcode: barCode })
      })
          .then(res => res.json())
          .then(data => {
              if (data.estado === "exito") {
                  let precioStr = data.producto.Precio;  // e.g. "185" or "$185.00"
                  // Remove anything that is not a digit or a dot
                  let precioNum = parseFloat(precioStr.replace(/[^0-9.]/g, ''));
                  console.log(precioNum);  // 185
                  agregarProducto({
                      barCode: data.producto.CodigoBarras,
                      Descripcion: data.producto.Descripcion,
                      Precio: precioNum,
                      cantidad: 1,
                      encontrado: true
                  });
                  mensaje.innerHTML = ``;
                  actualizarTotales();
              } else {
                  mensaje.innerHTML = `${barCode} Producto no encontrado`;
              }
          })
          .catch(err => {
              mensaje.innerHTML = "Error al comunicarse con el servidor";
              logDebug( "Error al comunicarse con el servidor: "+err);
              console.error(err);
          });
  }

  // function agregarProducto(prod) {
  //     const existente = productosVenta.find(p => p.barCode === prod.barCode);
  //     if (existente) existente.cantidad += 1;
  //     else productosVenta.push(prod);
  //     actualizarTabla();
  // }

  // function actualizarTabla() {
  //     tabla.innerHTML = "";
  //     let totalVenta = 0;
  //     productosVenta.forEach(p => {
  //         const precio = parseFloat(p.Precio) || 0;
  //         const subtotal = p.encontrado ? precio * p.cantidad : 0;
  //         if (p.encontrado) totalVenta += subtotal;
  //         const fila = document.createElement("tr");
  //         fila.innerHTML = `
  //             <td>${p.barCode}</td>
  //             <td width="100%">${p.Descripcion}</td>
  //             <td><img src="static/imagenes/pieza_icon.jpg" width="20" height="20" alt="Pieza"/><img src="static/imagenes/paquete_icon.jpg" width="20" height="20" alt="Paquete"/></td>
  //             <td><input type="number" min="1" value="${p.cantidad}" onchange="window.cambiarCantidad('${p.barCode}', this.value)" ${p.encontrado ? "" : "disabled"} style="width:50px;"/></td>
  //             <td><img src="static/imagenes/up_icon.jpg" width="20" height="20" alt="Uno más"/></td>
  //             <td><img src="static/imagenes/down_icon.jpg" width="20" height="20" alt="Uno menos"/></td>
  //             <td><img src="static/imagenes/borrar_icon.jpg" width="20" height="20" alt="Borrar"/></td>
  //             <td class="celda_ocultable">${p.encontrado ? precio.toFixed(2) : "-"}</td>
  //             <td class="celda_ocultable"><input type="number" value="${precio.toFixed(2)}" onchange="window.cambiarPrecio('${p.barCode}', this.value)" style="width:100px;"/></td>
  //             <td class="celda_ocultable"><img src="static/imagenes/plus_icon.jpg" width="20" height="20" alt="Uno más"/></td>
  //             <td class="celda_ocultable"><img src="static/imagenes/minus_icon.jpg" width="20" height="20" alt="Uno menos"/></td>
  //             <td class="celda_ocultable">${p.encontrado ? subtotal.toFixed(2) : "-"}</td>`;
  //         tabla.appendChild(fila);
  //     });
  //     total.innerText = totalVenta.toFixed(2);
  //     updateGuardarButtonVisibility();
  // }

    function agregarProducto(prod) {
      const existente = productosVenta.find(p => p.barCode === prod.barCode);
      if (existente) {
        existente.cantidad += 1;
        // Just update quantity cell visually
        const filaExistente = tabla_tbody.querySelector(`tr[data-barcode="${prod.barCode}"]`);
        if (filaExistente) {
          const cantidadInput = filaExistente.querySelector(".cantidad-input");
          if (cantidadInput) {
            cantidadInput.value = existente.cantidad;
          }
        }
        actualizarTotales();
        return;
      }

      prod.PrecioVenta = prod.Precio;
      // Add new product object
      productosVenta.push(prod);

      // Create a new row (not rebuilding the whole table)
      const fila = document.createElement("tr");
      fila.dataset.barcode = prod.barCode;

      const precio = parseFloat(prod.Precio) || 0;
      const subtotal = prod.encontrado ? precio * prod.cantidad : 0;

      fila.innerHTML = `
        <td style="width: 1%;"><img src="static/imagenes/borrar_icon.jpg" class="borrar-btn" width="20" height="20" alt="Borrar"/></td>
        <td style="width:auto%;">${prod.Descripcion}</td>
        <!--td style="width: 1%;"-->
          <!--img src="static/imagenes/pieza_icon.jpg" width="20" height="20" alt="Pieza"/-->
          <!--img src="static/imagenes/paquete_icon.jpg" width="20" height="20" alt="Paquete"/-->
        <!--/td-->
        <td style="width: 1%;"><input type="number" min="0" value="${prod.cantidad}" class="cantidad-input"
            onchange="window.cambiarCantidad('${prod.barCode}', this)" style="width:80px;font-weight:bold;"/>
        </td>
        <td style="width: 1%;">
          <img src="static/imagenes/up_icon.jpg" class="arrow-up" width="20" height="20" alt="Uno más"/>
        </td>
        <td style="width: 1%;">
          <img src="static/imagenes/down_icon.jpg" class="arrow-down" width="20" height="20" alt="Uno menos"/>
        </td>
        <!--td class="celda_ocultable" style="width: 1%;">${precio.toFixed(2)}</td-->
        <td class="celda_ocultable" style="width: 1%;">
          <input type="number" value="${precio.toFixed(2)}" placeholder="${precio.toFixed(2)}" class="precio-input" min="0"
            onchange="window.cambiarPrecio('${prod.barCode}', this)" style="width:80px;font-weight:bold;"/>
        </td>
        <td class="celda_ocultable" style="width: 1%;">
          <img src="static/imagenes/plus_icon.jpg" class="plus-btn" width="20" height="20" alt="Subir precio"/>
        </td>
        <td class="celda_ocultable" style="width: 1%;">
          <img src="static/imagenes/minus_icon.jpg" class="minus-btn" width="20" height="20" alt="Bajar precio"/>
        </td>
        <td class="celda_ocultable subtotal-cell" style="width: 1%;">${subtotal.toFixed(2)}</td>
      `;

      tabla_tbody.appendChild(fila);
      tabla_thead.style.display="block";
      tabla_tfoot.style.display="block";

      // Initialize image controls on this new row
      inicializarControlesFila(fila);

      actualizarTotales();
      updateGuardarButtonVisibility();
    }

  // function actualizarTabla() {
  //   // Kept for compatibility with any other calls in your code
  //   // but now it just refreshes totals (no full rebuild)
  //   actualizarTotales();
  // }
  
  window.cambiarCantidad = function (barCode, cantidadInput) {
      logDebug("cantidadInput", cantidadInput);
      let nuevaCantidad = parseFloat(cantidadInput.value) || 0;
      if (nuevaCantidad<0.1){
        nuevaCantidad=0.1;
        cantidadInput.value=nuevaCantidad;
      }
      const prod = productosVenta.find(p => p.barCode === barCode);
      if (prod && prod.encontrado) {
        prod.cantidad = parseFloat(nuevaCantidad) || 1;
        actualizarTotales();
        //toggleColumnas(mostrarCeldasOcultas);
      }
  };

  window.cambiarPrecio = function (barCode, precioInput) {
      const prod = productosVenta.find(p => p.barCode === barCode);
      if (prod && prod.encontrado) {
          let nuevoPrecio = parseFloat(precioInput.value) || 1;
          prod.PrecioVenta = nuevoPrecio;
          if (nuevoPrecio==prod.Precio){
            precioInput.style.color="black";
            precioInput.style.backgroundColor="#ffffff";
          } else if (nuevoPrecio<prod.Precio){
            precioInput.style.color="red";
            precioInput.style.backgroundColor="#ffffe0";
          } else {
            precioInput.style.color="green";
            precioInput.style.backgroundColor="#ffffe0";
          }
          actualizarTotales();
          //toggleColumnas(mostrarCeldasOcultas);
      }
  };

  function guardarVenta() {
      const ventasAguardar = productosVenta
          .filter(p => p.encontrado)
          .map(p => ({
              CodigoBarras: p.barCode,
              Descripcion: p.Descripcion,
              PrecioSistema: p.Precio,
              PrecioVenta: p.PrecioVenta,
              Cantidad: p.cantidad,
              Subtotal: (p.PrecioVenta * p.cantidad).toFixed(2)
          }));

      if (ventasAguardar.length === 0) {
          mensaje.innerHTML = "No hay productos válidos para guardar.";
          playErrorSound();
          return;
      }

      fetch("/guardar_venta", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ venta: ventasAguardar })
      })
          .then(res => res.json())
          .then(data => {
              if (data.estado === "exito") {
                  mensaje.innerHTML= `<font color="green">✅ Venta guardada correctamente <font size="5">$ ${data.total_venta}</font></font>`;
                  playSuccessSound();
                  eliminarVenta();
              } else {
                  mensaje.innerHTML = `❌ Error al guardar: ${data.mensaje}`;
                  playErrorSound();
              }
          })
          .catch(err => {
              mensaje.innerHTML = "⚠️ Error al guardar venta";
              playErrorSound();
          });
  }

  // Helper: dynamically load script
  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  /**************************************************/
  /*** LOGICA PARA EL SCANNER DE CODIGO DE BARRAS ***/

  document.addEventListener("keydown", (e) => {
      const now = Date.now();
      const timeDiff = now - lastKeyTime;

      if (timeDiff > 100) {
          barcodeBuffer = "";
      }

      if (e.key.length === 1) {
          barcodeBuffer += e.key;
      } else if (e.key === "Enter") {
          if (barcodeBuffer.length >= 4) {
              logDebug("📦 SCAN Detected barcode:", barcodeBuffer);

              // Call your existing scanner callback
              if (typeof buscarProducto === "function") {
                  buscarProducto(barcodeBuffer);
              }

              e.preventDefault();
          }
          barcodeBuffer = "";
      }

      lastKeyTime = now;
  });

  /**************************************************/
  /**************************************************/
  // === 👇 FUNCIONALIDAD DE TABLA PRODUCTOS 👇 ===
  /**************************************************/

  let celdasOculatbles = document.querySelectorAll(".celda_ocultable");
  celdasOculatbles.forEach(celda => celda.style.display = "none");
  const totalRow = tabla_tfoot.querySelector("tr");

  btn_toggle_columnas.addEventListener("click", () => {
              logDebug('Click on ', 'btn_toggle_columnas');
              toggleColumnas();
              
  });

  btn_eliminar_venta.addEventListener("click", () => {
    logDebug('Click on ', 'btn_eliminar_venta');
    eliminarVenta();
              
  });

  // ---------- Toggle hideable columns ----------
  function toggleColumnas(isHidden) {
    celdasOculatbles = document.querySelectorAll(".celda_ocultable");
    //logDebug("celdasOculatbles", celdasOculatbles); 
    logDebug("arg isHidden", isHidden)
    if (isHidden=== undefined){
      isHidden = Array.from(celdasOculatbles).some(c => c.style.display === "none");
    }
    mostrarCeldasOcultas = isHidden; 
    logDebug("isHidden", isHidden);
    celdasOculatbles.forEach(
      celda => celda.style.display = isHidden ? "table-cell" : "none");
    if (totalRow) totalRow.style.display = isHidden ? "table-row" : "none";
  }

  function eliminarVenta() {
    logDebug("eliminarVenta", "eliminarVenta");
    productosVenta = [];
    if (tabla_tbody) {
        tabla_tbody.innerHTML = ""; // removes only the product rows
    }
    actualizarTotales();
    actualizarVisibilidadBotones();
    mostrarCeldasOcultas = true;
  }



  // ---------- Button visibility toggle ----------
  function actualizarVisibilidadBotones() {
    let tieneProductos = tabla_tbody && tabla_tbody.querySelectorAll("tr").length > 0;
    logDebug("tieneProductos", tieneProductos);
    //console.log("tieneProductos"+tieneProductos);
    btnGuardar.style.display = tieneProductos ? "inline-block" : "none";
    btn_toggle_columnas.style.display = tieneProductos ? "inline-block" : "none";
    btn_eliminar_venta.style.display = tieneProductos ? "inline-block" : "none";
    logDebug("to check", "thead");
    tabla_thead.style.display= tieneProductos ? "" : "none";
    logDebug("to check", "tfoot");
    tabla_tfoot.style.display= tieneProductos ? "" : "none";
    toggleColumnas(mostrarCeldasOcultas);
  }

  // ---------- Update totals (wrapper) ----------
  function actualizarTotales() {
    const totalCell = document.getElementById("total");
    if (!tabla_tbody|| !totalCell) return;

    let total = 0;
    tabla_tbody.querySelectorAll("tr").forEach(row => {
      const cantidad = parseFloat(row.querySelector(".cantidad-input")?.value || 0);
      const precio = parseFloat(row.querySelector(".precio-input")?.value || 0);
      const subtotalCell = row.querySelector(".subtotal-cell");
      const subtotal = cantidad * precio;
      if (subtotalCell) subtotalCell.textContent = subtotal.toFixed(2);
      total += subtotal;
    });
    totalCell.textContent = total.toFixed(2);
    actualizarVisibilidadBotones();
  }

  // ---------- Attach image behavior after product added ----------
  function inicializarControlesFila(row) {
    const cantidadInput = row.querySelector(".cantidad-input");
    const precioInput = row.querySelector(".precio-input");
    const borrarBtn = row.querySelector(".borrar-btn");
    const codigo = row.dataset.barcode;

    // Quantity arrows
    const upArrow = row.querySelector(".arrow-up");
    const downArrow = row.querySelector(".arrow-down");

    // update the array when the user types or changes the input manually
    cantidadInput.addEventListener("input", () => {
      const producto = productosVenta.find(p => p.barCode === codigo);
      if (producto) producto.cantidad = parseFloat(cantidadInput.value) || 1;
      actualizarTotales();
    });

    precioInput.addEventListener("input", () => {
      const producto = productosVenta.find(p => p.barCode === codigo);
      if (producto) producto.precio = parseFloat(precioInput.value) || 1;
      actualizarTotales();
    });

    if (upArrow && cantidadInput) {
      upArrow.addEventListener("click", () => {
        let val = parseFloat(cantidadInput.value) || 0;
        if (val < 1) {
          // Find the next value in the array greater than current
          const siguiente = valoresMenoresUno.find(v => v > val);
          val = siguiente !== undefined ? siguiente : 1; // jump to 1 if already at the top
        } else {
          val += 1;
        }
        // Ensure minimum of 0.1
        if (val < 0.1) val = 0.1;
        // } else {
        //   const val = Math.max(1, parseFloat(cantidadInput.value) + 1);
        // }
        cantidadInput.value = val;
        const producto = productosVenta.find(p => p.barCode === codigo);
        if (producto) producto.cantidad = val;
        actualizarTotales();
      });
    }
    if (downArrow && cantidadInput) {
      downArrow.addEventListener("click", () => {
        let val = parseFloat(cantidadInput.value) || 0;
        if (val <= 1) {
          // Find the next value in the array greater than current
          logDebug("valoresMenoresUno", valoresMenoresUno);
          let valoresMenoresUnoR = valoresMenoresUno.slice();
          valoresMenoresUnoR.reverse();
          logDebug("Reversed", valoresMenoresUnoR);
          logDebug("valoresMenoresUno", valoresMenoresUno);
          const siguiente = (valoresMenoresUnoR).find(v => v < val);
          val = siguiente !== undefined ? siguiente : 0.1; // jump to 1 if already at the top
        } else {
          val -= 1;
        }
        // Ensure minimum of 0.1
        if (val < 0.1) val = 0.1;
        // } else {
        //   const val = Math.max(1, parseFloat(cantidadInput.value) + 1);
        // }
        cantidadInput.value = val;
        const producto = productosVenta.find(p => p.barCode === codigo);
        if (producto) producto.cantidad = val;
        actualizarTotales();
      });
    }

    // Price plus/minus
    const plusBtn = row.querySelector(".plus-btn");
    const minusBtn = row.querySelector(".minus-btn");

    if (plusBtn && precioInput) {
      plusBtn.addEventListener("click", () => {
        const val = Math.max(1, parseFloat(precioInput.value) + 1);
        precioInput.value = val;
        const producto = productosVenta.find(p => p.barCode === codigo);
        if (producto) {
          producto.PrecioVenta = val;
          if (producto.Precio==val){
            precioInput.style.color = "black";
            precioInput.style.backgroundColor="#ffffff";
          } else if (producto.Precio>val){
            precioInput.style.color = "red";
            precioInput.style.backgroundColor="#ffffe0";
          } else {
            precioInput.style.color = "green";
            precioInput.style.backgroundColor="#ffffe0";
          }
        }
        actualizarTotales();
      });
    }
    if (minusBtn && precioInput) {
      minusBtn.addEventListener("click", () => {
        const val = Math.max(1, parseFloat(precioInput.value) - 1);
        precioInput.value = val;
        const producto = productosVenta.find(p => p.barCode === codigo);
        if (producto) {
          producto.PrecioVenta = val;
          if (producto.Precio==val){
            precioInput.style.color = "black";
            precioInput.style.backgroundColor="#ffffff";
          } else if (producto.Precio>val){
            precioInput.style.color = "red";
            precioInput.style.backgroundColor="#ffffe0";
          } else {
            precioInput.style.color = "green";
            precioInput.style.backgroundColor="#ffffe0";
          }
        }
        actualizarTotales();
      });
    }

    // // Borrar row
    // if (borrarBtn) {
    //   borrarBtn.addEventListener("click", () => {
    //     row.remove();
    //     actualizarTotales();
    //   });
    // }

    borrarBtn.addEventListener("click", () => {
      // Find the code or ID for the product in this row
      const codigo = row.dataset.barcode;

      // Remove the product from productosVenta (assuming productosVenta is an array of objects with .codigo)
      if (codigo) {
        const index = productosVenta.findIndex(p => p.barCode === codigo);
        if (index !== -1) {
          productosVenta.splice(index, 1);
          // Remove the row from the DOM
          row.remove();
        }
      }

      // If there are no products left, clean the table and hide buttons
      if (productosVenta.length === 0) {
        eliminarVenta();
      } else {
        // Otherwise just update totals normally
        actualizarTotales();
      }
    });

  } // inicializarControlesFila(row)

  actualizarVisibilidadBotones();

    /**** TERMINA DE CARGAR EL DOM ****/
});


