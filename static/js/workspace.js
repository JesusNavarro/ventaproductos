//console.log("Workspace JS loaded");

let linkWS = document.createElement('link');
linkWS.rel = 'stylesheet';
linkWS.href = '/static/css/workspace.css';
document.head.appendChild(linkWS);

const DEFAULT_VIEW_KEY = "__home__";

if (configDev){
    if (configDev["MS_SOY"]){
        window.thisRol = configDev["MS_SOY"]["rol"];
    }
}

console.log(configDev);
console.log(window.thisRol);
const views = {};
const buttonGroups = {};

function viewKey(groupId, index) {
    return `${groupId}_${index}`;
}

const carritoColors = [
    "teal",
     "#6f42c1", // purple
    //"#6610f2", // deep violet
    "#d63384", // magenta
    "#fd7e14", // orange
    //"#20c997", // mint-green (NOT teal)
    //"#e5533d", // soft red-orange
    "#198754", // dark green
    "lightslategrey"  // gray
];


window.addEventListener("beforeunload", (e) => {
    e.preventDefault();
    e.returnValue = "¿Salir de la aplicación?";
});

function initDefaultView() {
    const workspace = document.getElementById("workspace");
    if (!workspace) return;

    const key = DEFAULT_VIEW_KEY;

    const iframe = document.createElement("iframe");
    iframe.src = "/workspace/home";
    iframe.classList.add("workspace-view", "activeframe");
    iframe.dataset.viewKey = key;

    iframe.onload = () => {
        iframe.contentWindow?.focus();
    };

    workspace.appendChild(iframe);

    views[key] = {
        key,
        groupId: "home",
        index: 0,
        label: "Inicio",          // no label → generic messages
        uiNumber: null,
        route: "/workspace/home",
        iframe,
        button: null          // no button
    };
}

function activateView(key) {
    // Object.values(views).forEach(v => {
    //     v.iframe.classList.remove("activeframe");
    //     v.button?.classList.remove("activebutton");
    Object.values(views).forEach(v => {
        if (v.iframe) {
            v.iframe.classList.remove("activeframe");
        }
        if (v.button) {
            v.button.classList.remove("activebutton");
        }
    });

    const view = views[key];
    if (!view) return;
    console.log(view);
    view.iframe.classList.add("activeframe");
    view.button?.classList.add("activebutton");

    try {
        view.iframe.contentWindow?.focus();
    } catch {}
}

// function btnColorChange(mybutton){
//         document.querySelectorAll('#global-toolbar button').forEach(b =>
//             b.classList.remove('activebutton')
//         );
//         mybutton.classList.add('activebutton');
// }

function comparaUrl(str1, str2){
    if (str1.replace(/\//g, "_")==str2.replace(/\//g, "_"))
        return true;
    return false;
}

function openView({ groupId, index, route, label }) {
    const key = viewKey(groupId, index);

    if (views[key] && views[key].iframe) {
        activateView(key);
        return;
    }

    const iframe = document.createElement("iframe");
    iframe.src = route;
    iframe.classList.add("workspace-view");
    iframe.dataset.viewKey = key;

    document.getElementById("workspace").appendChild(iframe);

    // views[key] = {
    //     key,
    //     groupId,
    //     index,
    //     label,
    //     uiNumber: index === 0 ? null : index + 1,
    //     route,
    //     iframe,
    //     button: null
    // };
    views[key].iframe = iframe;

    activateView(key);
}

function getNextAvailableSiblingIndex(group) {
    // internal indexes used by siblings (>=1)
    const used = group
        .map(btn => Number(btn.dataset.index))
        .filter(i => i >= 1)
        .sort((a, b) => a - b);

    let candidate = 1;
    for (const idx of used) {
        if (idx === candidate) {
            candidate++;
        } else if (idx > candidate) {
            break;
        }
    }
    return candidate;
}

window.addEventListener("message", (event) => {
    if (!event.data || typeof event.data !== "object") return;

    const { type, payload } = event.data;

    if (type === "OPEN_ADHOC_VIEW") {
        const { groupId, route, label, addSequence } = payload;

        if (!groupId || !route || !label) return;

        createAdHocSibling({ groupId, route, label, addSequence });
    }
});


function createAdHocSibling({ groupId, route, label, addSequence=false }) {
    if (!buttonGroups[groupId]) {
        const originBtn = document.createElement("button");
        originBtn.style.display = "none"; // invisible anchor
        document.getElementById("global-toolbar").appendChild(originBtn);

        buttonGroups[groupId] = [originBtn];
        buttonGroups[groupId].confirmClosing = false;
        buttonGroups[groupId].siblingColors = null;
    }

    // 🔴 ADHOC IDENTITY INVALIDATION (this is the key)
    const group = buttonGroups[groupId];
    const index = getNextAvailableSiblingIndex(group);
    const key = viewKey(groupId, index);

    if (views[key]) {
        views[key]?.iframe?.remove(); // safety
        delete views[key];
    }

    createSibling({
        groupId,
        route,
        label,
        maxSiblingButtons: Infinity,
        isAdhoc: true,
        addSequence: addSequence
    });
}

// function createAdHocSibling({ groupId, route, label }) {
//     if (!buttonGroups[groupId]) {
//         buttonGroups[groupId] = [];
//         buttonGroups[groupId].confirmClosing = true;
//         buttonGroups[groupId].siblingColors = null;
//     }

//     const group = buttonGroups[groupId];
//     const index = getNextAvailableSiblingIndex(group);
//     const key = viewKey(groupId, index);
//     const uiNumber = index + 1;

//     const btn = document.createElement("button");
//     btn.classList.add("workspace-btn");
//     btn.dataset.index = index;
//     btn.dataset.viewKey = key;
//     btn.textContent = `${label} ${uiNumber}`;

//     btn.addEventListener("click", () => {
//         openView({ groupId, index, route, label });
//     });

//     // close button
//     const close = document.createElement("span");
//     close.textContent = "✕ ";
//     close.classList.add("btn-close");
//     close.style.cursor = "pointer";
//     close.style.fontWeight = "bold";

//     close.addEventListener("click", e => {
//         e.stopPropagation();
//         activateView(key);

//         setTimeout(() => {
//             if (!confirm(`¿Eliminar ${label} ${uiNumber}?`)) return;

//             views[key]?.iframe?.remove();
//             btn.remove();
//             delete views[key];

//             const idx = group.indexOf(btn);
//             if (idx !== -1) group.splice(idx, 1);
//         }, 0);
//     });

//     btn.prepend(close);

//     views[key] = {
//         key,
//         groupId,
//         index,
//         label,
//         uiNumber,
//         route,
//         iframe: null,
//         button: btn
//     };

//     // insert at end of toolbar
//     document.getElementById("global-toolbar").appendChild(btn);
//     group.push(btn);

//     openView({ groupId, index, route, label });
// }


function createSibling({ groupId, route, label, maxSiblingButtons, isAdhoc = false, addSequence=true }) {
    let group = buttonGroups[groupId];
    console.log(group);
    if (group.length > maxSiblingButtons) return;

    const index = getNextAvailableSiblingIndex(group);
    const key = viewKey(groupId, index);
    //const uiNumber = index + 1;
    const uiNumber = isAdhoc ? index : index + 1;

    const btn = document.createElement("button");
    btn.dataset.index = index;
    btn.classList.add("workspace-btn");
    btn.textContent = `${label} ${addSequence? uiNumber:""}`;
    btn.dataset.viewKey = key;

    const colors = buttonGroups[groupId].siblingColors;
    if (Array.isArray(colors) && colors.length > 0) {
        const colorIndex = index; // siblings start at index 1
        if (colors[colorIndex]) {
            btn.style.backgroundColor = colors[colorIndex];
        }
    }

    btn.addEventListener("click", () => {
        openView({ groupId, index, route, label });
    });

    const close = document.createElement("span");
    close.style.fontWeight="bold";
    close.textContent = "✕ ";
    close.style.cursor = "pointer";
    close.classList.add("btn-close");

    close.addEventListener("click", e => {
        e.stopPropagation();
        activateView(key);

        setTimeout(() => {

            const mustConfirm = buttonGroups[groupId].confirmClosing !== false;
            if (mustConfirm) {
                if (!confirm(`¿Eliminar ${label} ${uiNumber}?`)) return;
            }
            //if (!confirm(`¿Eliminar ${label} ${uiNumber}?`)) return;

            const view = views[key];
            view?.iframe?.remove();
            document.querySelectorAll(`iframe[data-view-key="${key}"]`).forEach(f => f.remove());
            btn.remove();
            delete views[key];
            //group = group.filter(b => b !== btn);
            const idx = group.indexOf(btn);
            if (idx !== -1) group.splice(idx, 1);
        }, 0);
    });

    btn.prepend(close);

    views[key] = {
        key,
        groupId,
        index,
        label,
        uiNumber,
        route,
        iframe: null,
        button: btn,
        isAdhoc 
    };

    group.push(btn);
    //const originBtn = buttonGroups[groupId][0];
    //originBtn.after(btn);

    // insert after last sibling, or after generator if none exist
    // const groupButtons = buttonGroups[groupId];
    // if (groupButtons.length > 1) {
    //     // last sibling is before this new push, so length - 2
    //     const lastSibling = groupButtons[groupButtons.length - 2];
    //     lastSibling.after(btn);
    // } else {
    //     // only generator exists
    //     const generatorBtn = groupButtons[0];
    //     generatorBtn.after(btn);
    // }
    if (isAdhoc) {
        // adhoc buttons are standalone → always append safely
        document.getElementById("global-toolbar").appendChild(btn);
    } else {
        const groupButtons = buttonGroups[groupId];
        // insert after last existing button
        if (groupButtons.length > 1) {
            groupButtons[groupButtons.length - 2].after(btn);
        } else if (groupButtons[0]) {
            groupButtons[0].after(btn);
        } else {
            document.getElementById("global-toolbar").appendChild(btn);
        }
    }
    openView({ groupId, index, route, label });
}

function createGeneratorButton({ groupId, route, label, maxSiblingButtons = 0, confirmClosing = true, siblingColors = null }) {
    if (!buttonGroups[groupId]) {
        buttonGroups[groupId] = [];
    }
    buttonGroups[groupId].confirmClosing = confirmClosing;
    buttonGroups[groupId].siblingColors = siblingColors;

    const index = 0;
    const key = viewKey(groupId, index);

    const btn = document.createElement("button");
    btn.classList.add("workspace-btn");
    btn.textContent = label;
    btn.dataset.viewKey = key;
    if (siblingColors && siblingColors.length>0){
        btn.style.backgroundColor=siblingColors[0];
    }

    btn.addEventListener("click", () => {
        openView({ groupId, index, route, label });
    });

    views[key] = {
        key,
        groupId,
        index,
        label,
        uiNumber: null,
        route,
        iframe: null,
        button: btn
    };

    if (maxSiblingButtons > 0) {
        const plus = document.createElement("span");
        plus.style.fontWeight="bold";
        plus.textContent = "+ ";
        plus.style.cursor = "pointer";
        plus.classList.add("btn-plus");

        plus.addEventListener("click", e => {
            e.stopPropagation();
            createSibling({ groupId, route, label, maxSiblingButtons });
        });

        btn.prepend(plus);
    }

    buttonGroups[groupId].push(btn);
    return btn;
}

function drawGlobalToolbar(){
    let  mydiv = document.getElementById("global-toolbar");
    if (!mydiv) return;

    let maxSib = 0;

    let vender =  createGeneratorButton({
            groupId: "vender",
            label: window.thisRol && window.thisRol=="maestro" ? "Carrito" : "Vender",
            route: "/vender",
            maxSiblingButtons: window.thisRol && window.thisRol=="maestro" ? 4 : 0,
            siblingColors: carritoColors    });
    vender.id="botonVender";
    

    let productos = createGeneratorButton({
            groupId: "productos",
            label: "Productos",
            route: "/producto",
            maxSiblingButtons: window.thisRol && window.thisRol=="maestro" ? 1 : 0,
            confirmClosing: false        });
    

    // let inventario_url = "/inventario";
    // let inventario = document.createElement("button");
    // inventario.textContent="Inventario";
    // inventario.addEventListener("click", function(){
    //     openFlaskRoute(inventario_url);
    //     btnColorChange(inventario);
    // });

    // let pedidos_url = "/pedidos";
    // let pedidos = document.createElement("button");
    // pedidos.textContent="Pedidos";
    // pedidos.addEventListener("click", function(){
    //     openFlaskRoute(pedidos_url);
    //     btnColorChange(pedidos);
    // });

    // let entregas_url = "/entregas";
    // let entregas = document.createElement("button");
    // entregas.textContent="Entregas";
    // entregas.addEventListener("click", function(){
    //     openFlaskRoute(entregas_url);
    //     btnColorChange(entregas);
    // });

    let ajustes = createGeneratorButton({
        groupId: "ajustes",
        label: "Ajustes",
        route: "/ajustes",
        maxSiblingButtons: 0    });
    
    let limpiar = document.createElement("button");
    //limpiar.classList.add("workspace-btn");
    limpiar.textContent="Refrescar";
    //limpiar.style.background="#990033";
    limpiar.classList.add("ice-btn");
    //limpiar.classList.add("ice-cracked");

    limpiar.addEventListener("click", () => {
        const activeView = Object.values(views)
            .find(v => v.iframe?.classList.contains("activeframe"));

        if (!activeView) return;

        const msg = activeView.label
            ? `¿Refrescar ${activeView.label}${activeView.uiNumber ? " " + activeView.uiNumber : ""}?`
            : "¿Refrescar vista?";
        playInteractionSound();
        //playErrorSound();
        //playScanSound();

        if (!confirm(msg)) return;

        activeView.iframe.src = activeView.route;
        activeView.iframe.contentWindow?.focus();
    });


    let ventas_esc_penidentes= createGeneratorButton({
            groupId: "pendientes",
            label: "Tableta",
            route: "/ventas/pendientes",
            maxSiblingButtons: 0        });
    

    let ventas = createGeneratorButton({
            groupId: "ventas",
            label: "Ventas",
            route: "/ventas",
            maxSiblingButtons: 0        });

    let entregas = createGeneratorButton({
            groupId: "entregas",
            label: "Entregas",
            route: "/entregas",
            maxSiblingButtons: 0        });

    let truper = createGeneratorButton({
        groupId: "truper",
        label: "Archivos",
        route: "/truper",
        maxSiblingButtons: 0    });
    
    if (window.thisRol){
        mydiv.appendChild(vender);
    }
    if (window.thisRol && window.thisRol=="maestro") {
        mydiv.appendChild(productos);
        mydiv.appendChild(ventas);
        mydiv.appendChild(ventas_esc_penidentes);
        mydiv.appendChild(truper);
        //mydiv.appendChild(entregas);
        // animaciones para maestro
        vender.classList.add("carrito-btn");
        productos.classList.add("productos-btn");
        ventas.classList.add("ventas-btn");
        ventas_esc_penidentes.classList.add("sync-btn");
        truper.classList.add("archivos-btn");
        ajustes.classList.add("ajustes-btn");
    } else if (window.thisRol && window.thisRol=="esclavo") {
        vender.style.backgroundColor="teal";
        mydiv.appendChild(productos);
        mydiv.appendChild(ventas);
    }

    console.log(mydiv.children);
    console.log(mydiv.children.length);
    if (mydiv.children.length==0){
            mydiv.appendChild(ajustes);
            mydiv.appendChild(limpiar); 
    } else {
        mydiv.appendChild(limpiar); 
        mydiv.appendChild(ajustes);
    }
}


//if (window.thisRol && window.thisRol=="maestro"){
    initDefaultView();
//}
drawGlobalToolbar();

if (window.thisRol && window.thisRol=="esclavo"){
    const botonVender = document.getElementById("botonVender");
    if (botonVender){
        botonVender.click();
    }
}
