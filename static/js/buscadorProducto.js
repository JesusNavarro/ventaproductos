// ----------------------------- Stopwords -----------------------------
const stopwords = [
    "de", "del", "la", "el", "los", "las", "para", "por", "con", "sin",
    "y", "o", "u", "en", "a", "al", "the", "a", "and", "or", "to"
];

const tipoVentas = ["muestraUnidad", "muestraKg", "muestraPaquete"];

productosBuscador = null;

let barcodeBuffer = "";
let lastKeyTime = 0;
let lastTargetWasInput = false;
let inputValorInicial="";
let focusedOnElement = false;
let fastKeyCount = 0;
let lastScannedBarcode = "";

const SCANNER_THRESHOLD_MS = 60;   // time between scanner keystrokes
const MIN_SCANNER_KEYS = 4;        // minimum chars to consider scan

/* begin sortable table */

function makeTableSortable(tableId) {
    const table = document.getElementById(tableId);
    const ths = table.querySelectorAll("thead th");
    const tbody = table.querySelector("tbody");

    let sortState = {};

    ths.forEach((th, colIndex) => {
        th.style.cursor = "pointer";

        th.addEventListener("click", () => {
            const rows = Array.from(tbody.querySelectorAll("tr"));
            const direction = sortState[colIndex] === "asc" ? "desc" : "asc";
            sortState[colIndex] = direction;

            rows.sort((a, b) => {
                const aText = getCellValue(a, colIndex);
                const bText = getCellValue(b, colIndex);

                const aNum = parseSortableNumber(aText);
                const bNum = parseSortableNumber(bText);

                // numeric comparison when possible
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return direction === "asc" ? aNum - bNum : bNum - aNum;
                }

                // string comparison fallback
                return direction === "asc"
                    ? aText.localeCompare(bText, undefined, { numeric: true, sensitivity: "base" })
                    : bText.localeCompare(aText, undefined, { numeric: true, sensitivity: "base" });
            });

            // reattach sorted rows
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

function getCellValue(row, colIndex) {
    const cell = row.children[colIndex];
    return cell ? cell.textContent.trim() : "";
}

function parseSortableNumber(text) {
    // remove currency symbols, units, commas
    const cleaned = text
        .replace(/[^0-9.\-]/g, "")
        .trim();

    return cleaned === "" ? NaN : parseFloat(cleaned);
}

/* end sortable table */

function enableDoubleClickWordDelete(element, options = {}) {

    element.addEventListener("dblclick", function (event) {
        const input = event.target;
        const text = input.value;
        const cursorPos = input.selectionStart;

        // 1. Find word boundaries
        let start = cursorPos;
        let end = cursorPos;

        while (start > 0 && text[start - 1] !== " ") start--;
        while (end < text.length && text[end] !== " ") end++;

        const word = text.slice(start, end).trim();
        if (!word) return;

        // 2. Remove the word
        const before = text.slice(0, start);
        const after = text.slice(end);
        const newText = (before + " " + after).replace(/\s+/g, " ").trim();

        input.value = newText;

        // 3. Place cursor at deletion position
        input.setSelectionRange(start, start);

        // 4. Optional callback
        if (typeof options.onDelete === "function") {
            options.onDelete(word, newText);
        }

        // 🔥 5. Fire input event manually so other listeners run
        const evt = new Event("input", { bubbles: true, cancelable: true });
        input.dispatchEvent(evt);
    });
}

function enableClickAction(btn, textInput, clickAction, selectAction, buscaActivo, paraVenta){
    btn.addEventListener("click", function (e) {
        clickAction(textInput, selectAction, buscaActivo, paraVenta);
    });
}

function enableInputEnterActions(input, inputFunction, enterFunction, selectAction, buscaActivo, paraVenta) {

    input.addEventListener("input", function (e) {
        // if (scanInProgress) {
        //     return; // 🚫 ignore scanner input
        // }
        inputFunction(input, selectAction, buscaActivo);
    });

    input.addEventListener("keydown", async function (e) {
        // if (scanInProgress) {
        //     return; // 🚫 ignore scanner input
        // }
        if (e.key === "Enter") {
            if (input.value.trim()!=''){
                enterFunction(input, selectAction, buscaActivo, paraVenta);
            }
        }
    });

    // // Another reliable fallback
    // input.addEventListener("blur", () => {
    //     enterFunction(input, selectAction, activo);
    // });
}

function enableTableKeyboardNavigation(myTable) {

    if (!myTable) {
        console.error("Table not found:", tableSelector);
        return;
    }

    const rows = Array.from(myTable.querySelectorAll("tr"));

    // Make rows focusable
    //rows.forEach(row => row.tabIndex = 0);

    myTable.addEventListener("keydown", function (e) {
        const currentRow = document.activeElement;
        if (!rows.includes(currentRow)) return;

        const index = rows.indexOf(currentRow);

        // ⬆ UP Arrow → previous row (Shift+Tab behavior)
        if (e.key === "ArrowUp") {
            e.preventDefault();
            if (index > 0) {
                rows[index - 1].focus();
            } //else {
            //     console.log(myTable.tHead);
            //     myTable.tHead.focus();
            //     rows[index].focus();
            // }
        }

        // ⬇ DOWN Arrow or TAB → next row
        if (e.key === "ArrowDown") { //|| e.key === "Tab"
            e.preventDefault();
            if (index < rows.length - 1) {
                rows[index + 1].focus();
            }
        }

    });
}

function normalizeKeepEnye(str) {
  return str
    // protect ñ and Ñ
    .replace(/ñ/g, "__enie__")
    .replace(/Ñ/g, "__ENIE__")

    // normalize and remove diacritics
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")

    // restore ñ and Ñ
    .replace(/__enie__/g, "ñ")
    .replace(/__ENIE__/g, "Ñ");
}

async function productoFind(searchString, buscaActivo) {
    searchString = normalizeKeepEnye(searchString);
    res = await myfetch("/producto/find",  {"searchString":searchString, "buscaActivo": buscaActivo});
    if (res.success) {
        return res.resultado
    }
}

async function productoNumerico(codigo, buscaActivo) {
    res = await myfetch("/producto/find/numerico",  {"codigo":codigo, "buscaActivo": buscaActivo});
    console.log(`productoNumerico ${res}`);
    if (res.success) {
        return res.resultado
    }
}

async function productoArticulo(buscaActivo) {
    res = await myfetch("/producto/find/clave",  {"codigo":"art", "buscaActivo": buscaActivo});
    if (res.success) {
        return res.resultado
    }
}

async function buscarProductoEnterAction(inputBuscador, selectAction, buscaActivo, paraVenta) {
    val = inputBuscador.value.trim();
    if (val.length < 2) {
        alert("Busqueda muy corta");
    } else {
        getTagsBuscador().style.display='';
        getResultsBuscador().style.display='';
        productosBuscador = await productoFind(val, buscaActivo);
        if (productosBuscador){
            if (productosBuscador.length==1 && (!paraVenta || numMuestraVenta(productosBuscador[0])==1)){
                await productoSeleccionado(inputBuscador, productosBuscador[0], selectAction);
            } else if (productosBuscador.length>0){
                onInput(inputBuscador, selectAction, paraVenta, false);
                const table = document.getElementById("resultsBuscador");
                const tbody = table.tBodies[0];
                if (tbody && tbody.rows.length) {
                    tbody.rows[0].focus();
                }
            } else {
                centerMessage(`${val} - no encontrado`);
                if (window.thisRol=="esclavo"){
                    inputBuscador.blur();
                } else if (window.thisRol=="maestro"){
                    inputBuscador.focus();
                }
            }
        } else {
            centerMessage(`${val} - no encontrado`);
            if (window.thisRol=="esclavo"){
                inputBuscador.value='';
                inputBuscador.blur();
            } else if (window.thisRol=="maestro"){
                inputBuscador.focus();
            }
        }
    } 

}

async function buscarProductoCodigoAction(inputBuscador, selectAction, buscaActivo, paraVenta) {
    val = inputBuscador.value.trim();
    if (val.includes("e") || !Number.isInteger(Number(val)) || Number(val)<1000){
        alert("El codigo a buscar es invalido");
        return;
    }
    if (val.length > 0) {
        getTagsBuscador().style.display='';
        getResultsBuscador().style.display='';
        productosBuscador = await productoNumerico(val, buscaActivo);
        if (productosBuscador){
            if (productosBuscador.length==1 && (!paraVenta || numMuestraVenta(productosBuscador[0])==1)){
                await productoSeleccionado(inputBuscador, productosBuscador[0], selectAction);
            } else if (productosBuscador.length>0){
            //if (productosBuscador.length>1 || (productosBuscador.length==1 && (!paraVenta || numMuestraVenta(productosBuscador[0])>1))){
                console.log("buscarProductoCodigoAction "+JSON.stringify(productosBuscador));
                onInput(inputBuscador, selectAction, paraVenta, false);
                const table = document.getElementById("resultsBuscador");
                const tbody = table.tBodies[0];
                if (tbody && tbody.rows.length) {
                    tbody.rows[0].focus();
                }
            } else {
                centerMessage(`${val} - no encontrado`);
                if (window.thisRol=="esclavo"){
                    inputBuscador.value='';
                    inputBuscador.blur();
                } else if (window.thisRol=="maestro"){
                    inputBuscador.focus();
                }
            }
        } else {
            centerMessage(`${val} - no encontrado`);
            if (window.thisRol=="esclavo"){
                inputBuscador.blur();
            } else if (window.thisRol=="maestro"){
                inputBuscador.focus();
            }
        }
    }

}


function parseArtCode(str) {
    const match = str.match(/ART(\d+)(?:-(\d+))?/i);
    if (!match) return null;

    return {
        major: parseInt(match[1], 10),
        // ART5 → minor = 0
        // ART5-1 → minor = 1
        minor: match[2] ? parseInt(match[2], 10) : 0
    };
}

// function sortProductosPorArticulo(productosBuscador) {
//     return productosBuscador.sort((a, b) => {
//         const artA = parseArtCode(a.claves);
//         const artB = parseArtCode(b.claves);

//         // 1️⃣ Both have ART##-##
//         if (artA && artB) {
//             if (artA.major !== artB.major) {
//                 return artA.major - artB.major;
//             }
//             return artA.minor - artB.minor;
//         }

//         // 2️⃣ Only A has ART → A first
//         if (artA && !artB) return -1;

//         // 3️⃣ Only B has ART → B first
//         if (!artA && artB) return 1;

//         // 4️⃣ Neither has ART → fallback string compare
//         return a.claves.localeCompare(b.claves, undefined, {
//             numeric: true,
//             sensitivity: "base"
//         });
//     });
// }

function sortProductosPorArticulo(productosBuscador) {
    return productosBuscador.sort((a, b) => {
        const artA = parseArtCode(a.claves);
        const artB = parseArtCode(b.claves);

        // Both are ART
        if (artA && artB) {
            if (artA.major !== artB.major) {
                return artA.major - artB.major;
            }
            return artA.minor - artB.minor;
        }

        // Safety fallback (should not happen if all are ART)
        if (artA && !artB) return -1;
        if (!artA && artB) return 1;

        return a.claves.localeCompare(b.claves);
    });
}


function generarProductoComunAction(inputBuscador=null, comunAction, buscaActivo, paraVenta){
    getTagsBuscador().style.display='';
    getResultsBuscador().style.display='';
    getTagsBuscador().innerHTML = '';
    //getResultsBuscador().innerHTML = '';
    getResultsBuscador().innerHTML = `<tr><th>Descripcion</th><th>Cantidad</th><th>Precio</th></tr>`;
    let tr = document.createElement("tr");
    let td = document.createElement("td");
    let inputDesc = document.createElement("input");
    inputDesc.setAttribute("type","text");
    inputDesc.classList.add("artComun");
    inputDesc.style.fontSize="25px";
    inputDesc.style.width="300px";
    inputDesc.placeholder="Descripcion";
    inputDesc.value = "Articulo Comun";
    td.append(inputDesc);
    tr.append(td);
    td = document.createElement("td");
    let inputCant = document.createElement("input");
    inputCant.setAttribute("type","number");
    inputCant.setAttribute("min","1");
    inputCant.classList.add("artComun");
    inputCant.style.fontSize="25px";
    inputCant.style.width="100px";
    inputCant.placeholder="Cantidad";
    inputCant.value = 1;
    td.append(inputCant);
    tr.append(td);
    td = document.createElement("td");
    let inputPrecio = document.createElement("input");
    inputPrecio.setAttribute("type","number");
    inputPrecio.setAttribute("min","0.1");
    inputPrecio.classList.add("artComun");
    inputPrecio.style.fontSize="25px";
    inputPrecio.style.width="100px";
    inputPrecio.placeholder="Precio";
    let btnAgregaComun = document.createElement("button");
    inputPrecio.addEventListener("keydown", function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            btnAgregaComun.click();
        }
    });
    td.append(inputPrecio);
    tr.append(td);
    td = document.createElement("td");
    
    btnAgregaComun.setAttribute("id", "btnAgregaComun");
    btnAgregaComun.style.width = "100px";
    btnAgregaComun.style.fontSize="25px";
    btnAgregaComun.textContent = "Agregar";
    btnAgregaComun.setAttribute("tabindex", "-1");
    btnAgregaComun.addEventListener("click", function(){
        if (inputDesc.value.trim()==''){
            inputDesc.focus();
            return;
        }
        if (inputCant.value.trim()==''){
            inputCant.focus();
            return;
        }
        if (inputPrecio.value.trim()==''){
            inputPrecio.focus();
            return;
        }
        productoComunSeleccionado(-1, inputDesc.value, inputCant.value, inputPrecio.value, comunAction);
    });
    td.append(btnAgregaComun);
    tr.append(td);
    getResultsBuscador().append(tr);
    inputPrecio.focus();
}

function renderArticulos(productosBuscador, selectAction){
    getTagsBuscador().style.display='';
    getResultsBuscador().style.display='';
    getTagsBuscador().innerHTML = '';
    getResultsBuscador().innerHTML = '';
    sortProductosPorArticulo(productosBuscador);
    numCols = 4;
    numRows = Math.ceil(productosBuscador.length/numCols);
    for (let i=0; i<numRows; i++){
        let tr = document.createElement("tr");
        for (let j=0; j<numCols; j++){
            let td = document.createElement("td");
            // Para imprimir por renglones de izquierda a derecha y de arriba a abajo
            //let index = i*numCols+j;
            // Para imprimir por columnas de arriba a abajo y de izquierda a derecha
            let index = j * numRows + i;
            if (index<productosBuscador.length){
                let div = document.createElement("div");
                let prod = productosBuscador[index];
                let btnArt = document.createElement("button");
                //btnArt.style.width = "100px";
                let artNumber= /ART(\d+(?:-\d+)?)/.exec(prod.claves);
                btnArt.textContent = artNumber[1];
                btnArt.style.fontSize="20px";
                btnArt.style.fontWeight="bold";
                btnArt.setAttribute("tabindex", "-1");

                btnArt.addEventListener("click", function(event){
                    productoSeleccionado(null, prod, selectAction);
                });
                div.append(btnArt);
                let span = document.createElement("span");
                span.style.marginLeft="10px";
                span.append(prod.descripcion);
                div.append(span);
                td.append(div);
            }
            tr.append(td);
        }
        getResultsBuscador().append(tr);
    }
}

async function buscarProductoArticuloAction(inputBuscador=null, selectAction, buscaActivo, paraVenta=null) {
        getTagsBuscador().style.display='';
        getResultsBuscador().style.display='';
        productosBuscador = await productoArticulo(buscaActivo);
        if (productosBuscador){
            if (productosBuscador.length>1){
                renderArticulos(productosBuscador, selectAction);
            } else if (productosBuscador.length==1){
                productoSeleccionado(inputBuscador, productosBuscador[0], selectAction);
            }
        } 
}

async function buscarProductoInputAction(inputBuscador, selectAction, buscaActivo, paraVenta) {
    val = inputBuscador.value.trim();
    if (val.length>0 && val.split(" ").length>1){
        if ( productosBuscador && productosBuscador.length>0) {
            getTagsBuscador().style.display='';
            getResultsBuscador().style.display='';
            onInput(inputBuscador, selectAction, paraVenta, false);
        }
    }
}

function getTagsBuscador(){
    // tbodyBuscador =  inputBuscador.parentNode.parentNode.parentNode;    // id= buscadorProducto
    // if (tbodyBuscador.rows.length>1){
    //     return tbodyBuscador.rows[1].children[0].children[0].children[0].children[0];   // id = tagsBuscador
    // }
    return document.getElementById("tagsBuscador");
}

function getResultsBuscador(){
    // tbodyBuscador =  inputBuscador.parentNode.parentNode.parentNode;    // id= buscadorProducto
    // if (tbodyBuscador.rows.length>2){
    //     return tbodyBuscador.rows[2].children[0].children[0].children[0];   // id = resultsBuscador
    // }
    return document.getElementById("resultsBuscador");
}

function creaBuscadorProducto(tbodyBusqueda, selectAction, buscaActivo=true, comunAction=null, paraVenta=true) {
    let link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/static/css/buscadorProducto.css';
    document.head.appendChild(link);
    tbodyBusqueda.innerHTML = '';
    rowBuscar = tbodyBusqueda.insertRow();
    let numBotones = 5;
    let anchoFilaBotones = parseInt(100/numBotones); 
    let colSpanRes = 5;
    if (comunAction){
        anchoFilaBotones = parseInt(100/(numBotones+1)); 
        colSpanRes=colSpanRes+1;
    }
    let inputCodigo = document.createElement("input");
    inputCodigo.setAttribute("type", "number");
    inputCodigo.setAttribute("id", "inputCodigo");
    inputCodigo.classList.add("inputCodigo");
    inputCodigo.setAttribute("placeholder", "123 (F1)");
    inputCodigo.style.width = "100px";
    inputCodigo.setAttribute("autocomplete", "off");
    inputCodigo.setAttribute("tabindex", "-1");
    enableInputEnterActions(inputCodigo, function(){}, buscarProductoCodigoAction, selectAction, buscaActivo, paraVenta);

    let btnCodigo= document.createElement("button");
    btnCodigo.setAttribute("id", "btnCodigo");
    btnCodigo.style.width = "100px";
    btnCodigo.textContent = "Codigo";
    btnCodigo.setAttribute("tabindex", "-1");
    enableClickAction(btnCodigo, inputCodigo, buscarProductoCodigoAction, selectAction, buscaActivo, paraVenta);
    let cellCodigo = rowBuscar.insertCell();
    cellCodigo.style.width=anchoFilaBotones+"%";
    cellCodigo.style.textAlign = "center";
    cellCodigo.appendChild(inputCodigo);
    cellCodigo.appendChild(btnCodigo);
    cellCodigo.style.backgroundColor="DarkSlateGray";
    cellCodigo.setAttribute("tabindex", "-1");
    cellCodigo.style.whiteSpace = "nowrap";

    let inputBuscador = document.createElement("input");
    inputBuscador.setAttribute("type", "text");
    inputBuscador.setAttribute("id", "inputBuscador");
    inputBuscador.setAttribute("placeholder", "ABC (F2)");
    inputBuscador.setAttribute("autocomplete", "off");
    inputBuscador.style.width = "250px";
    inputBuscador.setAttribute("tabindex", "-1");
    enableDoubleClickWordDelete(inputBuscador);
    let btnBuscador = document.createElement("button");
    btnBuscador.setAttribute("id", "btnBuscador");
    btnBuscador.style.width = "100px";
    btnBuscador.textContent = "Buscar";
    btnBuscador.setAttribute("tabindex", "-1");
    enableClickAction(btnBuscador, inputBuscador, buscarProductoEnterAction, selectAction, buscaActivo, paraVenta);
    let cellBuscador = rowBuscar.insertCell();
    cellBuscador.style.width=(anchoFilaBotones*2)+"%";
    cellBuscador.style.textAlign = "left";
    cellBuscador.appendChild(inputBuscador);
    cellBuscador.appendChild(btnBuscador);
    //cellBuscador.style.backgroundColor="yellow";
    cellBuscador.setAttribute("tabindex", "-1");
    cellBuscador.style.whiteSpace = "nowrap";
    enableInputEnterActions(inputBuscador, buscarProductoInputAction, buscarProductoEnterAction, selectAction, buscaActivo, paraVenta);

    let btnArticulo = document.createElement("button");
    btnArticulo.setAttribute("id", "btnArticulo");
    btnArticulo.style.width = "100px";
    btnArticulo.textContent = "ART# (F3)";
    btnArticulo.setAttribute("tabindex", "-1");
    btnArticulo.style.backgroundColor="lightblue";
    enableClickAction(btnArticulo, null, buscarProductoArticuloAction, selectAction, buscaActivo, paraVenta);
    let cellArticulo = rowBuscar.insertCell();
    cellArticulo.style.width=anchoFilaBotones+"%";
    cellArticulo.style.textAlign = "center";
    cellArticulo.appendChild(btnArticulo);
    cellArticulo.setAttribute("tabindex", "-1");

    if (comunAction){
        let btnComun = document.createElement("button");
        btnComun.setAttribute("id", "btnComun");
        btnComun.style.width = "110px";
        btnComun.textContent = "Comun (F4)";
        btnComun.setAttribute("tabindex", "-1");
        btnComun.style.backgroundColor="lightpink";
        enableClickAction(btnComun, null, generarProductoComunAction, comunAction, buscaActivo, paraVenta);
        let cellComun = rowBuscar.insertCell();
        cellComun.style.width=anchoFilaBotones+"%";
        cellComun.style.textAlign = "center";
        cellComun.appendChild(btnComun);
        cellComun.setAttribute("tabindex", "-1");
        //cellArticulo.style.textAlign = "center";
    }
    let cellCancelar = rowBuscar.insertCell();
    cellCancelar.style.width=anchoFilaBotones+"%";
    cellCancelar.style.textAlign = "center";
    cellCancelar.setAttribute("tabindex", "-1");
    let btnCancelar = document.createElement("button");
    btnCancelar.setAttribute("id", "btnCancelar");
    btnCancelar.textContent = "Cancelar";
    btnCancelar.setAttribute("tabindex", "-1");
    btnCancelar.title = "Cancelar";
    btnCancelar.addEventListener("click", function(){
        inputCodigo.value='';
        inputBuscador.value='';
        getResultsBuscador().innerHTML='';
        getTagsBuscador().innerHTML='';
        productosBuscador = null;
    });
    cellCancelar.append(btnCancelar);

    let listaTagsBuscador = tbodyBusqueda.insertRow().insertCell();
    listaTagsBuscador.colSpan= colSpanRes;
    listaTagsBuscador.innerHTML = `<table><tbody><tr id="tagsBuscador" style="vertical-align: top; display: none;"></tr></tbody></table>`;
    let listaBuscador = tbodyBusqueda.insertRow().insertCell();
    listaBuscador.colSpan= colSpanRes;
    listaBuscador.innerHTML = `<div style="width: 100%;" ><table id="resultsBuscador" style="width:100%; display: none;" class='zebra'></table></div>`;

    async function scanAction(codigoBarras, selectAction, buscaActivo){
        if (codigoBarras){
            lastScannedBarcode = codigoBarras;
            const producto = await findProductoBarras(codigoBarras, buscaActivo);
            if (producto) {
                selectAction(producto, null, true);
                playScanSound();
            } else {
                centerMessage(`Codigo ${barcodeBuffer} no encontrado`);
                playErrorSound();
            }
            getResultsBuscador().innerHTML = "";
            getTagsBuscador().innerHTML = "";
            productosBuscador = null;
        }
    }

    document.addEventListener(
    "keydown",
    async (e) => {
        const now = Date.now();
        const timeDiff = now - lastKeyTime;
        const focusedElement = document.activeElement;
        const hasFocus = focusedElement &&
            focusedElement !== document.body &&
            focusedElement !== document.documentElement;

        const allowScannerInInput = hasFocus &&
            focusedElement instanceof HTMLInputElement &&
            focusedElement.hasAttribute("data-allow-scanner");

        if (hasFocus && !focusedOnElement){
            inputValorInicial = focusedElement.value;
            focusedOnElement=true;
        }
        /* --------------------------------
        Detect scanner speed
        -------------------------------- */ //SCANNER_THRESHOLD_MS
        if (timeDiff < 100) {  // && e.key.length === 1
            fastKeyCount++;
        } else {
            fastKeyCount = 0;
            barcodeBuffer = "";
        }

        if (e.key.length === 1){
            barcodeBuffer += e.key;
        }

        /* --------------------------------
        CASE 1️⃣: Element focused
        -------------------------------- */
        if (hasFocus) {
            // Only block input IF this looks like scanner input
            // ESTA PARTE LA QUITO PARA TENER LOS CARACTERES QUE UN HUMANO ESCRIBE RAPIDO   
            // if (fastKeyCount > 0) {
            //     e.preventDefault();
            //     e.stopPropagation();
            // }
            // Scanner finished → blur
            if (e.key === "Enter" && fastKeyCount >= MIN_SCANNER_KEYS) {
                // if (focusedElement instanceof HTMLInputElement ||
                //     focusedElement instanceof HTMLTextAreaElement) {
                //     focusedElement.value = inputValorInicial;
                // }
                focusedElement.value = inputValorInicial;
                focusedElement.blur();
                fastKeyCount = 0;
                focusedOnElement=false;
                inputValorInicial="";
                //alert(barcodeBuffer);
                await scanAction(barcodeBuffer, selectAction, buscaActivo);
                //centerMessage("Volver a escanear", 4, "orange");
            }
            lastKeyTime = now;
            return;
        }

        /* --------------------------------
        CASE 2️⃣: No element focused
        → Normal scanner logic
        -------------------------------- */

        // if (timeDiff > 100) {
        //     barcodeBuffer = "";
        // }

        // if (e.key.length === 1) {
        //     barcodeBuffer += e.key;
        // } else 
        if (e.key === "Enter") {
            e.preventDefault();
            e.stopPropagation();
            if (barcodeBuffer.length >= MIN_SCANNER_KEYS) {
                await scanAction(barcodeBuffer, selectAction, buscaActivo);
            }
            barcodeBuffer = "";
            fastKeyCount = 0;
            inputValorInicial="";
            focusedOnElement=false;
        }

        lastKeyTime = now;
    },
    true
    );
    
}

    // ----------------------------- Helpers -----------------------------
function normalizeText(t) {
    return t
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        //.replace(/[.'"]/g, "") //ADDED
        .trim();
}

function tokenWordsFrom(text) {
    return (text.match(/[A-Za-zÁÉÍÓÚÑáéíóúñ0-9\/\.\-']+/g) || []).filter(Boolean);
}

function isUppercaseLike(word) {
    const letters = (word.match(/[A-Za-zÁÉÍÓÚÑáéíóúñ]/g) || []);
    if (letters.length === 0) return false;
    return letters.every(ch => ch === ch.toUpperCase());
}

    // ----------------------------- Main input handler -----------------------------
function onInput(inputBuscador, selectAction, paraVenta, fromHashtag=false) {
    if (productosBuscador && productosBuscador.length>0){
        // Si la caja de texto no termina en espacio, no hagas nada
        valorBusqueda = inputBuscador.value;
        // if (!(/\s$/.test(valorBusqueda))) {
        //   return;
        // }
        const raw = valorBusqueda.trim();
        if (!raw) {
            getResultsBuscador().innerHTML = '';
            getTagsBuscador().innerHTML = '';
            return;
        }

        const inputWordsNorm = raw.split(/\s+/).map(normalizeText).filter(Boolean);
        const filtered = productosBuscador.filter(p => {
            let normDesc;
            if (fromHashtag){
                normDesc = normalizeText(p.descripcion);
            } else {
                normDesc = normalizeText(p.codigoBarras+' '+p.claves+' '+p.descripcion+' '+p.codigoNumerico);
            }
            return inputWordsNorm.every(w => {
                if (fromHashtag){
                    if (/\d/.test(w)){
                    return new RegExp(`(^|[^a-z0-9áéíóúüñ/-])${w}([^a-z0-9áéíóúüñ/-]|$)`, 'i').test(normDesc);
                    } else {
                        return normDesc.includes(w);
                    }
                } else {
                    return normDesc.includes(w);
                }
                //normDesc.includes(w)
                //new RegExp(`\\b${w}\\b`, 'i').test(normDesc)
                
            });
        });
        //console.log("filtered "+filtered);

        renderTable(inputBuscador, filtered, selectAction, paraVenta);
        //console.log(inputBuscador.getAttribute("type"));
        if (inputBuscador.getAttribute("type")!="number"){
            const hashtags = buildHashtagsFromFiltered(filtered, inputWordsNorm);
            renderHashtags(inputBuscador, hashtags, selectAction, paraVenta);
        } else {
             getTagsBuscador().innerHTML = '';
        }
    }
}

async function productoSeleccionado(inputBuscador, producto, selectAction, tipoVentaId=null){
    //const producto = await findProductoId(productoId, buscaActivo);
    let res = false;
    if (producto){
        //console.log(`productoSeleccionado ${buscaActivo} ${producto}`);
        //console.log("selectAction is:", selectAction.toString());
        res = await selectAction(producto, tipoVentaId);
        //console.log("res "+res);
        if (res){
            getResultsBuscador().innerHTML='';
            getTagsBuscador().innerHTML='';
            productosBuscador = null;
            if (inputBuscador){
                inputBuscador.value='';
            }
        }
    } else {
        centerMessage(`Producto con id ${productoId} no encontrado`);
    }
    if (inputBuscador){
        if (window.thisRol=="esclavo"){
            inputBuscador.blur();
        } else if (window.thisRol=="maestro" && res){
            inputBuscador.focus();
        }
    }
    return res;
}

function productoComunSeleccionado(productoId, desc, cant, precio, comunAction){
    comunAction(productoId, desc, cant, precio);
    getResultsBuscador().innerHTML='';
    getTagsBuscador().innerHTML='';
    productosBuscador = null;
}

function renderProdBuscadorRow(inputBuscador, p, selectAction, paraVenta, muestra=null){
    const tr = document.createElement('tr');
    //rowStr = `<td>${p.productoId}</td><td>${p.codigoBarras}</td><td>${p.claves}</td><td><b>${p.descripcion}</b></td><td><b>$ ${p.precio}</b></td>`
    //rowStr += `<td>${p.descVenta}</td><td>${p.existencia}</td><td><input type='button' value='Elegir' onclick='${selectAction(p.productoId)};'/></td>`
    //tr.innerHTML = rowStr;
    //console.log(p.descripcion+" "+parseInt(p.activo));
    tr.setAttribute("tabindex", "0");
    // td = document.createElement('td');
    // td.innerHTML=p.productoId;
    // tr.appendChild(td);
    // td = document.createElement('td');
    // td.innerHTML=p.codigoBarras;
    // tr.appendChild(td);
    const numVentas = numMuestraVenta(p);
    td = document.createElement('td');
    td.innerHTML=p.codigoNumerico;
    //td.setAttribute("rowSpan", numVentas);
    tr.appendChild(td);
    tdDesc = document.createElement('td');
    tdDesc.innerHTML="<b>"+p.descripcion+"</b>";
    //td.setAttribute("rowSpan", numVentas);
    tr.appendChild(tdDesc);
    //console.log(p);
    let img = document.createElement('img');
    let descVenta = "";
    let precio;
    let tipoVentaId = null;
    if (paraVenta){
        if (muestra=="muestraUnidad"){
            img.src = `/static/imagenes/${p.unidadInv}.png`;
            img.setAttribute("title", `${p.unidadInv}`);
            descVenta = p.descVentaUnidad;
            precio = p.precioUnidad;
            tipoVentaId=-1;
        } else if (muestra=="muestraPaquete"){
            img.src = `/static/imagenes/paquete.png`;
            img.setAttribute("title", `${p.descVentaPaquete}`);
            descVenta = p.descVentaPaquete;
            precio = p.precioPaquete;
            tipoVentaId=-2;
        } else if (muestra=="muestraKg"){
            img.src = `/static/imagenes/kg.png`;
            img.setAttribute("title", `kilo`);
            descVenta = p.descVentaKg;
            precio = p.precioKg;
            tipoVentaId=-3;
        }
        img.style.width='25px';
        img.style.height='25px';
        img.style.marginRight = '10px';
        tdDesc.prepend(img);
        td = document.createElement('td');
        td.style.fontWeight="bold";
        //trUni.appendChild(td);
        //td = document.createElement('td');
        td.append("$ "+precio);
        tr.appendChild(td);
        td = document.createElement('td');
        //td.append(img);
        //tr.append(td);
        //td = document.createElement('td');
        td.append(descVenta);
        //trUni.appendChild(td);
        tr.appendChild(td);
    } else {
        let numCols = 0;
        td = document.createElement('td');
        if (p["muestraUnidad"]){
            const wrapper = document.createElement("div");
            //wrapper.style.fontWeight="bold";
            wrapper.style.display = "flex";
            wrapper.style.alignItems = "center";
            //td = document.createElement('td');
            let img = document.createElement('img');
            img.src = `/static/imagenes/${p.unidadInv}.png`;
            img.setAttribute("title", `${p.unidadInv}`);
            img.style.width='25px';
            img.style.height='25px';
            img.style.marginRight = '10px';
            wrapper.append(img);
            wrapper.append("$ "+p.precioUnidad);
            wrapper.append(" "+p.descVentaUnidad);
            td.append(wrapper);
            numCols+=1;
        }       
        tr.append(td);
        td = document.createElement('td');
        if (p["muestraKg"]){
            const wrapper = document.createElement("div");
            //wrapper.style.fontWeight="bold";
            wrapper.style.display = "flex";
            wrapper.style.alignItems = "center";
            img = document.createElement('img');
            img.src = `/static/imagenes/kg.png`;
            img.setAttribute("title", `kilo`);
            img.style.width='25px';
            img.style.height='25px';
            img.style.marginRight = '10px';
            wrapper.append(img);
            wrapper.append("$ "+p.precioKg);
            wrapper.append(" "+p.descVentaKg);
            td.append(wrapper);
            numCols+=1;
        }
        tr.append(td);
        td = document.createElement('td');
        if (p["muestraPaquete"]){
            const wrapper = document.createElement("div");
            //wrapper.style.fontWeight="bold";
            wrapper.style.display = "flex";
            wrapper.style.alignItems = "center";
            img = document.createElement('img');
            img.src = `/static/imagenes/paquete.png`;
            img.setAttribute("title", `${p.descVentaPaquete}`);
            img.style.width='25px';
            img.style.height='25px';
            img.style.marginRight = '10px';
            wrapper.append(img);
            wrapper.append("$ "+p.precioPaquete);
            wrapper.append(" "+p.descVentaPaquete);
            td.append(wrapper);
            numCols+=1;
        }
        tr.append(td);
        // for (i=3; i> (numCols??0); i--){
        //     td = document.createElement('td');
        //     tr.append(td);
        // }
        
    }
    tr.addEventListener("keydown", async function (e) {
        // ENTER → trigger callback
        if (e.key === "Enter") {
            e.preventDefault();
            // if (typeof onEnterCallback === "function") {
            //     onEnterCallback(currentRow, index);
            // }
            let res = await productoSeleccionado(inputBuscador, p, selectAction, tipoVentaId);
            if (!res){
                tr.focus();
            }
        }
    });
    //td = document.createElement('td');
    //console.log(img.innerHTML);
    
    td = document.createElement('td');
    td.innerHTML=p.descExistencia;
    //td.setAttribute("rowSpan", numVentas);
    if (p.existencia<0 || p.existencia<p.minimo){
        td.style.color = 'red';
    }
    tr.appendChild(td);
    //if (configDev && configDev["MS_SOY"] && configDev["MS_SOY"]["rol"] && configDev["MS_SOY"]["rol"]=="esclavo"){
        tdElegir = document.createElement('td');
        //tdElegir.setAttribute("rowSpan", numVentas);
        inputElegir = document.createElement('input');
        inputElegir.setAttribute("type", "button");
        inputElegir.setAttribute("tabindex", "-1");
        inputElegir.value='Elegir';
        inputElegir.id="elegir_"+p.productoId+"_"+Math.abs(tipoVentaId);
        inputElegir.addEventListener("click", function (event) {
            //selectAction(p.productoId);
            productoSeleccionado(inputBuscador, p, selectAction, tipoVentaId);
        });
        inputElegir.style.display='none';
        tdElegir.appendChild(inputElegir);
        tr.appendChild(tdElegir);
    //}
    tr.addEventListener('focus', () => {
        tr.style.backgroundColor='lightgreen';
        //if (window.thisRol=="esclavo"){
            const elegirBotones = resultsTable.querySelectorAll('[id^="elegir_"]');
            elegirBotones.forEach(el => {
                el.style.display='none';
            });
            const elegirBtn = resultsTable.querySelector("#elegir_"+p.productoId+"_"+Math.abs(tipoVentaId));
            if (elegirBtn){
                elegirBtn.style.display='';
            }
        //}
    });
    tr.addEventListener('blur', () => {
        tr.style.backgroundColor='';
    });
    if (parseInt(p.activo)!=1){
        console.log("Inactivo "+p.codigoBarras+" "+p.activo);
        tr.style.color = "red";
        tr.style.backgroundColor = 'yellow !important';
    }
    return tr;
}

    // ----------------------------- Render table -----------------------------
function renderTable(inputBuscador, items, selectAction, paraVenta) {
    resultsTable = getResultsBuscador();
    //console.log(resultsTable);
    resultsTable.innerHTML = '';
    //resultsTable.setAttribute("border-collapse", "collapse");
    //trHead = document.createElement('tr');
    //<th>Id</th><th>Codigo Barras</th> 
    headStr = `<thead><tr style="position: sticky; top: 0;"><th>Codigo</th><th>Descripcion</th>`
    if (paraVenta){
        headStr += `<th>Precio</th><th>Tipo</th>`
    } else {
        headStr += `<th colspan="3">Ventas Posibles</th>`
    }
    headStr += `<th>Existencia</th>`;
    //if (configDev && configDev["MS_SOY"] && configDev["MS_SOY"]["rol"] && configDev["MS_SOY"]["rol"]=="esclavo"){
        headStr += "<th></th>";
    //}
    headStr += `</tr></thead>`;
    //trHead.innerHTML =headStr;
    //trHead.setAttribute("class", "tags-head");
    resultsTable.innerHTML = headStr;
    if (items.length>0){
        tbody = document.createElement('tbody');
        //tbody.setAttribute("overflow","auto");
        //tbody.setAttribute("height","100px");
        //tbody.setAttribute("display","block");
        resultsTable.appendChild(tbody);
        items.forEach(p => {
            if (paraVenta){
                for (muestra of tipoVentas){
                    if (p[muestra]){
                        tr = renderProdBuscadorRow(inputBuscador, p, selectAction, paraVenta, muestra);
                        tbody.append(tr);
                    }
                }
            } else {
                tr = renderProdBuscadorRow(inputBuscador, p, selectAction, paraVenta);
                tbody.append(tr);
            }
        });
        resultsTable.appendChild(tbody);
    }
    enableTableKeyboardNavigation(resultsTable);
    makeTableSortable("resultsBuscador");
}

    // ----------------------------- Build hashtags -----------------------------
    // ONLY CHANGE REQUESTED:
    // alpha = only first 2 tokens per description (original rule)
    // upper, numeric, alnum = ALL tokens across ALL descriptions
function buildHashtagsFromFiltered(filteredProducts, inputWordsNorm) {

    let alphaCollected = [];    // only first 2 per description
    let seenAlpha = new Set();

    let allTokens = [];         // collect ALL tokens for upper/numeric/alnum

    // ---------- classify tokens ----------
    const alpha = [];
    const upper = [];
    const numeric = [];
    const alnum = [];
    const acceptTokensPerProducts = 1;

    for (let p of filteredProducts) {
        const tokens = tokenWordsFrom(p.descripcion);
        // --- collect ALL tokens for non-alpha categories ---
        let indexToken = 0;
        //console.log("Tokens descripcion: " + tokens)
        tokens.forEach(w => {
            const wNorm = normalizeText(w);
            if (!allTokens.includes(wNorm)) {
                if (wNorm && !stopwords.includes(wNorm) && !inputWordsNorm.includes(wNorm)) {
                    //console.log("Index Token : " + indexToken + " " + w);
                    wClean = w.replace(/^[,.'";)+-]+|[,.'";)+-]+$/g, '');//.replace(/[.'"]$/, "");
                    if (/[0-9A-ZÑÁÉÍÓÚ]/.test(wClean)) {
                        //console.log("\t\tClassifying: "+w)
                        if (/^[0-9]+$/.test(wClean)) {
                            numeric.push(wClean);
                            allTokens.push(wNorm);
                            //console.log("\t\tNumeric: " + w)
                        } else if (isUppercaseLike(w.replace(/['\.]/g, ''))) {
                            upper.push(wClean);
                            allTokens.push(wNorm);
                            //console.log("\t\tUpppercase: " + w)
                        } else if (/[0-9]/.test(w)) {
                            alnum.push(wClean);
                            allTokens.push(wNorm);
                            //console.log("\t\tAlNum: " + w)
                        }
                    }

                    if (indexToken < acceptTokensPerProducts) {  //!seenAlpha.has(wNorm) &&
                        //console.log("\t\tNot seen and not taken: "+wNorm)
                        if (!numeric.includes(wClean) && !upper.includes(wClean) && !alnum.includes(wClean)) {
                            //console.log("\t\t\tAlpha: " + wNorm)
                            alpha.push(wClean);     //  alphaCollected.push(w); 
                            allTokens.push(wNorm);
                            indexToken++;
                        }
                    }

                }
            } else {
                indexToken++;
            }

        });

    }

    // ---------- sorting ----------
    const sortFn = (a, b) => normalizeText(a).localeCompare(normalizeText(b));

    alpha.sort(sortFn);
    upper.sort(sortFn);
    numeric.sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
    alnum.sort(sortFn);

    // remove duplicates while keeping order
    const uniq = arr => [...new Set(arr)];

    return {
        alpha: uniq(alpha),
        upper: uniq(upper),
        numeric: uniq(numeric),
        alnum: uniq(alnum)
    };
}

    // ----------------------------- Render hashtags -----------------------------
function renderHashtags(inputBuscador, groups, selectAction, paraVenta) {
    getTagsBuscador().innerHTML = '';

    const order = [
        { key: 'alpha', title: 'Alphabetic', arr: groups.alpha },
        { key: 'upper', title: 'Uppercase', arr: groups.upper },
        { key: 'numeric', title: 'Numeric', arr: groups.numeric },
        { key: 'alnum', title: 'Alphanumeric', arr: groups.alnum }
    ];

    let sectionIndex = 0;
    order.forEach(section => {

        sectionIndex++;

        const arr = section.arr || [];
        if (arr.length === 0) return;

        const secWrap = document.createElement('div');
        secWrap.className = 'tag-row';

        const title = document.createElement('div');
        title.className = 'section-title';
        title.textContent = section.title;

        const tagsDiv = document.createElement('div');
        tagsDiv.className = 'tags-section';

        arr.forEach(tagText => {
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.textContent = tagText;
            tag.title = tagText;

            tag.addEventListener('click', () => {
                const toAppend = normalizeText(tagText);
                const cur = inputBuscador.value.trim();
                inputBuscador.value = cur ? (cur + ' ' + toAppend) : toAppend;
                onInput(inputBuscador, selectAction, paraVenta, true);
                const table = document.getElementById("resultsBuscador");
                const tbody = table.tBodies[0];
                if (tbody && tbody.rows.length) {
                    tbody.rows[0].focus();
                }
            });

            tagsDiv.appendChild(tag);
        });

        //secWrap.appendChild(title);
        secWrap.appendChild(tagsDiv);

        var td = document.createElement("td");
        if (sectionIndex % 2 == 0)
            td.style.backgroundColor = "#1d7e9f60";
        td.appendChild(secWrap);
        getTagsBuscador().appendChild(td);
    });
}

document.addEventListener("keydown", e => {
    if (
        e.target.matches('.inputCodigo') &&
        (e.key === "ArrowUp" || e.key === "ArrowDown")
    ) {
        e.preventDefault();
        return;
    }
    if (e.key === "Escape") {
        e.preventDefault();
        //cerrarModal();   // or clear form, cancel sale, etc.
        let cancelMostrarTipoVenta = document.getElementById("cancelMostrarTipoVenta");
        if (cancelMostrarTipoVenta){
            cancelMostrarTipoVenta.click();
            return;
        }
        let btnCancelar = document.getElementById("btnCancelar");
        if (btnCancelar)
            btnCancelar.click();
        return;
    }
    const shortcuts = {
        F1: () => document.getElementById("inputCodigo").focus(),
        F2: () => document.getElementById("inputBuscador").focus(),
        F3: () => document.getElementById("btnArticulo").click(),
        F4: () => document.getElementById("btnComun")?.click(),
        F10: () => {
            const el = document.activeElement;
            if (
                el &&
                (el instanceof HTMLInputElement ||
                el instanceof HTMLTextAreaElement)
            ) {
                el.value = lastScannedBarcode;
                //el.dispatchEvent(new Event("input", { bubbles: true }));
            }
        }
        //F3: () => document.getElementById("precio").focus(),
    };

    if (shortcuts[e.key]) {
        e.preventDefault();
        shortcuts[e.key]();
        return;
    }
});

// VENDER
// async function findProductoId(productoId, activo=true) {
//     res = await myfetch("/producto/find/id", { "productoId": productoId, "activo": activo })
//     if (res.success && res.resultado.length > 0) {
//         producto = res.resultado[0];
//         //console.log(JSON.stringify(producto));
//         //logDebug("producto ", producto);
//         productoEncontrado(producto);
//     } else {
//         centerMessage(`Id ${productoId} - Producto no encontrado`);
//         //logDebug("Error", res.error);
//     }
// }

// PRODUCTO
async function findProductoId(productoId, buscaActivo=true) {
    if (productoId && parseInt(productoId) > 0) {
        res = await myfetch("/producto/find/id", {"productoId":parseInt(productoId), "buscaActivo": buscaActivo})
        console.log(`findProductoId ${res}`);
        if (res.success && res.resultado.length > 0) {
            const producto = res.resultado[0];
            return producto;
            //console.log(producto);

            //viewVentaProducto(producto);
        }
    } else {
        console.log(`findProductoId ${productoId} NO SE PUDO BUSCAR`);
    }
}

async function findProductoBarras(codigoBarras, buscaActivo=true) {
    res = await myfetch("/producto/find/barras", { "codigoBarras": codigoBarras, "buscaActivo": buscaActivo })
    console.log(`findProductoBarras ${res}`);
    if (res.success && res.resultado.length > 0) {
        producto = res.resultado[0];
        //console.log(producto)
        //logDebug("producto ", producto);
        //productoEncontrado(producto);
        return producto;
    }
}