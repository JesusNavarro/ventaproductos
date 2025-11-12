# CONFIG FILE FOR APP VARIABLES 
import os

# -----------------------------------------------------------
# Device mode
# -----------------------------------------------------------

""" ***** Cambiar este valor si la app se va a ejecutar en la tableta o en la Mac ***** """

APP_DEVICE = "Tablet"	# "Tablet" for Samsung, "Mac" for computer
AMBIENTE= "Prod"  # Dev for development uses port 5000, and 5001 for "Prod"
APP_PORT = 5000 if AMBIENTE=="Dev" else 5000

# -----------------------------------------------------------
# Folders y archivos
# -----------------------------------------------------------

APP_FOLDER = "/storage/emulated/0/SyncFolder/ventaproductos" if APP_DEVICE== "Tablet" else "./"
INVENTORY_FOLDER = "inventario"
INVENTORY_FILE = "inventario.txt"
VENTAS_FOLDER = "ventas"
LOG_FOLDER = "logs"
LOG_FILE = "log.txt"
DEBUG_FILE = "debug_log.txt"

VENTAS_FOLDER_PATH = os.path.join(APP_FOLDER, VENTAS_FOLDER)
INVENTORY_FOLDER_PATH = os.path.join(APP_FOLDER, INVENTORY_FOLDER)
LOG_FOLDER_PATH = os.path.join(APP_FOLDER, LOG_FOLDER)

INVENTORY_FILE_PATH = os.path.join(APP_FOLDER, INVENTORY_FOLDER, INVENTORY_FILE)
LOG_FILE_PATH = os.path.join(APP_FOLDER, LOG_FOLDER, LOG_FILE)
DEBUG_FILE_PATH = os.path.join(APP_FOLDER, LOG_FOLDER, DEBUG_FILE)


# -----------------------------------------------------------
# Configuraciones camara. Si estan activadas, segun sea la tablet o la mac, 
# va a cargar las librerias para usar la camara. Si estan desactivsadas,
# no se caragaran ni las librerias ni la logica que usan.  
# 
# -----------------------------------------------------------

CAMERAS_ON = True if APP_DEVICE=="Mac" else False
