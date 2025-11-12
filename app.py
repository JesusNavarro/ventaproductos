import subprocess
import sys
import os
import csv
import signal
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import time
import errno
from config import *

app = Flask(__name__)

# VARIABLES FOR FILE LOCATIONS AND APP LOCATION are in config.py and automatically loaded

# Ensure folders exist
os.makedirs(INVENTORY_FOLDER_PATH, exist_ok=True)
os.makedirs(VENTAS_FOLDER_PATH, exist_ok=True)
os.makedirs(LOG_FOLDER_PATH, exist_ok=True)

with open(LOG_FILE_PATH, "w") as f:
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

sys.stdout = TimestampedWriter(open(LOG_FILE_PATH, "a"))
sys.stderr = TimestampedWriter(open(LOG_FILE_PATH, "a"))

# -----------------------------------------------------------
# Load inventory (TSV format)
# -----------------------------------------------------------

# ********** ORIGINAL FILE READING
#with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
#    reader = csv.DictReader(f, delimiter="\t")
#    inventory_list = [row for row in reader]

#with open(INVENTORY_PATH, "r", encoding="utf-8-sig", newline="") as f:
#    # reader = csv.reader(f)
#    reader = csv.DictReader(f, delimiter="\t")
#    inventory_list = [[cell.strip().replace('\r', '') for cell in row] for row in reader]

#with open(INVENTORY_FILE_PATH, "r", encoding="utf-8-sig", newline="") as f:
#    reader = csv.DictReader(f, delimiter="\t")
#    inventory_list = [
#        {k: v.strip().replace('\r', '') for k, v in row.items()} 
#        for row in reader
#    ]


def open_with_fallback(file_path):
    encodings = ["utf-8-sig", "utf-8", "cp1252"]  # try in order
    for enc in encodings:
        try:
            f = open(file_path, "r", encoding=enc, newline="")
            # try reading a small sample to confirm it works
            f.read(1024)
            f.seek(0)
            print(f"Using encoding: {enc}")
            return f
        except UnicodeDecodeError:
            continue
    # last resort: open with errors replaced
    f = open(file_path, "r", encoding="utf-8", errors="replace", newline="")
    print("Using utf-8 with replacement for unknown characters")
    return f



# # Detect the file encoding
# result = from_path(INVENTORY_FILE_PATH)
# encoding = result.best().encoding  # best guess of encoding
# print(f"Detected encoding: {encoding}")

# # Read the TSV file using the detected encoding
# with open(INVENTORY_FILE_PATH, "r", encoding=encoding, newline="") as f:
#     reader = csv.DictReader(f, delimiter="\t")
#     inventory_list = [
#         {k: v.strip().replace('\r', '') for k, v in row.items()} 
#         for row in reader
#     ]


def formateaFechaEspanol(fecha):
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    dias_semana = [
        "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"
    ]
    dia_semana = dias_semana[fecha.weekday()]  # weekday() -> 0 = Monday
    dia = fecha.day
    mes = meses[fecha.month - 1]
    anio = fecha.year
    hora = fecha.strftime("%I:%M %p").lower()  # 12-hour format with am/pm

    formatted = f"{dia_semana} {dia} de {mes} de {anio} - {hora}"
    return formatted

# with open_with_fallback(INVENTORY_FILE_PATH) as f:
#     reader = csv.DictReader(f, delimiter="\t")
#     inventory_list = [
#         {k: v.strip().replace('\r', '') for k, v in row.items()} 
#         for row in reader
#     ]


with open_with_fallback(INVENTORY_FILE_PATH) as f:
    sample = f.readline()
    f.seek(0)
    delimiter = "," if "," in sample else "\t"  # Auto-detect tab or comma

    reader = csv.reader(f, delimiter=delimiter)
    first_row = next(reader)
    num_cols = len(first_row)
    f.seek(0)  # Reset to start again

    expected_cols = [
        "CodigoBarras", "Descripcion", "Costo", "Precio",
        "Mayoreo", "Inventario", "Minimo", "Departamento"
    ]

    if num_cols == 8:
        print("✅ Detected 8 columns — assigning custom headers")
        f.seek(0)
        reader = csv.DictReader(f, fieldnames=expected_cols, delimiter=delimiter)
    else:
        print(f"⚠️ Detected {num_cols} columns — using file headers")
        f.seek(0)
        reader = csv.DictReader(f, delimiter=delimiter)

    inventory_list = [
        {k: v.strip().replace("\r", "") for k, v in row.items()}
        for row in reader
    ]

    print(f"📦 Loaded {len(inventory_list)} productos")

# Helper: lookup product by barcode
def buscar_producto_por_codigo(barcode):
    print(f"buscar_producto_por_codigo: '{barcode}'")
    for item in inventory_list:
        if str(item.get("CodigoBarras", "")).strip() == str(barcode).strip():
            print(item)
            return item
    return None

# -----------------------------------------------------------
# Helper: Today's ventas file path
# -----------------------------------------------------------
def get_today_sales_file():
    dias_es = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    dia = dias_es[now.weekday()]
    return os.path.join(VENTAS_FOLDER_PATH, f"{today}_{dia}.tsv")

# -----------------------------------------------------------
# Routes
# -----------------------------------------------------------
@app.route("/")
def index():
    mod_timestamp = os.path.getmtime(INVENTORY_FILE_PATH)
    mod_datetime = datetime.fromtimestamp(mod_timestamp)
    mod_inventario = formateaFechaEspanol(mod_datetime)
    print(f"{INVENTORY_FILE_PATH} was last modified at: {mod_inventario}")
    context = {
        "APP_DEVICE": APP_DEVICE,
        "PRODUCTOS_INVENTARIO": len(inventory_list),
        "MOD_INVENTARIO": mod_inventario,
        "CAMERAS_ON": CAMERAS_ON,
        "AMBIENTE": AMBIENTE
    }
    print(f"context: {context}")
    return render_template("index.html", context=context)

@app.route("/buscar_producto", methods=["POST"])
def buscar_producto():
    barcode = request.json.get("barcode")
    print("Inside Flask, buscar_producto: "+barcode)
    product = buscar_producto_por_codigo(barcode)
    if product:
        print("Inside Flask, producto: "+str(product))
        return jsonify({"estado": "exito", "producto": product})
    print(f"Producto no encontrado para {barcode} ({product})")
    return jsonify({"estado": "error", "mensaje": f"Producto no encontrado para {barcode} ({product})"})

@app.route("/guardar_venta", methods=["POST"])
def guardar_venta():
    venta_data = request.json.get("venta")
    print(venta_data)
    # Add date/time columns
    now = datetime.now()
    fecha = now.strftime("%Y-%m-%d")
    hora = now.strftime("%H:%M:%S")

    for p in venta_data:
        p["Fecha"] = fecha
        p["Hora"] = hora

    today_file = get_today_sales_file()
    print(today_file)
    file_exists = os.path.exists(today_file)

    # Write to TSV file
    with open(today_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=venta_data[0].keys(), delimiter="\t")
        if not file_exists:
            writer.writeheader()
        writer.writerows(venta_data)

    return jsonify({"estado": "exito"})

@app.route("/debug_log", methods=["POST"])
def debug_log():
    data = request.get_json()
    with open(DEBUG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(data.get("message", "") + "\n")
    return jsonify({"ok": True})

@app.route('/ventas/<path:filename>')
def ventas_file(filename):
    return send_from_directory('ventas', filename)


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
            print(f"⚠️ {cmd}: {e}")
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
                    print(f"⚠️ SIGTERM ProcessLookupError")
                except Exception as e:
                    print(f"⚠️ Could not SIGTERM kill port {port}: {e}")
                time.sleep(1)
                if pid_exists(pid):
                    os.kill(pid, signal.SIGKILL)
                    print(f"🔪 SIGKILL Killed process {pid} using port {port}")
                else:
                    print(f"🔪 SIGTERM Killed process {pid} using port {port}")
            except Exception as e:
                print(f"⚠️ Could not SIGKILL kill port {port}: {e}")
            time.sleep(2)

# -----------------------------------------------------------
# Run app
# -----------------------------------------------------------
if __name__ == "__main__":
    print(f"🚀 APP_DEVICE: {APP_DEVICE}")
    # if APP_DEVICE == "Mac":
    #     kill_port(APP_PORT)
    print(f"📦 Inventario cargado desde: {INVENTORY_FILE_PATH}")
    print(f"💾 Ventas se guardarán en: {VENTAS_FOLDER_PATH}")
    print(f"💾 Logs in: {LOG_FILE_PATH}")
    print(f"💾 Debug in: {DEBUG_FILE_PATH}")
    time.sleep(2)
    app.run(host="0.0.0.0", port=APP_PORT, debug=True, use_reloader=False)
