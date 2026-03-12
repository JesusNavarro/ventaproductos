
// let productTemplate = `
// <tr>
//     <td id="td_codigoNumerico">CODIGO</td>
//     <td colspan="5" id="td_descripcion">DESCRIPCION</td>
//     <td colspan="2" id="td_codigoBarras">BARRAS</td>
// </tr>
// <tr>
//     <td id="td_preferenciaVenta">PREFERIDA</td>
//     <td id="td_seCompraPor">PIEZA/PAQUETE</td>
//     <td id="td_numeroUnidades">UNIDADES</td>
//     <td id="td_unidadInv">UNIDAD</td>
//     <td id="td_numeroKgs">KGS</td>
//     <td>Kgs</td>
//     <td colspan="2" id="td_claves">CLAVES</td>
// </tr>
// <tr>
//     <th></th>
//     <th></th>
//     <th>COSTO</th>
//     <th>IVA</th>
//     <th>COSTO IVA</th>
//     <th>PRECIO</th>
//     <th>GANANCIA</th>
//     <th>EXISTENCIA</th>
// </tr>
// <tr>
//     <th>PAQUETE</th>
//     <td id="td_hayExistenciaPaquetes"></td>
//     <td id="td_hayCostoSinIvaPaquete">COSTO</td>
//     <td id="td_hayIvaPaquete">IVA</td>
//     <td id="td_hayCostoPaquete">COSTO IVA</td>
//     <td id="td_hayPrecioPaquete">PRECIO</td>
//     <td id="td_hayGananciaPaquete">GANANCIA</td>
//     <td></td>
// </tr>
// <tr>
//     <td id="td_muestraPaquete">VENTA</td>
//     <td id="td_llegaExistenciaPaquetes"></td>
//     <td id="td_llegaCostoSinIvaPaquete">COSTO</td>
//     <td id="td_llegaIvaPaquete">IVA</td>
//     <td id="td_llegaCostoPaquete">COSTO IVA</td>
//     <td id="td_llegaPrecioPaquete">PRECIO</td>
//     <td id="td_llegaGananciaPaquete">GANANCIA</td>
//     <td></td>

// </tr>
// <tr>
//     <td id="td_minimoPaquetes">MINIMO</td>
//     <td id="td_existenciaPaquetes"></td>
//     <td id="td_costoSinIvaPaquete">COSTO</td>
//     <td id="td_ivaPaquete">IVA</td>
//     <td id="td_costoPaquete">COSTO IVA</td>
//     <td id="td_precioPaquete">PRECIO</td>
//     <td id="td_gananciaPaquete">GANANCIA</td>
//     <td></td>
// </tr>
// <tr>
//     <th>PIEZA</th>
//     <td id="td_hayExistenciaUnidades"></td>
//     <td id="td_hayCostoSinIvaUnidad">COSTO</td>
//     <td id="td_hayIvaUnidad">IVA</td>
//     <td id="td_hayCostoUnidad">COSTO IVA</td>
//     <td id="td_hayPrecioUnidad">PRECIO</td>
//     <td id="td_hayGananciaUnidad">GANANCIA</td>
//     <td></td>
// </tr>
// <tr>
//     <td id="td_muestraUnidad">VENTA</td>
//     <td id="td_llegaExistenciaUnidades"></td>
//     <td id="td_llegaCostoSinIvaUnidad">COSTO</td>
//     <td id="td_llegaIvaUnidad">IVA</td>
//     <td id="td_llegaCostoUnidad">COSTO IVA</td>
//     <td id="td_llegaPrecioUnidad">PRECIO</td>
//     <td id="td_llegaGananciaUnidad">GANANCIA</td>
//     <td></td>

// </tr>
// <tr>
//     <td id="td_minimoUnidades">MINIMO</td>
//     <td id="td_existenciaUnidades"></td>
//     <td id="td_costoSinIvaUnidad">COSTO</td>
//     <td id="td_ivaUnidad">IVA</td>
//     <td id="td_costoUnidad">COSTO IVA</td>
//     <td id="td_precioUnidad">PRECIO</td>
//     <td id="td_gananciaUnidad">GANANCIA</td>
//     <td></td>
// </tr>
// <tr>
//     <th>KILO</th>
//     <td id="td_hayExistenciaKgs"></td>
//     <td id="td_hayCostoSinIvaKg">COSTO</td>
//     <td id="td_hayIvaKg">IVA</td>
//     <td id="td_hayCostoKg">COSTO IVA</td>
//     <td id="td_hayPrecioKg">PRECIO</td>
//     <td id="td_hayGananciaKg">GANANCIA</td>
//     <td></td>
// </tr>
// <tr>
//     <td id="td_muestraKg">VENTA</td>
//     <td id="td_llegaExistenciaKgs"></td>
//     <td id="td_llegaCostoSinIvaKg">COSTO</td>
//     <td id="td_llegaIvaKg">IVA</td>
//     <td id="td_llegaCostoKg">COSTO IVA</td>
//     <td id="td_llegaPrecioKg">PRECIO</td>
//     <td id="td_llegaGananciaKg">GANANCIA</td>
//     <td></td>
// </tr>
// <tr>
//     <td id="td_minimoKgs">MINIMO</td>
//     <td id="td_existenciaKgs"></td>
//     <td id="td_costoSinIvaKg">COSTO</td>
//     <td id="td_ivaKg">IVA</td>
//     <td id="td_costoKg">COSTO IVA</td>
//     <td id="td_precioKg">PRECIO</td>
//     <td id="td_gananciaKg">GANANCIA</td>
//     <td></td>
// </tr>`;

/* =========================================================
   TABLE ENGINE
   Schema-driven, editable, computed, template-capable
   ========================================================= */
/* =========================================================
   TABLE ENGINE (Always Synced Data Model)
   ========================================================= */

function createSectionFromTemplate(htmlString, hasSectionTemplate) {
  const template = document.createElement("template");
  template.innerHTML = htmlString.trim();
  let objSection = template.content.cloneNode(true);
  // if (hasSectionTemplate){
  //   let rows = objSection.querySelectorAll("tr");
  //   rows.forEach((tr, index) => {
  //     if (index === 0) {
  //       tr.classList.add("render-section-start");
  //     }
  //     if (index === rows.length - 1) {
  //       tr.classList.add("render-section-end");
  //     }
  //   });
  // }
  return objSection;
}

function renderProductTable(
  objetos = [],
  columnas = null,
  sectionTemplate = null,
  sectionColumn = "productoId") {

  if (!objetos?.length) {
    return;
  }

  columnas = generateColumnsFromRows(objetos, columnas);

  const table = document.createElement("table");

  /* ==========================
     HEADER (only if no template)
  ========================== */
  let hasSectionTemplate = false;
  if (!sectionTemplate) {
    const thead = document.createElement("thead");
    const trHead = document.createElement("tr");
    sectionTemplate = document.createElement("tr");
    columnas
      .forEach(col => {
        const th = document.createElement("th");
        th.textContent = col.title;
        if (col.titleClass) th.classList.add(col.titleClass);
        trHead.appendChild(th);
        const td = document.createElement("td");
        td.setAttribute("id", `td_${col.key}`);
        sectionTemplate.append(td);
      });

    thead.appendChild(trHead);
    table.appendChild(thead);
    sectionTemplate = sectionTemplate.outerHTML;
  } else {
    hasSectionTemplate = true;
  }

  /* ==========================
     BODY
  ========================== */

  const tbody = document.createElement("tbody");
  let idxSection =0;
  objetos.forEach(obj => {
      const sectionKey = obj[sectionColumn];
      
      //tbody.setAttribute("id", "tb_"+sectionKey);
      //let tr = document.createElement("tr");
      //let td = document.createElement("td");
      //td.setAttribute("colSpan");
      //td.innerHTML=sectionKey;
      //tr.append(td);
      //tbody.append(tr);
      
      //tr = document.createElement("tr");
      //td = document.createElement("td");
      //const innertable = document.createElement("table");
      //innertable.classList.add("zebra");
      //const tbodyDetalle = document.createElement("tbody");
      //innertable.setAttribute("id", "tbd_"+sectionKey);
      let objectSection = createSectionFromTemplate(sectionTemplate, hasSectionTemplate);
      idxSection+=1;
      columnas.forEach(col => {
          let td = objectSection.querySelector(`[id^='td_${col.key}']`);
          if (td){
            td.style.textAlign="center";
            renderCell(obj, sectionKey, td, col, idxSection);
            td.setAttribute("id", `cel_${sectionKey}_${col.key}`);
          }
      });
      //innertable.appendChild(objectSection);
      //td.append(innertable);
      //tr.append(td);
      //tbody.append(tr);
      //tbodyDetalle.style.display="none";
      tbody.appendChild(objectSection);
  });
  table.append(tbody);
  return table;
}

function getPTInputsGroup(sectionKey, groupClass){
  return document.body.querySelectorAll(`[id^='ip_${sectionKey}_']${groupClass?"."+groupClass:""}`);
}

function getPTInput(sectionKey, colKey){
  return document.body.querySelector(`[id^='ip_${sectionKey}_${colKey}']`);
}

function getPTCelda(sectionKey, colKey){
  return document.body.querySelector(`[id^='cel_${sectionKey}_${colKey}']`);
}

function getPTInputs(container, colKey) {
  const pattern = new RegExp(`^ip_\\d+_${colKey}$`);
  return [...container.querySelectorAll("[id^='ip_']")]
    .filter(el => pattern.test(el.id));
}

function renderCell(obj, sectionKey, td, col, idxSection) {
  if (col.tdalign) td.style.textAlign = col.tdalign;
  if (col.tdclass) td.classList.add(col.tdclass);
  if (col.control) {
    createControl(obj, col, sectionKey, td);
  } else {
    if (col.format) {
      let value = col.format(obj[col.key], obj, td, col, idxSection);
      td.append(value);
    } else {
      if (obj.hasOwnProperty(col.key)){
        td.textContent = obj[col.key] ?? "";
      }
    }
  }
}

function lockField(el) {
  if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
    if (el.type === "checkbox" || el.type === "radio") {
      el.style.pointerEvents = "none";
    } else {
      el.readOnly = true;
    }
  }

  if (el.tagName === "SELECT") {
    el.style.pointerEvents = "none";
  }
}

function createControl(obj, col, sectionKey, td) {
  let input;
  if (col.control[0] === "button") {
    input = document.createElement("button");
    input.textContent = col.control[1];
  } else if (col.control[0] === "span") {
    input = document.createElement("span");
    input.innerHTML = obj[col.key] ?? "";
  } else if (col.control[0] === "select") {
    input = document.createElement("select");
    col.control[1]?.forEach(opt => {
      input.add(new Option(opt[1], opt[0]));
    });
    input.value = obj[col.key] ?? null;
  } else if (col.control[0] === "checkbox") {
    input = document.createElement("input");
    input.setAttribute("type", "checkbox");
    input.checked = obj[col.key] ?? false;
    td.textContent=col.title;
  } else if (col.control[0] === "text") {
    input = document.createElement("input");
    input.setAttribute("type", "text");
    input.value = obj[col.key] ?? "";
  } else if (col.control[0] === "number") {
    input = document.createElement("input");
    input.setAttribute("type", "number");
    input.step="any";
    input.value = obj[col.key] ?? "";
  }
  if (col.ctrlclass){
    for (let f of col.ctrlclass){
      input.classList.add(f);
      if (f==="locked"){
        lockField(input);
      } 
    }
  }
  input.classList.add(col.ctrlclass);
  input.setAttribute("id", `ip_${sectionKey}_${col.key}`);
  input.style.marginLeft="15px";
  input.style.marginRight="15px";
  if (col.listeners) {
    col.listeners.forEach(listenerObj => {
      Object.entries(listenerObj).forEach(([event, handler]) => {
        input.addEventListener(event, e =>
          handler({
            obj,
            col,
            input,
            event: e,
            sectionKey
          })
        );
      });
    });
  }
  td.appendChild(input);
  if (col.postCreate) {
    col.postCreate({input, obj, col, sectionKey, td });
  }
}

function generateColumnsFromRows(objetos, columnas) {
  if (!objetos?.length) return [];
  if (columnas?.length){
    columnas.forEach(col => {
      if (!col.title)
        col.title = toTitleCase(col.key);
    });
    return columnas;
  }
  return Object.keys(objetos[0]).map(key => ({
    key,
    title: toTitleCase(key)
  }));
}

function executeAfterLoad(table, afterLoad) {
  if (!table || !afterLoad) return;
  Object.entries(afterLoad).forEach(([colKey, listeners]) => {
    let inputs = getPTInputs(table, colKey);
    inputs.forEach(input => {
      listeners.forEach(listener => {
        input.dispatchEvent(new Event(listener));
      });
    });
  });
}
