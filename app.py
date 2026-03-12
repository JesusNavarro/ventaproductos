import subprocess
import sys
import os
import csv
import signal
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, Response, after_this_request
from datetime import datetime
import time
import errno
import services.businessLogic as bl
import config
import requests
from escpos.printer import Usb
from escpos.printer import Win32Raw
import base64
from PIL import Image
import io
import unicodedata

import logging
logging.getLogger("werkzeug").disabled = True

app = Flask(__name__)

def myRenderTemplate(templateFile):
    return render_template(templateFile, configDev=config.DEVICE, thisIP =config.THIS_IP)

@app.post("/jobs/start")
def start_job():
    data = request.json
    job_id = bl.startJob(data["script"], data["params"])
    return jsonify({"job_id": job_id})

@app.get("/jobs/<job_id>/status")
def job_status(job_id):
    job = bl.jobStatus(job_id)
    return jsonify(job)

@app.get("/jobs/<job_id>/result")
def job_result(job_id):
    return jsonify(bl.jobResult(job_id))

def ensure_init_py(folder_path):
    """
    Ensures folder_path/__init__.py exists.
    Safe to call repeatedly.
    """
    init_file = os.path.join(folder_path, "__init__.py")
    if not os.path.exists(init_file):
        open(init_file, "a").close()

def get_printer():
    # Gprint BT-58UB common USB IDs
    return Usb(
        idVendor=0x0483, # may vary
        idProduct=0x5743, # may vary
        timeout=0,
        in_ep=0x81,
        out_ep=0x01
    )
"""
@app.route("/print/ticket", methods=["POST"])
def print_ticket():
    data = request.json
    p = Win32Raw("POS58 Printer") # usa el nombre exacto
    print(p)
    print(f"/print/ticket {data}")
    for row in data["items"]:
        if len(row) < 3:
            continue
        qty, name, amount = row
        p.text(f"{qty:>2} {name[:20]:<20} {amount:>7}\n")
    # ---- TOTAL ----
    #p.text("--------------------------------\n")
    p.set(align="right")
    p.text(f"TOTAL: {data['total']}\n")
    # ---- FINISH ----
    p._raw(b'\x1b\x4a\x30') # small bottom margin
    print("finished printing")
    #p._raw(b'\x1b\x4a\x30') # ESC J 48
    # Partial cut, no feed
    #p._raw(b'\x1d\x56\x01') # GS V 1
    #p.cut()
    p._raw(b'\x1d\x56\x01')
    p.close()
    return jsonify({"status": "printed"})
"""
def normalize_text(text: str) -> str:
    if not text:
        return ""
    return (
        unicodedata
        .normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
    )

@app.route("/print/ticket", methods=["POST"])
def print_ticket():
    data = request.get_json(force=True)

    lines = data.get("lines", [])
    if not lines:
        return jsonify({"error": "No lines to print"}), 400

    p = Win32Raw("POS58 Printer")  # usa el nombre exacto

    print("/print/ticket received lines:")
    for l in lines:
        print(repr(l))

    # ---- PRINT ALL LINES AS-IS ----
    for line in lines:
        clean = normalize_text(line)
        p.text(clean + "\n")

    # ---- SMALL FEED ----
    #p._raw(b'\x1b\x4a\x30')  # ESC J 48

    # ---- PARTIAL CUT ----
    p._raw(b'\x1d\x56\x01')  # GS V 1

    p.close()
    print("finished printing")

    return jsonify({"status": "printed"})    

@app.route("/print/image", methods=["POST"])
def print_image():
    PRINTER_WIDTH = 400  # 58mm printers
    data = request.json["image"]
    image_bytes = base64.b64decode(data.split(",")[1])
    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    if img.width > PRINTER_WIDTH:
        ratio = PRINTER_WIDTH / img.width
        img = img.resize(
            (PRINTER_WIDTH, int(img.height * ratio)),
            Image.LANCZOS
        )
    p = Win32Raw("POS58 Printer")
    p._raw(b'\x1b\x61\x01')  # ESC a 1 → CENTER
    p.image(img, impl="bitImageRaster")
    p._raw(b'\x1b\x61\x00')  # back to LEFT
    #p.text("\n")
    p._raw(b'\x1b\x4a\x30') # small bottom margin
    #p.cut()
    #p.cut(mode="PART")
    p._raw(b'\x1d\x56\x01')
    p.close()
    return {"status": "ok"}

# VARIABLES FOR FILE LOCATIONS AND APP LOCATION are in config.py and automatically loaded


with open(config.LOG_FILE_PATH, "w") as f:
    f.write("Logging started fresh.\n")

class TimestampedWriter:
    def __init__(self, file):
        self.file = file

    def write(self, message):
        if message.strip():  # skip blank lines
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
            for line in message.rstrip().splitlines():
                self.file.write(f"{timestamp}{line}\n")
        self.file.flush()

    def flush(self):
        self.file.flush()

sys.stdout = TimestampedWriter(open(config.LOG_FILE_PATH, "a"))
sys.stderr = TimestampedWriter(open(config.LOG_FILE_PATH, "a"))

# -----------------------------------------------------------
# Routes
# -----------------------------------------------------------
@app.route("/")
def index():
    return myRenderTemplate("index.html")

@app.route("/workspace")
def workspace():
    return myRenderTemplate("workspace.html")

@app.route("/workspace/home")
def home():
    return myRenderTemplate("home.html")

@app.route("/entregas")
def entregas():
    return myRenderTemplate("entregas.html")

@app.route("/entregas/cargar", methods=["POST"])
def entregas_cargar():
    return jsonify(bl.entregasCargar(request.get_json()))

@app.route("/entregas/buscar", methods=["POST"])
def entregas_buscar():
    return jsonify(bl.entregasBuscar(request.get_json()))

@app.route("/print")
def print_home():
    return myRenderTemplate("ticket_poc.html")

@app.route("/config/device", methods=["POST"])
def config_device():
    return jsonify({"success": True, "resultado": config.DEVICE})

@app.route("/give/db/maestro", methods=["POST"])
def give_base_maestro():
    print("/give/db/maestro")
    print("give_db called")
    if config.soyRol(config.MAESTRO_NAME) and config.tengoRol(config.ESCLAVO_NAME):
        start = datetime.now()
        print("BackupMaestro Start:", start)
        res = bl.backup_maestro()
        end = datetime.now()
        print("BackupMaestro End:", end)
        diff = end - start
        print("BackupMaestro Difference:", diff.total_seconds(), "seconds")
        print(f"To Return {config.BASE_MAESTRO_BACKUP_PATH}")
        print(f"Path exists: {os.path.exists(config.BASE_MAESTRO_BACKUP_PATH)}")
        if res["success"]:
            # @after_this_request
            # def cleanup(response):
            #     if os.path.exists(config.BASE_MAESTRO_BACKUP_PATH):
            #         os.remove(config.BASE_MAESTRO_BACKUP_PATH)
            #     return response
            return send_file(
                config.BASE_MAESTRO_BACKUP_PATH,
                as_attachment=True,
                download_name=config.BASE_MAESTRO_FILE
            )
        # with open(f"{config.APP_FOLDER}/db/models/base_maestro.db", "rb") as f:
        #     data = f.read()
        # return Response(
        #     data,
        #     mimetype="application/octet-stream",
        #     headers={"Content-Disposition": "attachment; filename=base_maestro.db"}
        # )

@app.route("/pull/db/maestro", methods=["POST"])
def get_base_maestro():
    print("sync_from_master")
    if config.soyRol(config.ESCLAVO_NAME) and config.tengoRol(config.MAESTRO_NAME):
        maestroIP = config.DEVICE["MS_MAESTROS"][0]["direccionIP"]
        url = rf"http://{maestroIP.strip()}:5000/give/db/maestro"
        print(url)
        try:
            print("About to POST...")
            #response = requests.post(url, timeout=5)
            start = datetime.now()
            print("/pull/db/maestro Start:", start)
            response = requests.post(url, stream=True, timeout=300)
            end = datetime.now()
            print("/pull/db/maestro End:", end)
            diff = end - start
            print("/pull/db/maestro Difference:", diff.total_seconds(), "seconds")
            print("POST returned")
            print(response.status_code)
            print(response)
            if response.status_code != 200:
                print("Error syncing:", response.text)
                return {"success": False , "error": response.text}
            print("Hubo respuesta")
            print(config.BASE_MAESTRO_BACKUP_PATH)
            print(config.BASE_MAESTRO_PATH)
            temp_path = config.BASE_MAESTRO_BACKUP_PATH
            final_path = config.BASE_MAESTRO_PATH
            # Save in temp file
            # with open(temp_path, "wb") as f:
            #     f.write(response.content)
            start = datetime.now()
            print("Write received backup Start:", start)
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            response.close()  # 🔴 THIS IS CRITICAL
            end = datetime.now()
            print("Write received backup End:", end)
            diff = end - start
            print("Write received backup Difference:", diff.total_seconds(), "seconds")
            # # Replace DB safely
            print(f"Path exists: {os.path.exists(config.BASE_MAESTRO_BACKUP_PATH)}")
            print(f"Path exists: {os.path.exists(config.BASE_MAESTRO_PATH)}")
            start = datetime.now()
            print("Replace backup Start:", start)
            os.replace(temp_path, final_path)
            end = datetime.now()
            print("Replace backup End:", end)
            diff = end - start
            print("Replace backup Difference:", diff.total_seconds(), "seconds")
            print("Database updated successfully.")
            return {"success": True , "error": None}
        except Exception as e:
            print(e)
    else:
        return {"success": False , "error": "No soy esclavo o no tengo maestro"}

@app.route("/redirect")
def redirect():
    return send_from_directory('templates', "index.html")

@app.route("/ajustes")
def ajustes():
    return myRenderTemplate("ajustes.html")

@app.route("/ajustes/guardar", methods=["POST"])
def setAjustesVariable():
    return jsonify(bl.setAjustesVariable(request.get_json()))

@app.route("/ajustes/borrar", methods=["POST"])
def delAjustesVariable():
    return jsonify(bl.delAjustesVariable(request.get_json()))

@app.route("/ajustes/all", methods=["POST"])
def selAjustesVariables():
    return jsonify(bl.selAjustesVariables())

@app.route("/ajustes/sel", methods=["POST"])
def selAjustesVariable():
    print("/ajustes/sel")
    params = request.get_json()
    print(params)
    return jsonify(bl.selAjustesVariable(params["variable"], params.get("desde", None)))

@app.route("/registro/set", methods=["POST"])
def setRegistro():
    registro = request.get_json()
    print(registro)
    return jsonify(bl.setRegistro(registro))

@app.route("/registro/modificar", methods=["POST"])
def modRegistro():
    registro = request.get_json()
    print(registro)
    return jsonify(bl.modRegistro(registro))

@app.route("/registro/all", methods=["POST"])
def selRegistros():
    return jsonify(bl.selRegistros())

@app.route("/vender")
def vender():
    # mod_timestamp = os.path.getmtime(config.INVENTORY_FILE_PATH)
    # mod_datetime = datetime.datetime.fromtimestamp(mod_timestamp)

    # context = {
    #     "APP_DEVICE": config.APP_DEVICE,
    #     "MOD_INVENTARIO": str(mod_datetime)[:16],
    #     "CAMERAS_ON": config.CAMERAS_ON,
    #     "AMBIENTE": config.AMBIENTE
    # }
    #, context=context
    return myRenderTemplate("vender.html")

@app.route("/vender/guardar", methods=["POST"])
def setVenta():
    return jsonify(bl.setVenta(request.get_json()))

@app.route("/pull/ventas/esclavo", methods=["POST"])
def pull_ventas_esclavo():
    if config.soyRol(config.MAESTRO_NAME) and config.tengoRol(config.ESCLAVO_NAME):
        dispositivoId = request.get_json()
        dispositivo = config.getMSPorId(dispositivoId)
        if dispositivo is not None:
            url = rf"http://{dispositivo['direccionIP']}:5000/give/ventas/esclavo"
            print(url)
            response = requests.post(url)
            if response.status_code != 200:
                print("Error syncing:", response.text)
                return {"success": False , "error": response.text}
            print(f"Hubo respuesta: {response.json()}")
            resVentas = response.json()
            if resVentas["success"]:
                if len(resVentas["resultado"])>0:
                    res = bl.setVentasEsclavos(resVentas["resultado"], dispositivoId)
                    print(f"res guardaVentasEsclavos {res}")
                    if res["success"]:
                        print(f"resVentas[resultado]: {resVentas['resultado']}")
            return resVentas
    else:
        return {"success": False , "error": "No soy maestro o no tengo esclavo"}

@app.route("/give/ventas/esclavo", methods=["POST"])
def selVentasEsclavo():
    print("/give/ventas/esclavo")
    return jsonify(bl.selVentasEsclavo())

@app.route("/command/pull/maestro", methods=["POST"])
def command_slave_pull_maestro():
    print("Master: command slave to pull DB")
    dispositivo_id = request.get_json()
    dispositivo = config.getMSPorId(dispositivo_id)
    if not dispositivo:
        return {"success": False, "error": "Dispositivo no encontrado"}, 404
    url = f"http://{dispositivo['direccionIP']}:5000/pull/db/maestro"
    try:
        start = datetime.now()
        print("Start /command/pull/maestro:", start)
        response = requests.post(url, timeout=300)
        end = datetime.now()
        print("End /command/pull/maestro:", end)
        diff = end - start
        print("Difference /command/pull/maestro:", diff.total_seconds(), "seconds")
        if response.status_code != 200:
            return {"success": False, "error": response.text}
        return {
            "success": True,
            "resultado": response.json()
        }
    except Exception as e:
        print(e)
        return {"success": False, "error": str(e)}, 500

# @app.route("/push/db/maestro", methods=["POST"])
# def push_db_maestro():
#     print("Master: sending DB to slave")
#     dispositivoId = request.get_json()
#     dispositivo = config.getMSPorId(dispositivoId)
#     if dispositivo is not None:
#         url = f"http://{dispositivo['direccionIP']}:5000/receive/db/maestro"
#         path_to_db = config.BASE_MAESTRO_BACKUP_PATH
#         res = bl.backup_maestro()
#         if res["success"]:
#             with open(path_to_db, "rb") as f:
#                 files = {"dbfile": (config.BASE_MAESTRO_FILE, f, "application/octet-stream")}
#                 response = requests.post(url, files=files, timeout=300)
#                 if response.status_code != 200:
#                     print("Error syncing:", response.text)
#                     return {"success": False , "error": response.text}
#             print("Response:", response.text)
#             return {"success": True, "resultado": response.json()}
#         else:
#             return {"success": False, "error": "No se pudo hacer copia de datos para enviar"}
#     return {"success": False, "error": f"Dispositivo para {dispositivoId} no encontrado"}

@app.route("/receive/db/maestro", methods=["POST"])
def receive_db_maestro():
    print("Slave: update_database called")
    if "dbfile" not in request.files:
        return {"success": False, "msg": "No se envio la base del maestro"}, 400
    dbfile = request.files["dbfile"]
    temp_path = config.BASE_MAESTRO_BACKUP_PATH
    final_path = config.BASE_MAESTRO_PATH
    # Save temporary
    dbfile.save(temp_path)
    # Replace safely
    os.replace(temp_path, final_path)
    print("Slave DB updated successfully")
    return {"success": True, "msg": "Base del maestro recibida"}


@app.route("/push/pendientes/registrar", methods=["POST"])
def push_pendientes_registrar():
    print("Master: sending DB to slave")
    dispositivoId = request.get_json()
    dispositivo = config.getMSPorId(dispositivoId)
    if dispositivo is not None:
        url = f"http://{dispositivo['direccionIP']}:5000/receive/pendientes/registrar"
        response = requests.post(url, timeout=300)
        if response.status_code != 200:
            print("Error syncing:", response.text)
            return {"success": False , "error": response.text}
        return {"success": True, "slave_response": response.json()}
    return {"success": False, "error": f"Dispositivo para {dispositivoId} no encontrado"}

@app.route("/receive/pendientes/registrar", methods=["POST"])
def receive_pendientes_registrar():
    print("Slave: update_database called")
    res = bl.inventariaVentasPendientes()
    return {"success": True, "msg": "Base del maestro recibida"}

@app.route("/ventas/pendientes/sel", methods=["POST"])
def selVentasEsclavosPendientes():
    print("/ventas/pendientes/sel")
    return jsonify(bl.selVentasEsclavosPendientes())

@app.route("/ventas/pendientes/registrar", methods=["POST"])
def setVentasPendientes():
    dispositivoId = request.get_json()
    dispositivo = config.getMSPorId(dispositivoId)
    if dispositivo is not None:
        print(f"/ventas/pendientes/registrar: {dispositivoId}")
        start = datetime.now()
        print("Start:", start)
        res = bl.setVentasPendientes(dispositivoId)
        end = datetime.now()
        print("End:", end)
        diff = end - start
        print("Difference:", diff.total_seconds(), "seconds")
        return jsonify(res)
    return {"success": False, "error": f"Dispositivo para {dispositivoId} no encontrado"}

@app.route("/ventas/pendientes/borrar", methods=["POST"])
def delVentasPendientes():
    print("/ventas/pendientes/borrar")
    dispositivoId = request.get_json()
    print(f"dispositivoId {dispositivoId}")
    dispositivo = config.getMSPorId(dispositivoId)
    print(f"dispositivo {dispositivo}")
    if dispositivo is not None:
        return jsonify(bl.delVentasPendientes(dispositivoId))
    return {"success": False, "error": f"Dispositivo para {dispositivoId} no encontrado"}

@app.route("/ventas/pendientes")
def ventas_pendientes():
    print("/ventas/pendientes")
    return myRenderTemplate("pendientes.html")

@app.route("/ventas")
def ventas():
    print("/ventas")
    return myRenderTemplate("resumen.html")

@app.route("/ventas/resumen", methods=["POST"])
def selResumenVentas():
    return jsonify(bl.selResumenVentas(request.get_json()))

@app.route("/ventas/dia", methods=["POST"])
def selVentasDia():
    fecha = request.get_json()
    return jsonify(bl.selVentasDia(fecha["anio"], fecha["mes"], fecha["dia"]))

@app.route("/ventas/semana", methods=["POST"])
def selSemanaVentas():
    fecha = request.get_json()
    print(fecha)
    return jsonify(bl.selSemanaVentas(fecha["anio"], fecha["mes"], fecha["dia"]))

@app.route("/ventas/activar", methods=["POST"])
def setActivoVenProds():
    productos = request.get_json()
    print(productos)
    return jsonify(bl.setActivoVenProds(productos))

@app.route("/ventas/cambiarFecha", methods=["POST"])
def setFechaVentaVenProds():
    params = request.get_json()
    print(params)
    productos = params["ventas"]
    nuevaFecha = params["nuevaFecha"]
    return jsonify(bl.setFechaVentaVenProds(productos, nuevaFecha))

@app.route("/producto")
def producto():
    return myRenderTemplate("producto.html")


@app.route("/producto/exists", methods=["POST"])
def producto_exists():
    params = request.get_json()
    producto_id = params.get("productoId")  # may be null
    valor = params.get("valor")  # may be null
    campo = params.get("campo")  # may be null
    return bl.producto_exists(campo, valor, producto_id)


@app.route("/producto/set", methods=["POST"])
def setProducto():
    producto = request.get_json()
    return jsonify(bl.setProducto(producto))

@app.route("/producto/find", methods=["POST"])
def findProducto():
    params = request.get_json()
    return jsonify(bl.findProducto(params["searchString"], params["buscaActivo"]))

@app.route("/producto/find/barras", methods=["POST"])
def findProductoBarras():
    params = request.get_json()
    return jsonify(bl.findProductoBarras(params["codigoBarras"], params["buscaActivo"]))

# @app.route("/buscar_producto", methods=["POST"])
# def findProductoBarras():
#     barcode = request.json.get("barcode")
#     product = bl.findProductoBarras(barcode)
#     if product:
#         return jsonify({"estado": "exito", "producto": product})
#     return jsonify({"estado": "error", "mensaje": f"Producto no encontrado para {barcode} ({product})"})


@app.route("/producto/find/id", methods=["POST"])
def findProductoId():
    params = request.get_json()
    return jsonify(bl.findProductoId(params["productoId"], params["buscaActivo"]))

@app.route("/producto/find/clave", methods=["POST"])
def findProductoClaves():
    params = request.get_json()
    return jsonify(bl.findProductoClaves(params["codigo"], params["buscaActivo"]))

@app.route("/producto/find/numerico", methods=["POST"])
def findProductoNumerico():
    params = request.get_json()
    return jsonify(bl.findProductoNumerico(params["codigo"], params["buscaActivo"]))

@app.route("/producto/id", methods=["POST"])
def selProductoId():
    productoId = request.get_json()
    return jsonify(bl.selProductoId(productoId))

@app.route("/proveedor/getAll", methods=["POST"])
def selProveedores():
    return(jsonify(bl.selProveedores()))

@app.route("/inventario")
def inventario():
    return myRenderTemplate("inventario.html")

@app.route("/inventario/escaso", methods=["POST"])
def findProductoEscaso():
    return(jsonify(bl.findProductoEscaso()))

@app.route("/truper")
def truper():
    return myRenderTemplate("truper.html")

@app.route("/debug_log", methods=["POST"])
def debug_log():
    data = request.get_json()
    with open(config.DEBUG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(data.get("message", "") + "\n")
    return jsonify({"ok": True})

# @app.route('/ventas/ventas_viewer.html')
# def ventas_viewer():
#     return send_from_directory('templates', 'ventas_viewer.html')

# -----------------------------------------------------------
# Helper: Check if a process exists
# -----------------------------------------------------------

def pid_exists(pid: int) -> bool:
    """Return True if a process with the given PID exists."""
    try:
        os.kill(pid, 0)   # does not actually kill; just tests signal delivery
    except OSError as e:
        if e.errno == errno.ESRCH:  # no such process
            return False
        elif e.errno == errno.EPERM:  # process exists but no permission
            return True
        else:
            raise
    else:
        return True


# -----------------------------------------------------------
# Helper: Get processes running on APP_PORT
# -----------------------------------------------------------

def getProcessesOnPort(port):
    pids=[]
    if sys.platform.startswith('win'):
        cmd = f'netstat -ano | findstr :{port}'
        output = subprocess.check_output(cmd, shell=True).decode()
        for line in output.strip().split('\n'):
            if 'LISTENING' in line:
                pid = int(line.strip().split()[-1])
                pids.append(pid)
    else:
        cmd = f"lsof -t -i:{port}"
        try:
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            if output:
                pids = output.split("\n")
        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            print(f"{cmd}: {e}")
    return pids


# -----------------------------------------------------------
# Helper: Kill processes on port 5000 if already running
# -----------------------------------------------------------

def kill_port(port):
    print("sys.platform: "+sys.platform)

    current_pid = str(os.getpid())
    parent_pid = str(os.getppid())
    print(f"Current PID: {current_pid}, Parent PID: {parent_pid}")

    pids = getProcessesOnPort(port)
    print(f"Processes running on port {port}: {pids}")

    for pid in pids:
        if pid not in [current_pid, parent_pid]:
            print(pid)
            print(type(pid))
            pid = int(pid)
            time.sleep(2)
            try:
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    print(f"SIGTERM ProcessLookupError")
                except Exception as e:
                    print(f"Could not SIGTERM kill port {port}: {e}")
                time.sleep(1)
                if pid_exists(pid):
                    os.kill(pid, signal.SIGKILL)
                    print(f"SIGKILL Killed process {pid} using port {port}")
                else:
                    print(f"SIGTERM Killed process {pid} using port {port}")
            except Exception as e:
                print(f"Could not SIGKILL kill port {port}: {e}")
            time.sleep(2)

# -----------------------------------------------------------
# Run app
# -----------------------------------------------------------
if __name__ == "__main__":
    print(f"APP_DEVICE: {config.APP_DEVICE}")
    # if APP_DEVICE == "Mac":
    #     kill_port(APP_PORT)
    print(f"Ventas se guardarán en: {config.VENTAS_FOLDER_PATH}")
    print(f"Logs in: {config.LOG_FILE_PATH}")
    print(f"Debug in: {config.DEBUG_FILE_PATH}")
    bl.setMSConfig()
    print(f"DEVICE config: {config.DEVICE}")
    bl.setThisIP()
    print(f"DEVICE IP: {config.THIS_IP}")
    config.delete_files_older_than(config.PROCESS_LOG_PATH, days=15)
    config.delete_files_older_than(config.PROCESS_TMP_PATH, days=15)
    ensure_init_py(config.PROCESOS_PATH)
    ensure_init_py(config.PROCESS_JOBS_PATH)
    print("TERMINADO")
    time.sleep(2)
    app.run(host="0.0.0.0", port=config.APP_PORT, debug=True, use_reloader=False, threaded=True)
