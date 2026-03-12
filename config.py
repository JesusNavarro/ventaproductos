# CONFIG FILE FOR APP VARIABLES 
import os
import time

# -----------------------------------------------------------
# Device mode
# -----------------------------------------------------------

""" ***** Cambiar este valor si la app se va a ejecutar en la tableta o en la Mac ***** """

APP_DEVICE = "Mac"	# "Tablet" for Samsung, "Mac" for computer, "PC" para computadora windows
AMBIENTE= "Dev"  # Dev for development uses port 5000, and 5001 for "Prod"
APP_PORT = 5000 if AMBIENTE=="Dev" else 5000

OLD_SQL_LITE =False

# -----------------------------------------------------------
# Folders y archivos
# -----------------------------------------------------------

APP_FOLDER = "/storage/emulated/0/SyncFolder/ventaproductos" if APP_DEVICE== "Tablet" else "./"
INVENTORY_FOLDER = "inventario"
INVENTORY_FILE = "inventario.txt"
VENTAS_FOLDER = "ventas"
LOG_FOLDER = "logs"
LOG_FILE = "log_"+APP_DEVICE+".txt"
DEBUG_FILE = "debug_log_"+APP_DEVICE+".txt"
DB_FOLDER = "db"
MODELS_FOLDER = "models"
SQL_FOLDER = "sql"

DB_PATH = os.path.join(APP_FOLDER, DB_FOLDER)
os.makedirs(DB_PATH, exist_ok=True)
MODELS_PATH = os.path.join(DB_PATH, MODELS_FOLDER)
os.makedirs(MODELS_PATH, exist_ok=True)
SQL_PATH = os.path.join(DB_PATH, SQL_FOLDER)
os.makedirs(SQL_PATH, exist_ok=True)

MAESTRO_NAME = "maestro"
ESCLAVO_NAME = "esclavo"

BASE_MAESTRO_NAME = "base_maestro"
BASE_ESCALVO_NAME = "base_esclavo"
BASE_DEVICE_NAME = "device"
BASE_MAESTRO_BACKUP_NAME = BASE_MAESTRO_NAME+"_backup"
BASE_MAESTRO_BACKUP_SLAVE_NAME = BASE_MAESTRO_NAME+"_backup_slave"

BASE_MAESTRO_FILE = f"{BASE_MAESTRO_NAME}.db"
BASE_ESCLAVO_FILE = f"{BASE_ESCALVO_NAME}.db"
BASE_DEVICE_FILE = f"{BASE_DEVICE_NAME}.db"
BASE_MAESTRO_BACKUP_FILE = f"{BASE_MAESTRO_BACKUP_NAME}.db"
BASE_MAESTRO_BACKUP_SLAVE_FILE = f"{BASE_MAESTRO_BACKUP_SLAVE_NAME}.db"

BASE_MAESTRO_PATH = os.path.join(MODELS_PATH, BASE_MAESTRO_FILE)
BASE_ESCLAVO_PATH = os.path.join(MODELS_PATH, BASE_ESCLAVO_FILE)
BASE_DEVICE_PATH = os.path.join(MODELS_PATH, BASE_DEVICE_FILE)
BASE_MAESTRO_BACKUP_PATH = os.path.join(MODELS_PATH, BASE_MAESTRO_BACKUP_FILE)
BASE_MAESTRO_BACKUP_SLAVE_PATH = os.path.join(MODELS_PATH, BASE_MAESTRO_BACKUP_SLAVE_FILE)


VENTAS_FOLDER_PATH = os.path.join(APP_FOLDER, VENTAS_FOLDER)
os.makedirs(VENTAS_FOLDER_PATH, exist_ok=True)
INVENTORY_FOLDER_PATH = os.path.join(APP_FOLDER, INVENTORY_FOLDER)
os.makedirs(INVENTORY_FOLDER_PATH, exist_ok=True)
LOG_FOLDER_PATH = os.path.join(APP_FOLDER, LOG_FOLDER)
os.makedirs(LOG_FOLDER_PATH, exist_ok=True)

INVENTORY_FILE_PATH = os.path.join(INVENTORY_FOLDER_PATH, INVENTORY_FILE)
LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, LOG_FILE)
DEBUG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, DEBUG_FILE)

PROCESOS_FOLDER = "procesos"
PROCESS_JOBS_FOLDER = "jobs"
PROCESS_TMP_FOLDER = "tmp"
PROCESS_LOG_FOLDER = "logs"

PROCESOS_PATH =  os.path.join(APP_FOLDER, PROCESOS_FOLDER)
PROCESS_JOBS_PATH = os.path.join(PROCESOS_PATH, PROCESS_JOBS_FOLDER)
PROCESS_TMP_PATH = os.path.join(PROCESOS_PATH, PROCESS_TMP_FOLDER)
PROCESS_LOG_PATH = os.path.join(PROCESOS_PATH, PROCESS_LOG_FOLDER)
PROCESS_LOG_DELETE = True

os.makedirs(PROCESOS_PATH, exist_ok=True)
os.makedirs(PROCESS_JOBS_PATH, exist_ok=True)
os.makedirs(PROCESS_TMP_PATH, exist_ok=True)
os.makedirs(PROCESS_LOG_PATH, exist_ok=True)

TRUPER_IMAGENES_PATH = os.path.join(APP_FOLDER, "static", "imagenes", "truper")

# -----------------------------------------------------------
# Configuraciones camara. Si estan activadas, segun sea la tablet o la mac, 
# va a cargar las librerias para usar la camara. Si estan desactivsadas,
# no se caragaran ni las librerias ni la logica que usan.  
# 
# -----------------------------------------------------------

CAMERAS_ON = True if APP_DEVICE=="Mac" else False

# DEVICE MASTER / SLAVE CONFIG, TO BE LOADED WHEN APP STARTS

DEVICE = {
    "MS_SOY" : None,
    "MS_MAESTROS" : None,
    "MS_ESCLAVOS" :  None
}

THIS_IP = None

def getMSConfig():
    ms = []
    if DEVICE["MS_SOY"]!=None:
        ms.append(DEVICE["MS_SOY"])
    if DEVICE["MS_MAESTROS"]!=None:
        ms.extend(DEVICE["MS_MAESTROS"])
    if DEVICE["MS_ESCLAVOS"]!=None:
        ms.extend(DEVICE["MS_ESCLAVOS"])
    print(f"getMSConfig {ms}")
    return ms

def getMSPorId(dispositivoId):
    objList = [obj for obj in getMSConfig() if obj["dispositivoId"] == dispositivoId]
    if objList is not None and len(objList)==1:
        return objList[0]

def setMSConfig(registros):
    DEVICE["MS_SOY"] = None
    DEVICE["MS_MAESTROS"] = None
    DEVICE["MS_ESCLAVOS"] = None
    if registros!=None and len(registros)>0:
        maestros = []
        esclavos = []
        for r in registros:
            if r["soy"]:
                DEVICE["MS_SOY"] = r
            elif r["rol"]==MAESTRO_NAME:
                maestros.append(r)
            elif r["rol"]==ESCLAVO_NAME:
                esclavos.append(r)
        DEVICE["MS_MAESTROS"] = maestros
        DEVICE["MS_ESCLAVOS"] = esclavos
    print(DEVICE["MS_SOY"], DEVICE["MS_MAESTROS"], DEVICE["MS_ESCLAVOS"])

def soyRol(rol):
    if DEVICE["MS_SOY"]!=None:
        if DEVICE["MS_SOY"]["rol"]==rol:
            return True
    return False

def myRol():
    if DEVICE["MS_SOY"]!=None:
        return DEVICE["MS_SOY"]["rol"]
    
def tengoRol(rol):
    if rol==MAESTRO_NAME:
        return DEVICE["MS_MAESTROS"]!=None and len(DEVICE["MS_MAESTROS"])>0
    elif rol==ESCLAVO_NAME:
        return DEVICE["MS_ESCLAVOS"]!=None and len(DEVICE["MS_ESCLAVOS"])>0
    
def delete_files_older_than(folder, days):
    cutoff = time.time() - days * 86400
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)
        except FileNotFoundError:
            pass