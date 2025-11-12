// mac_scanner.js
export function MacScanner(divScanner, estadoElem, onResult, logFn, btnEscanear) {
    let scanner = null;
    let countdownInterval;
    let remainingSeconds = 60;
    let active = false;

    function start() {
        if (active) return;
        active = true;
        divScanner.style.display = "block";
        divScanner.innerHTML = "";

        const scannerDiv = document.createElement("div");
        scannerDiv.id = "scanner-mac";
        divScanner.appendChild(scannerDiv);

        scanner = new Html5Qrcode("scanner-mac");
        Html5Qrcode.getCameras()
            .then(devices => {
                if (!devices || !devices.length) {
                    estadoElem.innerText = "No se encontró ninguna cámara.";
                    active = false;
                    return;
                }
                const camId = devices[0].id;
                scanner
                    .start(
                        camId,
                        { fps: 10, qrbox: { width: 400, height: 200 } },
                        code => {
                            if (scanningEnabled) {
                                scanningEnabled = false
                                setTimeout(() => scanningEnabled = true, SCAN_DELAY);  // 🔹 2-second delay
                                onResult(code);
                                resetTimer();
                            }
                        },
                        err => {}
                    )
                    .then(() => {
                        estadoElem.innerText = "Cámara iniciada (Html5-Qrcode)";
                        btnEscanear.innerText = "Detener cámara";
                        startTimer();
                    })
                    .catch(err => {
                        console.error("Html5-Qrcode error", err);
                        estadoElem.innerText = "Error iniciando cámara.";
                    });
            })
            .catch(err => {
                console.error("Camera error", err);
                estadoElem.innerText = "Error al obtener cámaras.";
            });
    }

    function stop() {
        if (!active) return;
        clearInterval(countdownInterval);
        active = false;
        if (scanner) scanner.stop().catch(() => {});
        divScanner.style.display = "none";
        estadoElem.innerText = ""; //"Escaneo detenido";
        btnEscanear.innerText = "Escanear productos";
    }

    function startTimer() {
        remainingSeconds = 60;
        clearInterval(countdownInterval);
        countdownInterval = setInterval(() => {
            remainingSeconds--;
            estadoElem.innerText = `Cámara activa (Mac) (${remainingSeconds}s)`;
            if (remainingSeconds <= 0) stop();
        }, 1000);
    }

    function resetTimer() {
        remainingSeconds = 60;
    }

    function isActive() {
        return active;
    }

    return { start, stop, resetTimer, isActive };
}
