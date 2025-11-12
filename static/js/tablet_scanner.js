// tablet_scanner.js
export function TabletScanner(divScanner, estadoElem, onResult, logFn, btnEscanear) {
    let html5QrcodeScanner = null;
    let countdownInterval = null;
    let remainingSeconds = 60;
    let active = false;
    const SCAN_DELAY = 2000;

    if (!divScanner.id) divScanner.id = "html5qrcode-tablet-" + Date.now();
    const divId = divScanner.id;

    // Make sure div has fixed size for mobile browsers
    divScanner.style.width = divScanner.style.width || "100%";
    divScanner.style.height = divScanner.style.height || "200px";
    divScanner.style.background = divScanner.style.background || "black";

    async function start(cameraType) {
        if (active) return;

        try {
            logFn && logFn("START CAMERA", cameraType);
            divScanner.style.display = "block";
            await new Promise(resolve => requestAnimationFrame(resolve));

            if (btnEscanear) btnEscanear.innerText = "Detener cámara";

            if (!html5QrcodeScanner) html5QrcodeScanner = new Html5Qrcode(divId);

            const devices = await Html5Qrcode.getCameras();
            //logFn && logFn("Detected cameras", devices);

            if (!devices || !devices.length) {
                estadoElem.innerText = "No se encontró ninguna cámara.";
                return;
            }

            // Select camera based on cameraType
            let selectedCamera;
            if (cameraType === "front") {
                selectedCamera = devices.find(d => /front|user/i.test(d.label)) || devices[0];
                //const video = divScanner.querySelector("video");
                //if (video) video.style.transform = "scaleX(-1)";
            } else {
                selectedCamera = devices.find(d => /back|rear|environment/i.test(d.label)) || devices[0];
                const video = divScanner.querySelector("video");
                if (video) video.style.transform = "";
            }
            logFn && logFn("Using camera", selectedCamera);

            active = true;
            startTimer(cameraType);
            estadoElem.innerText = "Cámara iniciada";

            html5QrcodeScanner.start(
                { deviceId: { exact: selectedCamera.id } },
                {
                    fps: 10,
                    qrbox: 250,
                    experimentalFeatures: { useBarCodeDetectorIfSupported: true }
                },
                (decodedText) => {
                    onResult(decodedText);

                    // Throttle scan
                    html5QrcodeScanner.pause();
                    setTimeout(() => {
                        html5QrcodeScanner.resume();
                    }, SCAN_DELAY);
                },
                (errorMessage) => {
                    // Optional decode errors
                }
            ).catch(err => {
                logFn && logFn("Html5Qrcode start warning (non-fatal)", err);
            });

        } catch (err) {
            logFn && logFn("Html5Qrcode start try/catch error", err);
            estadoElem.innerText = "Error al iniciar cámara.";
            if (btnEscanear) btnEscanear.innerText = "Escanear código";
            active = false;
        }
    }

    async function stop() {
        if (!active) return;
        clearInterval(countdownInterval);

        if (html5QrcodeScanner) {
            try {
                await html5QrcodeScanner.stop();
                await html5QrcodeScanner.clear();
            } catch (err) {
                logFn && logFn("Html5Qrcode stop/clear error", err);
            }
        }

        active = false;
        divScanner.style.display = "none";
        if (btnEscanear) btnEscanear.innerText = "Escanear código";
        estadoElem.innerText = "Escaneo detenido";
    }

    function startTimer(cameraType) {
        remainingSeconds = 60;
        clearInterval(countdownInterval);
        countdownInterval = setInterval(() => {
            remainingSeconds--;
            estadoElem.innerText = `Cámara activa ${cameraType} (${remainingSeconds}s)`;
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
