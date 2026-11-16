// main.js

//const { createElement } = require("react");

//const { createElement } = require("react");

if (configDev && configDev.MS_SOY){
    window.thisRol = configDev.MS_SOY.rol;
}

document.addEventListener("DOMContentLoaded", async () => {

    tbodyBusqueda = document.getElementById("buscadorProducto");

    function crearProductoComun({ descripcion, cantidad, precio }) {
        const candidatos = productosVenta.filter(p => p.tipoVentaId === -4);
        const minProducto = candidatos.length
        ? candidatos.reduce((min, p) =>
            p.productoId < min.productoId ? p : min
            )
        : null;
        let productoId=-1;
        if (minProducto){
            productoId = minProducto.productoId-1;
        }
        if (descripcion=='Articulo Comun'){
            descripcion = descripcion+' '+Math.abs(productoId);
        }
        return {
            productoId: productoId,
            tipoVentaId: -4,

            // Unique internal identifier (so rows are independent)
            comunId: crypto.randomUUID(),
            descripcion: descripcion,
            descVenta: "artículo",
            cantidad: cantidad,
            precio: precio,
            precioVenta: precio,

            encontrado: true,

            // Inventory-related defaults
            existencia: 0,
            minimo: 0,
            descExistencia: "",

            // Venta behavior
            muestraUnidad: false,
            muestraPaquete: false,
            muestraKg: false,

            // Metadata
            proveedor: "",
            codigoBarras: "",
            codigoNumerico: "",
            claves: "",
            // Device
            dispositivoId: configDev?.MS_SOY?.dispositivoId ?? null,
            extraInfo: descripcion
        };
    }

    function setFormatoTableta(fila){
        if (window.thisRol=='esclavo'){
            let cantidad = fila.querySelector(".cantidad-input");
            cantidad.style.fontSize = '20px';
            let codigo = fila.querySelector(".codigo-numerico");
            codigo.style.fontSize = '23px';
            let precio = fila.querySelector(".precio-input");
            precio.style.fontSize = '20px';
        }
    }

    function agregaProductoComun(productoId, desc, cantidad, precio) {
        const producto = crearProductoComun({
            descripcion: desc,
            cantidad: Number(cantidad) || 1,
            precio: Number(precio) || 0
        });

        // Add to sale list (no deduplication)
        productosVenta.unshift(producto);

        // Create row
        const fila = document.createElement("tr");
        fila.dataset.productoId = producto.productoId;       // -1
        fila.dataset.tipoVentaId = producto.tipoVentaId;     // -1
        fila.dataset.comunId = producto.comunId;              // 🔑 unique

        fila.innerHTML = setFilaProdHTML(producto);
        setFormatoTableta(fila);
        tabla_tbody.prepend(fila);
        

        updateGuardarButtonVisibility();
        mensaje.innerHTML = ``;
        fila.focus();
        actualizarTotales();
    }

    creaBuscadorProducto(tbodyBusqueda, productoEncontrado, true, agregaProductoComun, true);

    const btnGuardar = document.getElementById("btn-guardar");
    const btnImprimir = document.getElementById("btn-imprimir");
    const btnSinInventario = document.getElementById("btn-sinInventario");
    const mensaje = document.getElementById("mensaje");
    let tabla = document.querySelector("#tabla-productos");
    let tabla_tbody = document.querySelector("#tabla-productos tbody");
    let tabla_thead = document.querySelector("#thead");
    let tabla_tfoot = document.querySelector("#tfoot");
    const total = document.getElementById("total");
    const debugDiv = document.getElementById("debug");

    let mostrarCeldasOcultas = true;

    const valoresMenoresUno = [0.1, 0.2, 0.25, 0.3, 0.333, 0.4, 0.5, 0.6, 0.666, 0.7, 0.75, 0.8, 0.9];

    // Controles de la tabla de productos

    const btn_toggle_columnas = document.getElementById("btn-toggle-columnas");
    const btn_eliminar_venta = document.getElementById("btn-eliminar-venta");

    // if (context.AMBIENTE === "Dev") {
    //     debugDiv.style.display = "block";
    // }

    // --- Show/hide "Guardar Venta" button dynamically ---
    function updateGuardarButtonVisibility() {
        if (productosVenta.length > 0) {
            if (window.thisRol=='maestro'){
                //btnSinInventario.style.display="block";
                //btn_toggle_columnas.style.display = "block";
                //btnImprimir.style.display="block";
            } else if (window.thisRol=='esclavo'){
                btnSinInventario.style.display="none";
                btn_toggle_columnas.style.display = "none";
                btnImprimir.style.display="none";
            }
            btnGuardar.style.display = "block";
            btn_eliminar_venta.style.display = "block";
        } else {
            btnGuardar.style.display = "none";
            btn_toggle_columnas.style.display = "none";
            btn_eliminar_venta.style.display = "none";
            btnImprimir.style.display="none";
            btnSinInventario.style.display="none";
        }
    }

    let productosVenta = [];

    // window.logDebug = function logDebug(label, data) {
    //     if (context.AMBIENTE === "Dev") {
    //         try {
    //             if (debugDiv) {
    //                 const pretty = typeof data === "object" ? JSON.stringify(data, null, 2) : data;
    //                 debugDiv.innerText += `[DEBUG] ${label}: ${pretty}\n`;
    //                 debugDiv.scrollTop = debugDiv.scrollHeight;
    //             }
    //         } catch {
    //             debugDiv.innerText += `[DEBUG] ${label}: (unprintable)\n`;
    //         }
    //     }
    // }

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
        } catch (e) { }
    }

    function splitParenTextSimple(str) {
        const open = str.indexOf("(");
        if (open === -1) {
            return { mainpart: str.trim(), extra: '' };
        }
        return {
            mainpart: str.slice(0, open).trim(),
            extra: str.slice(open + 1, str.lastIndexOf(")")).trim()
        };
    }

    btnGuardar.addEventListener("click", async function(){
        await guardarVenta();
    });

    btnSinInventario.addEventListener("click", async function(){
        if (!confirm(`¿Registrar venta SIN afectar el inventario?`)) return;
        await guardarVenta(1);
    });

    btnImprimir.addEventListener("click", function(){print()});

    async function productoEncontrado(producto, tipoVentaId, bypassSelectorVenta=false) {
        let precio = producto.precio;
        producto.precioVenta = precio;
        //producto.cantidad=1;
        producto.encontrado = true;
        let res = true;
        if (bypassSelectorVenta){
            producto.cantidad=1;
            const tiposVentaEnTabla = getTiposVentaEnTabla(producto.productoId);
            if (tiposVentaEnTabla.size === 0) {
                producto.tipoVentaId = producto.preferenciaVenta;
                agregarProducto(producto);
            } else if (tiposVentaEnTabla.size === 1) {
                producto.tipoVentaId = [...tiposVentaEnTabla][0];
                agregarProducto(producto);
            } else {
                // 🔔 ambiguous → let user pick
                res = await mostrarSelectorTipoVenta(producto, tipoVentaId??producto.preferenciaVenta);
            }
        } else {
            res = await mostrarSelectorTipoVenta(producto, tipoVentaId??producto.preferenciaVenta);
        }
        mensaje.innerHTML = ``;
        actualizarTotales();
        //playErrorSound();
        return res;
    }

    function resetInfoSelections(){
        document.querySelectorAll('.info-btn').forEach(b =>
            b.classList.remove('activeInfo')
        );
        const infoTH = document.getElementById("infoTH");
        infoTH.innerHTML='';
    }

    function redibujaTodasTipoVentas(prod){
        const trs = tabla_tbody.querySelectorAll(`tr[data-producto-id="${prod.productoId}"]`);
        trs.forEach(tr => {
            const tipoVentaId = tr.dataset.tipoVentaId;
            const prodFila = findProductoVenta(prod.productoId, tipoVentaId);
            //console.log(prodFila);
            const td = tr.querySelector("td.prodVentasCambiar");
            newHTML=dibujaTiposVentaCambiar(prodFila).innerHTML;
            //console.log(newHTML);
            td.innerHTML = newHTML;
            const btn = tr.querySelector('.info-btn');
            if (btn) btn.classList.remove('activeInfo');
        });
    }

    function generaImagenTipoVenta(prod, tipoVenta){
        //console.log(prod);
        //console.log(tipoVenta);
        const img = document.createElement("img");
        if (tipoVenta==-1){
            img.src = `static/imagenes/${prod.unidadInv}.png`;
        } else if (tipoVenta==-2){
            img.src = `static/imagenes/paquete.png`;
        } else if (tipoVenta==-3){
            img.src = `static/imagenes/kg.png`;
        }
        img.width = 25;
        img.height = 25;
        img.alt = "";
        return img;
    }

    function generaBotonTipoVenta(prod, tipoVenta, etiqueta=false){
        const btn = document.createElement("button");
        btn.type = "button";
        //btn.className = "tipoVenta-btn";
        btn.value = tipoVenta;
        // styles
        btn.style.marginRight = "10px";
        btn.style.border = "none";
        btn.style.backgroundColor = "transparent";
        // image
        const img = generaImagenTipoVenta(prod, tipoVenta);
        if (tipoVenta==-1){
            btn.title = prod.unidadInv;
        } else if (tipoVenta==-2){
            btn.title = prod.descVentaPaquete;
        } else if (tipoVenta==-3){
            btn.title = 'kilogramo';
        }
        // assemble
        if (etiqueta){
            const text = document.createElement("span");
            text.textContent = btn.title;
            text.style.marginRight = "6px";   // spacing from icon
            text.style.pointerEvents = "none"; // 👈 click goes to button
            btn.style.border = "3px double black";
            btn.appendChild(text);
        }
        btn.appendChild(img);
        return btn;
    }

    function dibujaTiposVentaCambiar(prod){
        // new logic added
        //if (prod.muestraUnidad && prod.tipoVentaId!=-1){
        const container = document.createElement("div");
        const tiposUsados = getTiposVentaEnTabla(prod.productoId);
        if (prod.muestraUnidad && prod.tipoVentaId !== -1 && !tiposUsados.has(-1)) {
            //prodHtml+=`<input class="tipoVenta-btn" type="image" value="-1" src="static/imagenes/${prod.unidadInv}.png" width="25" height="25" title="${prod.unidadInv}" style="margin-right: 10px;"/>`;
            const btn = generaBotonTipoVenta(prod, -1);
            btn.classList.add("tipoVenta-btn");
            container.append(btn);
        }
        // new logic added
        // if (prod.muestraPaquete && prod.tipoVentaId!=-2){
        if (prod.muestraPaquete && prod.tipoVentaId !== -2 && !tiposUsados.has(-2)) {
            //prodHtml+=`<input class="tipoVenta-btn" type="image" value="-2" src="static/imagenes/paquete.png" width="25" height="25" title="paquete" style="margin-right: 10px;"/>`;
            const btn = generaBotonTipoVenta(prod, -2);
            btn.classList.add("tipoVenta-btn");
            container.append(btn);
        }
        // new logic added
        //if (prod.muestraKg && prod.tipoVentaId!=-3){
        if (prod.muestraKg && prod.tipoVentaId !== -3 && !tiposUsados.has(-3)) {
            //prodHtml+=`<input class="tipoVenta-btn" type="image" value="-3" src="static/imagenes/kg.png" width="25" height="25" title="kilogramo"/>`;
            const btn = generaBotonTipoVenta(prod, -3);
            btn.classList.add("tipoVenta-btn");
            container.append(btn);
        }
        return container;
    }

    function setFilaProdHTML(prod){
        //let precio = parseFloat(prod.precio) || 0;
        const precio = parseSmartNumber(prod.precio) || 0;
        const subtotal = prod.encontrado ? precio * prod.cantidad : 0;
        const {mainpart, extra} = splitParenTextSimple(prod.descVenta);

        let prodHtml = `
        <td style="width: 1%;" class="no-print"><button type="button" class="borrar-btn" title="Borrar" style="border:none; background-color: transparent;">
            <img src="static/imagenes/borrar_icon.png" width="25" height="25" alt="">
            </button></td>
        <td style="width: 1%;" class="celda_ocultable no-print codigo-numerico" nowrap><b>${prod.codigoNumerico ?? ''}</b></td> 
        <td style="width: 1%;" class="no-print" nowrap title="Info">`;
        if (prod.tipoVentaId!=-4){
            prodHtml+= `<button type="button" class="info-btn" title="Info" style="border:none; background-color: transparent;">
            <img src="static/imagenes/info.png" width="25" height="25" alt="">
            </button>`;
        }
        let img = generaImagenTipoVenta(prod, prod.tipoVentaId);
        img.style.marginRight="10px";
        //console.log(img.outerHTML);
        prodHtml+=`</td>
        <td style="width:auto; color: ${prod.existencia<0 || prod.existencia<prod.minimo ? 'BB0000' : ''}">${img.outerHTML} ${prod.claves? prod.claves+" - " : ""} ${prod.descripcion}</td>
        <td style="width: 1%;"><input type="number" step="any" min="0" value="${prod.cantidad}" class="cantidad-input"
            style="width:80px;font-weight:bold;" placeholder="${prod.cantidad}" alt="${prod.cantidad}" required/>
        </td>
        <td style="width: 1%;" class="no-print"><button type="button" class="arrow-up" title="Uno más" style="border:none; background-color: transparent;">
            <img src="static/imagenes/up_icon.jpg" width="25" height="25" alt="">
            </button>
        </td>
         <td style="width: 1%;" class="no-print"><button type="button" class="arrow-down" title="Uno menos" style="border:none; background-color: transparent;">
            <img src="static/imagenes/down_icon.jpg" width="25" height="25" alt="">
            </button>
        </td>
        <td style="width: 1%;" class="no-print" nowrap title="${extra}"><b>${prod.tipoVentaId!=-2? mainpart:extra}</b></td>
        <td class="celda_ocultable" style="width: 1%;">
          <input type="number" step="any" value="${precio}"  class="precio-input yes-print" min="0"
             style="width:80px;font-weight:bold;" placeholder="${precio}" alt="${precio}" required readonly/>
        </td>
        <td class="celda_ocultable no-print"><button type="button" class="plus-btn" title="Subir precio" style="border:none; background-color: transparent; display:none;">
            <img src="static/imagenes/plus_icon.jpg" width="25" height="25" alt="">
            </button>
        </td>
        <td class="celda_ocultable no-print"><button type="button" class="minus-btn" title="Bajar precio" style="border:none; background-color: transparent; display:none;">
            <img src="static/imagenes/minus_icon.jpg" width="25" height="25" alt="">
            </button>
        </td>
        <td class="celda_ocultable subtotal-cell yes-print" style="width: 1%; font-weight: bold; font-size:23px; white-space: nowrap;"><b>$ ${parseSmartNumber(subtotal)}</b></td>`;
        prodHtml+=`<td style="width: 1%;" class="celda_ocultable no-print prodVentasCambiar" nowrap>`;
        prodHtml+= dibujaTiposVentaCambiar(prod).innerHTML;
        prodHtml+=`</td>`;
        return prodHtml;
    }

    function agregarProducto(prod) {
        //const existente = findProductoVenta(prod.productoId); //findProductoVenta(prod.productoId, prod.tipoVentaId);
        const existente = findProductoVenta(prod.productoId, prod.tipoVentaId);
        //logDebug("existente", existente);
        if (existente) {
            //existente.cantidad += parseFloat(prod.cantidad??1);
            // Just update quantity cell visually
            //logDebug("productoId", prod.productoId);
            //logDebug("tr[data-*]", tabla_tbody.querySelector(`tr[data-*]`));
            const filaExistente = tabla_tbody.querySelector(`tr[data-producto-id="${existente.productoId}"][data-tipo-venta-id="${existente.tipoVentaId}"]`);
            //logDebug("filaExistente", filaExistente);
            if (filaExistente) {
                //console.log(JSON.stringify(filaExistente.outerHTML));
                let cantidadInput = filaExistente.querySelector(".cantidad-input");
                if (cantidadInput) {
                    existente.cantidad += parseFloat(prod.cantidad??1);
                    cantidadInput.value = parseSmartNumber(existente.cantidad.toFixed(3));
                    cantidadInput.setAttribute("placeholder", existente.cantidad);
                }
                const prodRows = tabla_tbody.querySelectorAll(`tr`);
                prodRows.forEach(el => {
                    el.style.removeProperty("--bs-table-bg");
                });
                filaExistente.style.setProperty("--bs-table-bg","#d1eaf6");
                tabla_tbody.prepend(filaExistente);
            }
            actualizarTotales();
            resetInfoSelections();
            return;
        }
        
        // Add new product object
        productosVenta.unshift(prod);
        // Create a new row (not rebuilding the whole table)
        const fila = document.createElement("tr");
        fila.dataset.productoId = prod.productoId;
        fila.dataset.tipoVentaId = prod.tipoVentaId;
        
        //logDebug("fila.dataset", fila.dataset);
        fila.innerHTML=setFilaProdHTML(prod);
        const prodRows = tabla_tbody.querySelectorAll(`tr`);
        prodRows.forEach(el => {
            el.style.removeProperty("--bs-table-bg");
        });
        fila.style.setProperty("--bs-table-bg","#d1eaf6");
        setFormatoTableta(fila)
        tabla_tbody.prepend(fila);
        tabla_thead.style.display = "block";
        tabla_tfoot.style.display = "block";

        // Initialize image controls on this new row
        //inicializarControlesFila(fila);
        actualizarTotales();
        updateGuardarButtonVisibility();
        resetInfoSelections();
        fila.focus();
    }

    async function dibujaTicket(res){
        console.log(JSON.stringify(res["resultado"]));
        let tdTicket = document.createElement("td");
        tdTicket.id = "tdTicket";
        let divTicket = await generateTicket(res["resultado"]);
        divTicket.style.border="1px solid black";
        tdTicket.style.verticalAlign = "top";
        tdTicket.style.overflow = "visible";
        const scaleWrapper = document.createElement("div");
        scaleWrapper.style.display = "inline-block";
        scaleWrapper.style.paddingLeft = "30px"; // requested left spacing
        divTicket.style.transformOrigin = "top right";
        scaleWrapper.append(divTicket);
        tdTicket.append(scaleWrapper);
        return tdTicket;
    }

    async function guardarVenta(sinInventario=0) {
        //if (window.thisRol=="esclavo"){
        if (!confirm(`¿Guardar venta?`)) return;
        //}
        productosVenta.forEach(p => {
            p.subtotal = (p.precioVenta * p.cantidad).toFixed(2);
            if (configDev.MS_SOY){
                p.dispositivoId = configDev.MS_SOY.dispositivoId;
            }
            p.sinInventario =sinInventario;
        });
        const ventasAGuardar = productosVenta;
        //console.log(ventasAGuardar);
        if (ventasAGuardar.length === 0) {
            mensaje.innerHTML = "No hay productos válidos para guardar.";
            playErrorSound();
            return;
        }
        res = await myfetch("/vender/guardar", ventasAGuardar );
        if (res.success) {
            console.log(res.fechaVenta);
            mensaje.innerHTML = `<div style="color: green">✅ Venta guardada correctamente <span style="font-size: 2em"> $ ${parseSmartNumber(res.total)}</span>
            <br/>`+formatDate(res.fechaVenta) +`</div>`;
            playSuccessSound();
            eliminarVenta();
            // TICKET
            let resVenta = document.createElement("table");
            let trVenta = document.createElement("tr");
            //if (window.thisRol=="maestro"){
                let tdTicket = await dibujaTicket(res);
                trVenta.append(tdTicket);
            //}
            let tablaVenta = generaTablaVenta(res["resultado"]);
            tablaVenta.classList.add("zebra");
            tablaVenta.style.width="auto";
            tablaVenta.style.border="1px solid black";
            let tdVenta = document.createElement("td");
            let divPago = document.createElement("div");
            let tablaPago = document.createElement("table");
            let trHeaderPago = document.createElement("tr");
            let tdHeader = document.createElement("td");
            tdHeader.innerHTML = "<b>Total</b>";
            trHeaderPago.append(tdHeader);
            tdHeader = document.createElement("td");
            tdHeader.innerHTML = "<b>Tipo Pago</b>";
            trHeaderPago.append(tdHeader);
            tdHeader = document.createElement("td");
            tdHeader.innerHTML = "<b>Paga con</b>";
            trHeaderPago.append(tdHeader);
            tdHeader = document.createElement("td");
            tdHeader.innerHTML = "<b>Cambio</b>";
            trHeaderPago.append(tdHeader);
            tablaPago.append(trHeaderPago);
            let trPago = document.createElement("tr");
            tablaPago.append(trPago);
            let tdTotal = document.createElement("td");
            tdTotal.style.fontSize = "25px";
            tdTotal.innerHTML = "<b>$ "+parseSmartNumber(res.total)+"</b>";
            /* inputTotal.setAttribute("type", "numeric");
             tdTotal.append(inputTotal); */
            trPago.append(tdTotal);
            let tdPagoCon = document.createElement("td");
            let opcionesPago = document.createElement("select");
            let opt = document.createElement("option");
            opt.value="E";
            opt.textContent="Efectivo";
            opcionesPago.options.add(opt);
            opt = document.createElement("option");
            opt.value="R";
            opt.textContent="Transferencia";
            opcionesPago.options.add(opt);
            opt = document.createElement("option");
            opt.value="T";
            opt.textContent="Tarjeta";
            opcionesPago.options.add(opt);
            opcionesPago.options[0].selected = true;
            opcionesPago.style.fontSize = "25px";
            tdPagoCon.append(opcionesPago);
            trPago.append(tdPagoCon);
            let tdPago = document.createElement("td");
            let inputPago = document.createElement("input");
            inputPago.setAttribute("type", "number");
            inputPago.setAttribute("size", 10);
            inputPago.style.width = 140;
            inputPago.setAttribute("step","any");
            inputPago.value = res.total;
            inputPago.style.fontSize = "25px";
            inputPago.setAttribute("min", res.total);
            tdPago.append(inputPago);
            trPago.append(tdPago);
            let tdCambio = document.createElement("td");
            let inputCambio = document.createElement("input");
            inputCambio.setAttribute("type", "number");
            inputCambio.setAttribute("size", 10);
            inputCambio.style.width = 140;
            inputCambio.setAttribute("step","any");
            inputCambio.style.fontSize = "25px";
            inputCambio.setAttribute("min", 0);
            tdCambio.append(inputCambio);
            trPago.append(tdCambio);
            inputPago.addEventListener("focus", e => {
                inputPago.value="";
                inputCambio.value="";
            });
            inputCambio.addEventListener("focus", e => {
                inputCambio.value="";
                inputPago.value="";
            });
            inputPago.addEventListener("input", e => {
                if (inputPago.value != "") {
                    let val = parseSmartNumber(inputPago.value,2) - res.total;
                    if (Number.isInteger(val)){
                        inputCambio.value= val;
                    } else {
                        inputCambio.value= Number(val).toFixed(2);
                    }
                } else {
                    inputCambio.value="";
                }
            });
            inputCambio.addEventListener("input", e => {
                if (inputCambio.value != "") {
                    let val = res.total + parseSmartNumber(inputCambio.value,2);
                    if (Number.isInteger(val)){
                        inputPago.value= val;
                    } else {
                        inputPago.value= Number(val).toFixed(2);
                    }
                } else {
                    inputPago.value="";
                }
            });
            opcionesPago.addEventListener("change", function(){
                inputPago.value = res.total;
                inputCambio.value = "";
            });
            let tdGuardaPago = document.createElement("td");
            let inputGuardaPago = document.createElement("button");
            inputGuardaPago.innerText = 'Guardar Pago';
            inputGuardaPago.style.fontSize = "25px";
            inputGuardaPago.addEventListener("click", async function(){
                let pagoVal = Number(inputPago.value);
                let cambioVal = Number(inputCambio.value);
                if (pagoVal==0){
                    inputPago.value = res.total;
                    inputCambio.value = "";
                } else if (pagoVal<res.total){
                    alert("El monto del pago es insuficiente");
                    return;
                }
                let infoPago = {
                    "dispositivoId": configDev.MS_SOY.dispositivoId,
                    "fechaVenta": res.fechaVenta,
                    "total": res.total,
                    "tipoPago": opcionesPago.value,
                    "pago": Number(inputPago.value),
                    "cambio": Number(inputCambio.value),
                    "extraInfo": inputInfoPago.value
                };
                let resPago = await myfetch("/vender/setPago", infoPago);
                if (resPago["success"]){
                    centerMessage("Pago Guardado");
                    // if (window.thisRol=="maestro"){
                        tdTicket = document.getElementById("tdTicket");
                        if (tdTicket) {
                            tdTicket.innerHTML="";
                            let newTicket = await dibujaTicket(res);
                            //tdTicket.innerHTML=newTicket.innerHTML;
                            tdTicket.replaceChildren(newTicket);
                        }
                        // trVenta.append(tdTicket);
                    // }
                } else {
                    centerMessage("Pago No Guardado");
                }
            });
            tdGuardaPago.append(inputGuardaPago);
            trPago.append(tdGuardaPago);
            trPago = document.createElement("tr");
            tdPago = document.createElement("td");
            tdPago.innerText = "Comentario: ";
            trPago.append(tdPago);
            tdPago = document.createElement("td");
            tdPago.colSpan = 4;
            let inputInfoPago = document.createElement("input");
            inputInfoPago.setAttribute("type", "text");
            inputInfoPago.style.width = "100%";
            tdPago.append(inputInfoPago);
            trPago.append(tdPago);
            tablaPago.append(trPago);
            let divTablaVenta = document.createElement("div");
            divPago.append(tablaPago);
            divPago.append(document.createElement("br"));
            tdVenta.append(divPago);
            divTablaVenta.append(tablaVenta);
            tdVenta.append(divTablaVenta);
            trVenta.append(tdVenta);
            resVenta.append(trVenta);
            resVenta.style.width = "auto";
            resVenta.style.margin = "0 auto";
            mensaje.append(resVenta);
            if (window.thisRol=="maestro"){
                //inputPago.value="";
                [inputPago, inputCambio, inputInfoPago].forEach(input => {
                    input.addEventListener("keydown", (e) => {
                            if (e.key === "Enter") {
                                e.preventDefault();
                                inputGuardaPago.click();
                            }
                        });
                });
                document.activeElement?.blur();
                inputPago.focus();
            }
        } else {
            mensaje.innerHTML = `❌ Error al guardar: ${res.error}`;
            playErrorSound();
        }
    }

    function generaTablaVenta(productos){
        const schema = [         
            {   key: "codigoNumerico",
                title: "Codigo",
                format: (v, row, tr, td) => {
                    td.style.fontWeight = "bold";
                    td.style.fontSize = "20px";
                    return `${v}`;
                }
            },
             {   key: "claves",
                title: "Clave",  },
            {   key: "descripcion",
                title: "Producto"   },
            {   key: "cantidad",
                title: "Cant",  },   
            {   key: "descVenta",
                title: "Tipo"  
                // format: (v, row) => {
                //     if (v==-1)
                //         return row.unidadInv;
                //     else if (v==-3)
                //         return 'kilo'
                //     else
                //         return 'paquete';
                // }
            },
            {   key: "precioVenta",
                title: "Precio",
                format: (v, row, tr, td) => `$${parseSmartNumber(v)}`  },
            {   key: "subtotal",
                title: "Importe",
                align: "right",
                format: (v, row, tr, td) => `$${parseSmartNumber(v)}`  },
            {   key: "tipoVentaId",
                title: "Inventario",
                format: (v, row, tr, td) => {
                    if (row["existencia"]<1 || row["existencia"]<row["minimo"]){
                        tr.style.color="#a30101";
                    }
                    return descExistencia(row);
                }
            }
            ];
        return renderProductTable(productos, schema);
    }

    /**************************************************/
    /**************************************************/
    // === 👇 FUNCIONALIDAD DE TABLA PRODUCTOS 👇 ===
    /**************************************************/

    let celdasOculatbles = document.querySelectorAll(".celda_ocultable");
    celdasOculatbles.forEach(celda => celda.style.display = "none");
    const totalRow = tabla_tfoot.querySelector("tr");

    btn_toggle_columnas.addEventListener("click", () => {
        //logDebug('Click on ', 'btn_toggle_columnas');
        toggleColumnas();

    });

    btn_eliminar_venta.addEventListener("click", () => {
        //logDebug('Click on ', 'btn_eliminar_venta');
        //if (window.thisRol=="esclavo"){
        if (!confirm(`¿Eliminar venta?`)) return;
        //}
        eliminarVenta();
        centerMessage("Venta eliminada");

    });

    function findProductoVenta(productoId, tipoVentaId){
        const producto = productosVenta.find(p => p.productoId === parseInt(productoId) && p.tipoVentaId===parseInt(tipoVentaId));
        return producto;
    }

    // ---------- Toggle hideable columns ----------
    function toggleColumnas(isHidden) {
        celdasOculatbles = document.querySelectorAll(".celda_ocultable");
        //logDebug("arg isHidden", isHidden)
        if (isHidden === undefined) {
            isHidden = Array.from(celdasOculatbles).some(c => c.style.display === "none");
        }
        mostrarCeldasOcultas = isHidden;
        //logDebug("isHidden", isHidden);
        celdasOculatbles.forEach(
            celda => celda.style.display = isHidden ? "table-cell" : "none");
        if (totalRow) totalRow.style.display = isHidden ? "table-row" : "none";
    }

    function eliminarVenta() {
        //logDebug("eliminarVenta", "eliminarVenta");
        productosVenta = [];
        if (tabla_tbody) {
            tabla_tbody.innerHTML = ""; // removes only the product rows
        }
        actualizarTotales();
        //actualizarVisibilidadBotones();
        mostrarCeldasOcultas = true;
    }

    // ---------- Button visibility toggle ----------
    function actualizarVisibilidadBotones() {
        let tieneProductos = tabla_tbody && tabla_tbody.querySelectorAll("tr").length > 0;
        //logDebug("tieneProductos", tieneProductos);
        let soyMaestro = window.thisRol=='maestro';
        let soyEsclavo = window.thisRol=='esclavo';
        btnGuardar.style.display = tieneProductos ? "inline-block" : "none";
        //btn_toggle_columnas.style.display = tieneProductos && soyMaestro ? "inline-block" : "none";
        btn_eliminar_venta.style.display = tieneProductos ? "inline-block" : "none";
        //btnImprimir.style.display = tieneProductos && soyMaestro ? "inline-block" : "none";
        //btnSinInventario.style.display = tieneProductos && soyMaestro ? "inline-block" : "none";
        //logDebug("to check", "thead");
        tabla_thead.style.display = tieneProductos ? "" : "none";
        //logDebug("to check", "tfoot");
        tabla_tfoot.style.display = tieneProductos ? "" : "none";
        toggleColumnas(mostrarCeldasOcultas);
    }

    // ---------- Update totals (wrapper) ----------
    function actualizarTotales() {
        const totalCell = document.getElementById("total");
        if (!tabla_tbody || !totalCell) return;

        let total = 0;
        tabla_tbody.querySelectorAll("tr").forEach(row => {
            const cantidad = parseFloat(row.querySelector(".cantidad-input")?.value || 0);
            const precioVenta = parseFloat(row.querySelector(".precio-input")?.value || 0);
            const subtotalCell = row.querySelector(".subtotal-cell");
            const subtotal = cantidad * precioVenta;
            if (subtotalCell) subtotalCell.textContent = "$ "+parseSmartNumber(subtotal);
            total += subtotal;
        });
        //totalCell.textContent = "$ "+parseSmartNumber(total);
        totalCell.textContent = "$ "+parseSmartNumber(total);
        actualizarVisibilidadBotones();
    }

    function getDescVenta(prod, tipoVentaId){
        if (tipoVentaId==-1){
            return prod.descVentaUnidad;
        } else if (tipoVentaId==-2){
            return prod.descVentaPaquete;
        } else if (tipoVentaId==-3){
            return prod.descVentaKg;
        }
    }

    function getPrecioVenta(prod, tipoVentaId){
        if (tipoVentaId==-1){
            return prod.precioUnidad;
        } else if (tipoVentaId==-2){
            return prod.precioPaquete;
        } else if (tipoVentaId==-3){
            return prod.precioKg;
        }
    }

    function addTipoVentaAction(producto, tipoVentaId){
        const nuevo = structuredClone(producto);
        nuevo.tipoVentaId = tipoVentaId;
        nuevo.descVenta = getDescVenta(producto, tipoVentaId);
        nuevo.precioVenta = getPrecioVenta(producto, tipoVentaId);
        nuevo.precio = getPrecioVenta(producto, tipoVentaId);
        nuevo.cantidad=1;
        agregarProducto(nuevo);
        redibujaTodasTipoVentas(nuevo);
        actualizarVisibilidadBotones();
    }

    function dibujaInfoSection(producto){
            const infoTH = document.getElementById("infoTH");
            infoTH.innerHTML='';

            let tb = document.createElement("table");
            let tr= document.createElement("tr");
            let td = document.createElement("td");
            td.style.display = "flex";
            td.style.gap = "10px";

            infoTH.appendChild(tb);
            tb.appendChild(tr);
            tr.appendChild(td);

            div = document.createElement("div");
            div.insertAdjacentHTML("beforeend",`<b>Barras:</b> ${producto.codigoBarras}`);
            td.append(div);

            if (producto.claves){
                div = document.createElement("div");
                div.insertAdjacentHTML("beforeend", `<b>Claves:</b> ${producto.claves}`);
                td.append(div);
            }

            div = document.createElement("div");
            div.insertAdjacentHTML("beforeend", `<b>Existencia:</b> ${producto.descExistencia}`);
            td.append(div);

            const tipoVentasEnTabla = getTiposVentaEnTabla(producto.productoId);  // added
    
            if (tipoVentasEnTabla && tipoVentasEnTabla.size<3){
                let divAgregar = document.createElement("div");
                divAgregar.insertAdjacentHTML("beforeend", `<b>Agregar:</b>`);
                let muestraOpciones=false;

                div = document.createElement("div");
                // new logic added

                // new logic added
                //if (producto.muestraUnidad){
                if (producto.muestraUnidad && !tipoVentasEnTabla.has(-1)) {
                    const btn = generaBotonTipoVenta(producto, -1);
                    btn.className = "add-tipoVenta-btn";
                    btn.onclick = () => {
                        addTipoVentaAction(producto, -1);
                        infoTH.innerHTML = "";
                    };
                    div.appendChild(btn);
                    muestraOpciones=true;
                }
                // new logic added
                //if (producto.muestraPaquete){
                if (producto.muestraPaquete && !tipoVentasEnTabla.has(-2)) {
                    const btn = generaBotonTipoVenta(producto, -2);
                    btn.className = "add-tipoVenta-btn";
                    btn.onclick = () => {
                        addTipoVentaAction(producto, -2);
                        infoTH.innerHTML = "";
                    };
                    div.appendChild(btn);
                    muestraOpciones=true;
                }
                // new logic added
                //if (producto.muestraKg){
                if (producto.muestraKg && !tipoVentasEnTabla.has(-3)) {
                    const btn = generaBotonTipoVenta(producto, -3);
                    btn.className = "add-tipoVenta-btn";
                    btn.onclick = () => {
                        addTipoVentaAction(producto, -3);
                        infoTH.innerHTML = "";
                    };
                    div.appendChild(btn);
                    muestraOpciones=true;
                }
                if (muestraOpciones){
                    td.append(divAgregar);
                    td.append(div);
                }
            }
    }

    function manejarTipoVentaClick(btn, producto, filaExistente) {
        const nuevoTipoVentaId = Number(btn.value);

        // NEW ADDITION
        // 🚫 BLOCK if this tipoVenta already exists for the product
        const usados = getTiposVentaEnTabla(producto.productoId);
        if (usados.has(nuevoTipoVentaId)) {
            centerMessage("Ese tipo de venta ya está en la tabla");
            playErrorSound();
            return;
        }
        // END OF NEW ADDITION

        // 🔴 remove old product entry
        const oldIndex = productosVenta.findIndex(
            p => p.productoId === producto.productoId &&
                p.tipoVentaId === producto.tipoVentaId
        );
        if (oldIndex !== -1) productosVenta.splice(oldIndex, 1);

         // ✅ update product
        producto.tipoVentaId = nuevoTipoVentaId;
        producto.descVenta = getDescVenta(producto, nuevoTipoVentaId);
        producto.precioVenta = getPrecioVenta(producto, nuevoTipoVentaId);
        producto.precio = getPrecioVenta(producto, nuevoTipoVentaId);
        // ✅ reinsert product
        productosVenta.push(producto);

        // ✅ rebuild row safely
        const newTr = document.createElement("tr");
        newTr.dataset.productoId = producto.productoId;
        newTr.dataset.tipoVentaId = producto.tipoVentaId;
        newTr.innerHTML = setFilaProdHTML(producto);
        setFormatoTableta(newTr);
        filaExistente.replaceWith(newTr);

        actualizarTotales();
    }
    // event listeners controles fila

    tabla_tbody.addEventListener("change", e => {
        //e.stopPropagation();     // 🚫 prevent row selection
        const target = e.target;
        if (!(target instanceof HTMLInputElement)) return;
        //console.log("CHANGE EVENT");
        const filaExistente = target.closest("tr");
        if (!filaExistente) return;
        const productoId = filaExistente.dataset.productoId;
        const tipoVentaId = filaExistente.dataset.tipoVentaId;
        //alert(productoId + " " + tipoVentaId);
        const producto = findProductoVenta(productoId, tipoVentaId);
        if (!producto) {
            alert("No se encontro producto " + productoId + " " + tipoVentaId);
            return;
        }
        // const cantidadInput = filaExistente.querySelector(".cantidad-input");
        // if (cantidadInput){
        if (target.classList.contains("cantidad-input")) {
            e.stopPropagation();     // 🚫 prevent row selection
            //console.log("CAMBIO CANTIDAD");
             //logDebug("cantidadInput", cantidadInput);
            let nuevaCantidad = parseFloat(target.value) || 0;
            if (producto && producto.encontrado) {
                producto.cantidad = parseFloat(nuevaCantidad) || 1;
                actualizarTotales();
            }
            return;
        }
        // const precioInput = filaExistente.querySelector(".precio-input");
        // if (precioInput){
        if (target.classList.contains("precio-input")) {
            e.stopPropagation();     // 🚫 prevent row selection
            //console.log("CAMBIO PRECIO");
            //console.log(producto.encontrado);
            //console.log(producto);
            if (producto && producto.encontrado) {
                let nuevoPrecio = parseFloat(target.value) || 1;
                producto.precioVenta = nuevoPrecio;
                //console.log("nuevo precio "+nuevoPrecio);
                //console.log("prod precio "+producto.precio);
                // ############################ verificar cambio de color de precios
                if (nuevoPrecio == producto.precio) {
                    target.style.color = "black";
                    target.style.backgroundColor = "#ffffff";
                } else if (nuevoPrecio < producto.precio) {
                    target.style.color = "red";
                    target.style.backgroundColor = "#fbff07ff";
                } else {
                    target.style.color = "black";
                    target.style.backgroundColor = "#b3ffadff";
                }
                actualizarTotales();
            }
            return;
        }
    });

    // **** Listener para la tabla de articulos en venta
    tabla_tbody.addEventListener("click", e => {
        e.stopPropagation();     // 🚫 prevent row selection
        const filaExistente = e.target.closest("tr");
        if (!filaExistente) return;
        const productoId = filaExistente.dataset.productoId;
        const tipoVentaId = filaExistente.dataset.tipoVentaId;
        //alert(productoId + " " + tipoVentaId);
        const producto = findProductoVenta(productoId, tipoVentaId);
        if (!producto) {
            alert("No se encontro producto " + productoId + " " + tipoVentaId);
            return;
        }
        const tipoVentaBtn = e.target.closest(".tipoVenta-btn");
        if (tipoVentaBtn){
            e.stopPropagation();     // 🚫 prevent row selection
            manejarTipoVentaClick(tipoVentaBtn, producto, filaExistente);
            const infoTH = document.getElementById("infoTH");
            if (infoTH.innerHTML.trim()!=''){
                dibujaInfoSection(producto);
            }
            return;
        }
        const upArrow = e.target.closest(".arrow-up");
        const cantidadInput = filaExistente.querySelector(".cantidad-input");
        if (upArrow && cantidadInput){
            e.stopPropagation();     // 🚫 prevent row selection
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
            cantidadInput.value = val;
            if (producto) producto.cantidad = val;
            actualizarTotales();
            return;
        }
        const downArrow = e.target.closest(".arrow-down");
        if (downArrow && cantidadInput){
            e.stopPropagation();     // 🚫 prevent row selection
            let val = parseFloat(cantidadInput.value) || 0;
            if (val <= 1) {
                // Find the next value in the array greater than current
                //logDebug("valoresMenoresUno", valoresMenoresUno);
                let valoresMenoresUnoR = valoresMenoresUno.slice();
                valoresMenoresUnoR.reverse();
                //logDebug("Reversed", valoresMenoresUnoR);
                //logDebug("valoresMenoresUno", valoresMenoresUno);
                const siguiente = (valoresMenoresUnoR).find(v => v < val);
                val = siguiente !== undefined ? siguiente : 0.1; // jump to 1 if already at the top
            } else {
                val -= 1;
            }
            // Ensure minimum of 0.1
            if (val < 0.1) val = 0.1;
            cantidadInput.value = val;
            const producto = findProductoVenta(productoId, tipoVentaId);
            if (producto) producto.cantidad = val;
            actualizarTotales();
            return;
        }
        const plusBtn = e.target.closest(".plus-btn");
         const precioInput = filaExistente.querySelector(".precio-input");
        if (plusBtn && precioInput){
            e.stopPropagation();     // 🚫 prevent row selection
            let val = parseFloat(precioInput.value) || 0;
            if (val < 1) {
                val = Math.max(0.1, (parseFloat(precioInput.value) + 0.1).toFixed(1));
            } else {
                if (Number.isInteger(parseFloat(precioInput.value))){
                    val = Math.max(0.1, parseFloat(precioInput.value) + 1);
                } else {
                    val = Math.max(0.1, Math.ceil(parseFloat(precioInput.value))); 
                }
            }
            precioInput.value = parseSmartNumber(val);
            //logDebug("productoId", productoId);
            //logDebug("productosVenta", productosVenta);
            //logDebug("producto", producto);
            if (producto) {
                producto.precioVenta = val;
                //logDebug("val ",val);
                //logDebug("producto.precio ",producto.precio);
                if (producto.precio == val) {
                    precioInput.style.color = "black";
                    precioInput.style.backgroundColor = "#ffffff";
                } else if (producto.precio > val) {
                    precioInput.style.color = "red";
                    precioInput.style.backgroundColor = "#fbff07ff";
                } else {
                    precioInput.style.color = "black";
                    precioInput.style.backgroundColor = "#b3ffadff";
                }
            }
            actualizarTotales();
            return;
        }
        const minusBtn = e.target.closest(".minus-btn");
        if (minusBtn && precioInput){
            e.stopPropagation();     // 🚫 prevent row selection
            let val = parseFloat(precioInput.value) || 0;
            if (val <= 1) {
                val = Math.max(0.1, (parseFloat(precioInput.value) - 0.1).toFixed(1));
            } else {
                if (Number.isInteger(parseFloat(precioInput.value))){
                    val = Math.max(0.1, parseFloat(precioInput.value) - 1);
                } else {
                    val = Math.max(0.1, Math.floor(parseFloat(precioInput.value))); 
                }
            }
            precioInput.value = parseSmartNumber(val);
            if (producto) {
                producto.precioVenta = val;
                if (producto.precio == val) {
                    precioInput.style.color = "black";
                    precioInput.style.backgroundColor = "#ffffff";
                } else if (producto.precio > val) {
                    precioInput.style.color = "red";
                    precioInput.style.backgroundColor = "#fbff07ff";
                } else {
                    precioInput.style.color = "black";
                    precioInput.style.backgroundColor = "#b3ffadff";
                }
            }
            actualizarTotales();
            return;
        }
        const borrarBtn = e.target.closest(".borrar-btn");
        if (borrarBtn){
            e.stopPropagation();     // 🚫 prevent row selection
            if (productosVenta.length === 1)
                if (!confirm(`¿Eliminar venta?`)) return;
            const index = productosVenta.findIndex(p => p.productoId === Number(productoId) && p.tipoVentaId === Number(tipoVentaId));
            if (index !== -1) {
                productosVenta.splice(index, 1);
                // Remove the row from the DOM
                filaExistente.remove();
            }
            // If there are no products left, clean the table and hide buttons
            if (productosVenta.length === 0) {
                eliminarVenta();
                centerMessage("Venta eliminada");
            } else {
                // Otherwise just update totals normally
                actualizarTotales();
                redibujaTodasTipoVentas(producto);
                resetInfoSelections();
            }
            return;
        }
        const infoBtn =  e.target.closest(".info-btn");
        //const infoBtn = filaExistente.querySelector(".info-btn");
         if (infoBtn){
            e.stopPropagation();     // 🚫 prevent row selection
            if (infoBtn.classList.contains("activeInfo")){
                const infoTH = document.getElementById("infoTH");
                infoTH.innerHTML='';
                infoBtn.classList.remove("activeInfo");
                return;
            }
            dibujaInfoSection(producto);
            document.querySelectorAll('.info-btn').forEach(b =>
                b.classList.remove('activeInfo')
            );
            infoBtn.classList.add("activeInfo");
            return;
         }
    });

    /***** PARA DEDUPLICAR DTIPOS DE VENTA DE UN PRODUCTO Y ELEGIR ENTRE ELLAS */

    function getTiposVentaEnTabla(productoId) {
        // return productosVenta
        //     .filter(p => p.productoId === productoId)
        //     .map(p => p.tipoVentaId);
        const usados = new Set(
            productosVenta
                .filter(p => p.productoId === productoId)
                .map(p => p.tipoVentaId)
        );
        return usados;
    }

    // function getTiposVentaDisponibles(producto, excluirTipoVentaId = null) {
    //     const usados = new Set(getTiposVentaEnTabla(producto.productoId));

    //     if (excluirTipoVentaId !== null) {
    //         usados.delete(excluirTipoVentaId);
    //     }

    //     return producto.tiposVenta.filter(tv => !usados.has(tv.tipoVentaId));
    // }

    function mostrarSelectorTipoVenta(producto, tipoVentaId) {
        // if (!(tiposVentaEnTabla instanceof Set)) {
        //     console.error("tiposVentaEnTabla is not a Set", tiposVentaEnTabla);
        //     return;
        // }
            return new Promise((resolve) => {
                if (!tipoVentaId){
                    console.error("tipoVentaId no definido", tipoVentaId);
                    resolve(false);
                    return;
                }

            // const opciones = [];

            // // show ONLY existing tipos (because this selector is for "which row to add to")
            // if (producto.muestraUnidad && tiposVentaEnTabla.has(-1)) opciones.push(-1);
            // if (producto.muestraPaquete && tiposVentaEnTabla.has(-2)) opciones.push(-2);
            // if (producto.muestraKg && tiposVentaEnTabla.has(-3)) opciones.push(-3);

            // if (opciones.length === 0) return;
            
            let divAgregarTipoVenta = document.createElement("div");
            divAgregarTipoVenta.setAttribute("id", "divAgregarTipoVenta");
            divAgregarTipoVenta.style.position = "fixed";
            divAgregarTipoVenta.style.top = "100px";
            divAgregarTipoVenta.style.left = "50%";
            divAgregarTipoVenta.style.transform = "translate(-50%, -50%)";
            divAgregarTipoVenta.style.background = "#fff";
            divAgregarTipoVenta.style.padding = "15px";
            divAgregarTipoVenta.style.border = "1px solid #999";
            divAgregarTipoVenta.style.zIndex = 9999;
            let mtb = document.createElement("table");
            let mtr = document.createElement("tr");
            let mtd = document.createElement("td");

            //opsAgregarTipoVenta.innerHTML = `<b>¿Agregar a qué tipo de venta?</b><br/><br/>`;
            if (producto.codigoNumerico) {
                mtd.append(producto.codigoNumerico);
                mtd.append(document.createElement("br"));
            };
            if (producto.claves) {
                mtd.append(producto.claves);
                mtd.append(document.createElement("br"));
            };
            mtd.append(producto.descripcion);
            mtd.setAttribute("nowrap","nowrap");
            mtd.append(document.createElement("br"));
            let img = generaImagenTipoVenta(producto, tipoVentaId);
            //img.style.marginLeft="20px";
            img.style.marginRight="5px";
            mtd.append(img);
            let precioVenta;
            let ventaDesc;
            const existente = findProductoVenta(producto.productoId, tipoVentaId);
            if (existente){
                console.log(JSON.stringify(existente));
                precioVenta = existente.precioVenta;
                ventaDesc = existente.descVenta;
            } else {
                if (tipoVentaId==-1) {
                    precioVenta= producto.precioUnidad;
                    ventaDesc = producto.descVentaUnidad;
                }
                if (tipoVentaId==-2) {
                    precioVenta= producto.precioPaquete;
                    ventaDesc = producto.descVentaPaquete;
                }
                if (tipoVentaId==-3){
                    precioVenta= producto.precioKg;
                    ventaDesc = producto.descVentaKg;
                }
                producto.precio = parseFloat(precioVenta);
                producto.precioVenta = parseFloat(precioVenta);
                producto.descVenta = ventaDesc;
            }
            mtd.append(ventaDesc);
            mtd.append(document.createElement("br"));
            //divAgregarTipoVenta.append(document.createElement("br"));
            let tb = document.createElement("table");
            let tr = document.createElement("tr");
            let th = document.createElement("th");
            th.innerText="Cantidad";
            tr.append(th);
            th = document.createElement("th");
            th.innerText="Precio";
            tr.append(th);
            th = document.createElement("th");
            th.innerText="Importe";
            tr.append(th);
            tb.append(tr);
            tr = document.createElement("tr");
            let td = document.createElement("td");
            let btn = document.createElement("button");
            btn.innerText="Agregar";
            btn.style.backgroundColor = "lightgreen";
            //btn.textContent = getDescVenta(producto, tv);
            let cantInput = document.createElement("input");
            cantInput.style.width = "100px";
            cantInput.setAttribute("type", "number");
            cantInput.setAttribute("id", "cantIdWindow");
            cantInput.value=1;
            cantInput.setAttribute("step","any");
            td.append(cantInput);
            tr.append(td);
            td = document.createElement("td");
            td.innerText = "$ "+precioVenta;
            tr.append(td);
            td = document.createElement("td");
            let precioInput = document.createElement("input");
            precioInput.style.width = "100px";
            precioInput.setAttribute("type", "number");
            precioInput.value=precioVenta;
            precioInput.setAttribute("step","any");
            btn.onclick = () => {
                let cant = cantInput.value.trim();
                let pre = precioInput.value.trim();
                if (!cant || !pre || parseFloat(cant)<=0 || parseFloat(pre)<=0){
                    return;
                }
                producto.tipoVentaId= tipoVentaId;
                producto.cantidad= parseSmartNumber(cantInput.value,3);
                //console.log("Producto a agregar "+JSON.stringify(producto));
                agregarProducto(producto);
                divAgregarTipoVenta.remove();
                resolve(true);
            };
            function cantChange(){
                precioInput.value = parseSmartNumber(parseFloat(cantInput.value) * precioVenta);
            }
            cantInput.addEventListener('input', cantChange);
            cantInput.addEventListener("keydown", function(e) {
                if (e.key === "Enter") {
                    e.preventDefault();
                    btn.click();
                    return;
                }
                // if (e.key === "+") {
                //     e.preventDefault();
                //     cantInput.value = parseSmartNumber(cantInput.value)+1;
                //     cantChange();
                //     return;
                // }
                // if (e.key === "-") {
                //     e.preventDefault();
                //     cantInput.value = Math.max(parseSmartNumber(cantInput.value)-1,1);
                //     cantChange();
                //     return;
                // }
            });
            function changePrice(){
                const rawQty = parseFloat(precioInput.value) / precioVenta;
                // multiply by 1000, ceil, divide back
                const qty = Math.ceil(rawQty * 1000) / 1000;
                cantInput.value = parseSmartNumber(qty,3);
            }
            precioInput.onchange = changePrice;
            precioInput.addEventListener("keydown", function(e) {
                if (e.key === "Enter") {
                    e.preventDefault();
                    changePrice();
                    btn.click();
                }
            });
            td.append(precioInput);
            tr.append(td);
            tb.append(tr);
            mtd.append(tb);
            tb = document.createElement("table");
            tr = document.createElement("tr");
            td = document.createElement("td");
            td.style.textAlign="center";
            td.append(btn);
            tr.append(td);
            td = document.createElement("td");
            let btnCancel = document.createElement("button");
            btnCancel.setAttribute("id","cancelMostrarTipoVenta");
            btnCancel.textContent = "Cancelar";
            btnCancel.style.backgroundColor = "orange";
            btnCancel.onclick = () => {
                divAgregarTipoVenta.remove();
                resolve(false);
            };
            td.style.textAlign="center";
            td.append(btnCancel);
            tr.append(td);
            tb.append(tr);
            mtd.appendChild(tb);
            mtr.append(mtd);
            mtd = document.createElement("td");
            let imgProd = document.createElement("img");
            if (producto.codigoNumerico){
                imgProd.onload = function () {
                    // Image exists → show it
                    mtd.append(imgProd);
                };
                imgProd.onerror = function () {
                    // Image does NOT exist → do nothing
                    // (image won't be added to DOM)
                };
                imgProd.src=`/static/imagenes/truper/truper_${producto.codigoNumerico}.jpg`;
                imgProd.style.width = "150px";
                imgProd.style.height = "150px";
                imgProd.alt = "Sin imagen";
            }
            mtr.append(mtd);
            mtb.append(mtr);
            divAgregarTipoVenta.append(mtb);
            if (window.thisRol=="maestro"){
                imgProd.style.width = "250px";
                imgProd.style.height = "250px";
                divAgregarTipoVenta.style.top = "200px";
                divAgregarTipoVenta.style.boxShadow = "0 25px 25px rgba(0,0,0,1)";
                divAgregarTipoVenta.style.fontSize = "25px";
                divAgregarTipoVenta.querySelectorAll("*").forEach(el => {
                    el.style.fontSize = "25px";
                });
            }
            document.body.appendChild(divAgregarTipoVenta);
            cantInput.focus();
            cantInput.select();
        });
    }

    actualizarVisibilidadBotones();

    /**** TERMINA DE CARGAR EL DOM ****/

    function renderProductTable(rows, schema) {
        const table = document.createElement("table");

        /* ===== HEADER ===== */
        const thead = document.createElement("thead");
        const trh = document.createElement("tr");

        for (col of schema) {
            //if (col.nonPrintable) return;
            const th = document.createElement("th");
            th.textContent = col.title;
            if (col.class) th.classList.add(col.class);
            trh.appendChild(th);
        }

        thead.appendChild(trh);
        table.appendChild(thead);

        /* ===== BODY ===== */
        const tbody = document.createElement("tbody");

        rows.forEach(row => {
            const tr = renderRow(row, schema);
            tbody.appendChild(tr);
        });

        table.appendChild(tbody);
        return table;
    }

    function renderRow(row, schema) {
    const tr = document.createElement("tr");

    schema.forEach(col => {
        //if (col.nonPrintable) return;

        const td = document.createElement("td");
        td.dataset.col = col.key;

        let val = row[col.key] ?? "";

        if (col.editable) {
            const input = document.createElement("input");
            input.type = col.inputType || "text";
            input.value = val;

                if (col.eventListeners) {
                    col.eventListeners.forEach(listenerObj => {
                    Object.entries(listenerObj).forEach(([event, handler]) => {
                        input.addEventListener(event, e =>
                        handler({
                            row,
                            colKey: col.key,
                            input,
                            tr,
                            event: e
                        })
                        );
                    });
                    });
                }

            td.appendChild(input);
        } else {
            if (col.format) val = col.format(val, row, tr, td);
            td.textContent = val;
        }

        if (col.align) td.style.textAlign = col.align;
        if (col.class) td.classList.add(col.class);
        if (col.classIf) {
        const cls = col.classIf(val, row);
        if (cls) td.classList.add(cls);
        }

        tr.appendChild(td);
    });

    return tr;
    }
});