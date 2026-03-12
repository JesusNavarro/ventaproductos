import db.ajustesDAO as ajust
import db.productosDAO as pro
import db.dispositivosDAO as disp
import db.baseDatosDAO as db
import db.ventasDAO as ven
import db.catalogoTruperDAO as trup
import config
import socket
from procesos.jobManager import JobManager
import base64
from procesos.jobs.pandasReader import SimpleDF
import copy

jm = JobManager()

# PROCESOS

# def startJob(script, params):
# 	jobId = jm.start(script,params)
# 	return jobId

def decode_bytes(raw):
    for enc in ("ISO-8859-1", "utf-16", "utf-8"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            pass

    # latin-1 never fails, so last
    return raw.decode("latin-1"), "latin-1"

def startJob(script, params):
    wrapper = JOB_WRAPPERS.get(script, {})
    if "before" in wrapper:
        params = wrapper["before"](params)
    return jm.start(script, params)

def jobStatus(jobId):
    job = jm.status(jobId)
    return job

# def jobResult(jobId):
#     return jm.result(jobId)

def jobResult(jobId):
	job = jm.result(jobId)
	result = job["result"]
	wrapper = JOB_WRAPPERS.get(job["script"], {})
	if "after" in wrapper:
		result = wrapper["after"](job, result)
		job["result"] = result
	return job

# JOB PREPARATION LOGIC ********************

def formatInventario(params):
	b64 = params["archivos_texto"]["inventarioNuevo"]
	raw = base64.b64decode(b64)   # ← BYTES again
	archivoInventario, encoding = decode_bytes(raw)
	print(f"Se decodifico inventario usando {encoding}")
	params["archivos_texto"]["inventarioNuevo"] = archivoInventario
	return truperObtenCatExistente(params)
	#raise f"No se obtuvo selCatalogoTruper"


def truperObtenCatExistente(params):
	res = trup.selCatalogoTruper()
	if res["success"] and len(res["resultado"])>0:
		params.get("archivos_texto", {})["truperExistente"]= res["resultado"]
	res = trup.selTruperKgUnidades()
	if res["success"] and len(res["resultado"])>0:
		params.get("archivos_texto", {})["truperKgUnidades"]= res["resultado"]
	return params
	#raise f"No se obtuvo selCatalogoTruper"

def truperGuardaCatNuevo(job, result):
	if job["exitCode"]==0:
		res = trup.setCatalogoTruper(result)
		if res["success"]:
			return result
	return None
	#raise f"No se obtuvo selCatalogoTruper"

def invGuardaInventario(job, result):
	if job["exitCode"]==0:
		#print(result)
		res = trup.setInventarioWIP(result)
		if res["success"]:
		 	#return result
			pass
	return result
	#raise f"No se obtuvo selCatalogoTruper"

# ******************** JOB WRAPPERS

JOB_WRAPPERS = {
    "procesaTruper": {
        "before": truperObtenCatExistente,
        "after": truperGuardaCatNuevo,
    },
	"procesaInventario": {
		"before": formatInventario,
        "after": invGuardaInventario,
	}
}

# CONFIGURACION DISPOSITIVO *********************************

# DIRECCION IP
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Does not have to be reachable
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"
    finally:
        s.close()

def setThisIP():
	config.THIS_IP = get_local_ip()

# INSERTA EN TABLA REGISTROS
def _ins_registro(registro):
	res = disp.insRegistro(registro)
	if res["success"]:
		return res
	else:
		raise Exception(res["error"])

# MODIFICA EN TABLA REGISTROS
def modRegistro(registro):	# CHECKED
	res = disp.modRegistro(registro)
	if res["success"]:
		setMSConfig()
		return res
	else:
		raise Exception(res["error"])

# ACTUALIZA CONFIG DE REGISTROS SEGUN EXISTENTES
def setMSConfig():
	res = selRegistros()
	if res["success"]:
		config.setMSConfig(res["resultado"])
		return res
	else:
		raise Exception(res["error"])

# CREA TABLA REGISTROS, ISNERTA Y GUARDA CONFIG
def setRegistro(registro):	# CHECKED
	db.create_registro()
	if registro["soy"]:
		registro["direccionIP"]=get_local_ip()
	res = _ins_registro(registro)
	if res["success"]:
		setMSConfig()
	if config.soyRol(config.MAESTRO_NAME):
		db.create_maestro()
	elif config.soyRol(config.ESCLAVO_NAME):
		db.create_esclavo()
	if res["success"]:
		return res
	else:
		raise Exception(res["error"])

# SEL REGISTROS EXISTENTES
def selRegistros():		# CHECKED
	res = disp.selRegistros()
	if res["success"]:
		return res
	else:
		raise Exception(res["error"])
	
# GUARDA VARIABLE EN TABLA AJUSTES
def setAjustesVariable(registro_variable):	# CHECKED
	res = ajust.setAjustesVariable(registro_variable)
	if res["success"]:
		return res
	raise f"No se pudo guardar {registro_variable}"

# BORRA VARIABLE DE TABLA AJUSTES
def delAjustesVariable(registro_variable):	# CHECKED
	res = ajust.delAjustesVariable(registro_variable)
	if res["success"]:
		return res
	raise f"No se pudo guardar {registro_variable}"

# SEL VARIABLES EN AJUSTES
def selAjustesVariables():	# CHECKED
	res = ajust.selAjustesVariables()
	if res["success"]:
		return res
	raise f"No se pudo obtener ajustes"

# SEL UNA VARIABLE DE AJUSTES
def selAjustesVariable(nombre, desde=None):	# CHECKED
	res = ajust.selAjustesVariable(nombre, desde)
	if res["success"]:
		return res
	raise f"No se pudo obtener ajustes"

def selIva():
	res = selAjustesVariable("IVA")
	if (res["success"] and len(res["resultado"])==1):
		return float(res["resultado"][0]["valor"])
	return None

# PROVEEDORES *********************************

# SEL PROVEEDORES
def selProveedores():	# CHECKED
	res = ajust.selProveedores()
	if res["success"]:
		return res
	else:
		raise Exception(res["error"])

# INVENTARIO *********************************

# ENCUENTRA RODUCTO POR CADENA DE BUSQUEDA
def findProducto(searchString, buscaActivo):		# CHECKED
	res = pro.findProducto(searchString, buscaActivo)
	if res["success"]:
		return res
	else:
		raise Exception(res["error"])

# ENCUENTRA PRODUCTO POR CODIGO DE BARRAS
def findProductoBarras(codigoBarras, buscaActivo):	# CHECKED
	res = pro.findProductoBarras(codigoBarras, buscaActivo)
	if res["success"]:
		return res
	else:
		raise Exception(res["error"])
	
# ENCUENTRA PRODUCTO POR ID CON ATRIBUTOS
def findProductoId(productoId, buscaActivo):		# CHECKED
	res = pro.findProductoId(productoId, buscaActivo)
	if res["success"]:
		return res
	else:
		raise Exception(res["error"])

# ENCUENTRA PRODUCTO POR ID SIN ATRIBUTOS
def selProductoId(productoId):	# CHECKED
	res = pro.selProductoId(productoId)
	if res["success"]:
		return res
	else:
		raise Exception(res["error"])

# ENCUENTRA PRODUCTO POR CLAVES
def findProductoClaves(codigo, buscaActivo):	# CHECKED
	res = pro.findProductoClaves(codigo, buscaActivo)
	if res["success"]:
		return res
	else:
		raise Exception(res["error"])

# ENCUENTRA PRODUCTO POR CODIGO
def findProductoNumerico(codigo, buscaActivo):	# CHECKED
	res = pro.findProductoNumerico(codigo, buscaActivo)
	if res["success"]:
		return res
	else:
		raise Exception(res["error"])

# GUARDA UN PRODUCTO
def setProducto(producto):		# CHECKED
	if producto.get("productoId"):
		res = pro.modProducto(producto)
	else:
		res = pro.insProducto(producto)
	if res["success"]:
		return res
	else:
		raise Exception(res["error"])

# VENTAS *********************************

# GUARDA PRODUCTOS DE VENTA NUEVA, ACTUALIZA INVENTARIO
def setVenta(venta):		# CHECKED
	print(f"setVenta {venta}")
	if any(row.get("fechaVenta") is not None for row in venta):
		raise Exception(f"Venta nueva tiene productos ya con fecha de venta {venta}")
	else:
		res = ven.setVenta(venta)
		if res["success"]:
			return res
		else:
			raise Exception(res["error"])
		
# GUARDA PRODUCTOS CON FECHA VENTA EXISTENTE Y SIN FECHA INVENTARIO, ACTUALIZA INVENTARIO
def _set_venta_productos(prods):
	if any(row.get("fechaVenta") is None for row in prods):
		raise Exception(f"Se quiere registrar productos sin fecha de venta {prods}")
	if any(row.get("fechaInventario") is not None for row in prods):
		raise Exception(f"Productos ya tienen fecha de inventario {prods}")
	for prod in prods:
		res = _set_venta_producto(prod)
		if not res["success"]:
			raise Exception(res["error"])
	return db.returnBlank()

# GUARDA UN PRODUCTO EXISTENTE EN VENTAS, ACTUALIZA INVENTARIO
def _set_venta_producto(prod):
	res = ven.setProducto(prod)
	if not res["success"]:
		raise f"No se pudo insertar venta para {prod}"
	return res
	
# ACTIVA O DESACTIVA PRODUCTOS EN VENTAS Y MODIFICA INVENTARIO
def setActivoVenProds(prods):	# CHECKED
	res = ven.setActivoVenProds(prods)
	if not res["success"]:
		raise Exception(f"No se pudo activar venta {prods}")
	return res

# VENTAS MAESTRO *********************************

# BORRA VENTAS PENDIENTES DE LOS ESCLAVOS EN EL MAESTRO VENTAS_ESCLAVOS
def delVentasPendientes(dispositivoId): 	#CHECKED
	res = ven.delVentasPendientes(dispositivoId)
	if res["success"]:
		return res
	raise f"No se pudo borrar ventas pendientes para {dispositivoId}"

# GUARDA VENTAS RECIBIDAS DE ESCLAVOS EN VENTAS_ESCLAVOS
def setVentasEsclavos(ventas, dispositivoId):		# CHECKED
	print(f"setVentasEsclavos {ventas}")
	if config.soyRol(config.MAESTRO_NAME) and config.tengoRol(config.ESCLAVO_NAME):
		print("inside setVentasEsclavos")
		if len(ventas)>0:
			print("len(ventas)>0")
			res = ven.setVentasEsclavos(ventas, dispositivoId)
			if res["success"]:
				return res
			else:
				raise Exception(res["error"])
		else:
			print("NO HAY VENTAS PENDIENTES EN EL ESCLAVO ***** ")
			return db.returnBlank()
	else:
		print("NOT MAESTRO NOR ESCLAVO")
		return db.returnError("No soy maestro o no tengo esclavos")

# REGISTRA VENTAS PENDIENTES EN VENTAS Y SU INVENTARIO EN PRODUCTOS EN EL MAESTRO
def setVentasPendientes(dispositivoId):		# CHECKED
	if config.soyRol(config.MAESTRO_NAME):
		res = selVentasEsclavosPendientes(dispositivoId, sinInventario=True)
		if res["success"]:
			ventas = res["resultado"]
			res = _set_venta_productos(ventas)
			if res["success"]:
				return res
		return db.returnError("No hay ventar para registrar")
	else:
		return db.returnError("No soy maestro")

# OBTIENE VENTAS PENDIENTES DE VENTAS_ESCLAVOS EN MAESTRO
def selVentasEsclavosPendientes(dispositivoId=None, sinInventario=False):	# CHECKED
	if config.soyRol(config.MAESTRO_NAME):
		res = ven.selVentasEsclavosPendientes(dispositivoId, sinInventario)
		if res["success"]:
			return res
		else:
			raise Exception(res["error"])
	else:
		return db.returnError("No soy maestro")
	
# VENTAS ESCLAVO *********************************

# OBTIENE VENTAS PENDIENTES DE INVENTARIO DE UN ESCLAVO
def selVentasEsclavo():		# CHECKED
	if config.soyRol(config.ESCLAVO_NAME) and config.tengoRol(config.MAESTRO_NAME):
		res = ven.selVentasSinInventario()
		if res["success"]:
			return res
		else:
			raise Exception(res["error"])
	else:
		return db.returnError("No es esclavo o no tiene maestro")

# INVENTARIA VENTAS PENDIENTES EN ESCLAVO
def inventariaVentasPendientes():	# CHECKED
	if config.soyRol(config.ESCLAVO_NAME) and config.tengoRol(config.MAESTRO_NAME):
		res = ven.selVentasSinInventario()
		if res["success"]:
			ventas_pendientes = res["resultado"]
			if len(ventas_pendientes)>0:
				res = ven.selVentasInventariadas(ventas_pendientes)
				if res["success"]:
					ventas_inventariadas = res["resultado"]
					res = ven.modFechaInvVentas(ventas_inventariadas)
					if not res["success"]:
						raise res["error"]
					else:
						res["resultado"]=ventas_inventariadas
						print("A ejecutar borra ventas")
						ven.del_ventas_viejas_slave()
			return res
	raise "No soy esclavo, no tengo maestro o no se pudo inventariar ventas"

# REPORTE VENTAS *********************************

# OBTIENE RESUMEN DE VENTAS ANUAL
def selResumenVentas(anio):		# CHECKED
	res = ven.selResumenVentas(anio)
	if res["success"]:
		resultado = {}
		for r in res["resultado"]:
			print(r)
			resultado.setdefault(r["mes"], {})
			resultado[r["mes"]].setdefault(r["dia"], {})
			resultado[r["mes"]][r["dia"]]=r["subtotal"]
		res["resultado"]=resultado
		print(resultado)
		return res
	raise f"No se pudo obtener resumen ventas  para {anio}"

# OBTIENE RESUMEN VENTAS SEMANAL
def selSemanaVentas(anio, mes, dia):	# CHECKED
	res = ven.selSemanaVentas(anio, mes, dia)
	if res["success"]:
		return res
	raise f"No se pudo borrar ventas pendientes para {anio, mes, dia}"

# OBTIENE VENTAS DE UN DIA
def selVentasDia(anio, mes, dia):	# CHECKED
	res = ven.selVentasDia(anio, mes, dia)
	if res["success"]:
		return res
	raise f"No se pudo borrar ventas pendientes para {anio, mes, dia}"

def findProductoEscaso():
	res = pro.findProductoEscaso()
	if res["success"]:
		return res
	raise f"No se obtuvo productos escasos"

def selCatalogoTruper():
	res = trup.selCatalogoTruper()
	if res["success"]:
		return res
	raise f"No se obtuvo productos escasos"

def setFechaVentaVenProds(productos, nuevaFecha):
	res = ven.setFechaVentaVenProds(productos, nuevaFecha)
	if not res["success"]:
		raise Exception(f"No se pudo cambiar fecha de venta {productos}")
	return res

def producto_exists(campo, valor, productoId):
	res = pro.producto_exists(campo, valor, productoId)
	if res["success"]:
		return res
	raise Exception(f"No se obtuvo productos escasos")

def backup_maestro_for_slave():
	res = db.backup_db_for_slave(config.BASE_MAESTRO_NAME, config.BASE_MAESTRO_BACKUP_SLAVE_NAME)
	print(f"backup_maestro_for_slave {res}")
	if res["success"]:
		res = db.backup_db(config.BASE_MAESTRO_BACKUP_SLAVE_NAME, config.BASE_MAESTRO_BACKUP_NAME)
		if res["success"]:
			return res
	raise Exception(f"No se obtuvo productos escasos")

def backup_maestro():
	#res = db.backup_db(config.BASE_MAESTRO_NAME, config.BASE_MAESTRO_BACKUP_NAME)
	#if res["success"]:
	res = backup_maestro_for_slave()
	if res["success"]:
		return res
	raise Exception(f"No se obtuvo productos escasos")

def entregasCargar(params):
	b64 = params["archivo_entrega"]
	costoTieneIva = params["costoTieneIva"]
	raw = base64.b64decode(b64)   # ← BYTES again
	archivoEntrega, encoding = decode_bytes(raw)
	print(f"Se decodifico archivo usando {encoding}")
	print(type(archivoEntrega))
	print(archivoEntrega)
	df = SimpleDF.from_tsv_text(archivoEntrega, sep=",")
	colEsperadas = ['no__pedido', 'fecha', 'no__orden', 'material', 'descripcion', 'cantidad', 'precio_unitario', 'subtotal']
	if not df.columns==colEsperadas:
		res = db.returnError()
		res["Error"]="El archivo no contiene las columnas esperadas: "+str(colEsperadas)
		return res
	df.rename_columns({'no__pedido':'entregaId', 'fecha':'fechaEntrega', 'no__orden':'pedidoId', 'material':'codigoEntrega', 
					'descripcion':'descripcionEntrega', 'cantidad':'existenciaEntrega', 
					'precio_unitario': 'costoEntrega' ,
					'subtotal':'subtotalEntrega'})
	#print(df.columns)
	productosEntrega = df.rows
	res = entregasBuscar(productosEntrega, costoTieneIva)
	if res["success"]:
		productosBuscados = res["resultado"]
		resultado = db.returnBlank()
		resultado["resultado"]={"productosEntrega":productosEntrega, "productosBuscados":productosBuscados}
		return resultado
	return db.returnError()
	

def entregasBuscar(productosEntrega, costoTieneIva):
	productosBuscados = copy.deepcopy(productosEntrega)
	print(productosBuscados)
	# codigosNumericos = []
	# for p in productosEntrega:
	# 	codigosNumericos.append(p["codigoNumerico"])
	res = pro.selProductoCodigosNumericos(productosBuscados)
	if res["success"]:
		# codigosNumericos=[]
		# for v in productosEntrega:
		# 	val = {"codigoNumerico": v["codigoNumerico"]}
		# 	if val not in codigosNumericos:
		# 		codigosNumericos.append(val)
		encontrados = pro.mapper.db_to_many(res["resultado"], pro.db_map_prod)
		encontrados = res["resultado"]#pro.mapper.db_to_many(res["resultado"], pro.db_map_prod)
		print(encontrados)
		if encontrados and len(encontrados)>0:
			iva = selIva()
			indexProd= {prod["codigoNumerico"]: prod for prod in encontrados}
			# Extend items in listA
			for llega in productosBuscados:
				orig = indexProd.get(int(llega["codigoEntrega"]))
				if orig:
					if orig["seCompraPor"]=="paquete":
						orig["nuevoPrecioPaquete"] = orig["precioPaquete"]
						orig["llegaExistenciaPaquetes"]=llega["existenciaEntrega"]
						if costoTieneIva:
							orig["llegaCostoSinIvaPaquete"]=(float(llega["costoEntrega"])/(1+iva/100))
							#orig["costoPaquete"]=orig["nuevoCostoPaquete"]
						else:
							orig["llegaCostoSinIvaPaquete"]=float(llega["costoEntrega"])
						orig["nuevoCostoSinIvaPaquete"]=orig["llegaCostoSinIvaPaquete"]
						if orig["numeroKgs"] and orig["numeroKgs"]>0:
							orig["nuevoPrecioKg"]=orig["precioKg"]
						if orig["numeroUnidades"] and orig["numeroUnidades"]>0:
							orig["nuevoPrecioUnidad"]=orig["precioUnidad"]
					elif orig["seCompraPor"]=="unidad":
						orig["nuevoPrecioUnidad"] = orig["precioUnidad"]
						orig["llegaExistenciaUnidades"]=llega["existenciaEntrega"]
						if costoTieneIva:
							orig["llegaCostoSinIvaUnidad"]=(float(llega["costoEntrega"])/(1+iva/100))
							#orig["costoUnidad"]=orig["nuevoCostoUnidad"]
						else:
							orig["llegaCostoSinIvaUnidad"]=float(llega["costoEntrega"])
						orig["nuevoCostoSinIvaUnidad"]=orig["llegaCostoSinIvaUnidad"]
					llega.update(orig)
			res["resultado"]=productosBuscados
	return res



	