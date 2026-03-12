import db.baseDatosDAO as db
import datetime
from fractions import Fraction
import db.dbMapper as mapper
import config

db_map_prod = {
	"productoId": lambda x: int(x) if x else None,
	"codigoBarras": lambda x: db.createTimeCode() if not x else x,
	"codigoNumerico": lambda x: int(x) if x else None,
	"proveedorId": int,
	"preferenciaVenta": lambda x: int(x) if x else None,
	"numeroUnidades": lambda x: float(x) if x else None,
	"numeroKgs": lambda x: float(x) if x else None,
	"costoSinIvaUnidad": lambda x: float(x) if x else None,
	"precioUnidad": lambda x: float(x) if x else None,
	"costoSinIvaPaquete": lambda x: float(x) if x else None,
	"precioPaquete": lambda x: float(x) if x else None,
	"costoSinIvaKg": lambda x: float(x) if x else None,
	"precioKg": lambda x: float(x) if x else None,
	"muestraUnidad": bool,
	"muestraPaquete": bool,
	"muestraKg": bool,
	"existenciaUnidades": lambda x: float(x) if x else 0,
	"existenciaPaquetes": lambda x: float(x) if x else 0,
	"existenciaKgs": lambda x: float(x) if x else 0,
	"minimoUnidades": lambda x: float(x) if x else 0,
	"minimoPaquetes": lambda x: float(x) if x else 0,
	"minimoKgs": lambda x: float(x) if x else 0,
	"activo": bool
}

def _sel_producto(condiciones, condDict, db_map={}):
	sqlStr =  "select * from productos"
	if (condiciones and len(condiciones.strip())>0):
		sqlStr+=" "+condiciones
	db_map.update({"productoId": int})
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		res = db.run_sql(conn, sqlStr, data=condDict, fetchRows=True)
		print(res)
		return res
	
def selProductoId(productoId):	# CHECKED
	return _sel_producto("where productoId=:productoId", condDict={"productoId": productoId})

columnas_prod = ["productoId", "codigoBarras", "codigoNumerico","claves", "proveedorId", "descripcion", "preferenciaVenta", "seCompraPor", "numeroUnidades", "numeroKgs", 
				"unidadInv", "costoSinIvaUnidad", "precioUnidad", "costoSinIvaPaquete", "precioPaquete", "costoSinIvaKg", "precioKg", "muestraUnidad", 
				"muestraPaquete", "muestraKg", "existenciaUnidades", "existenciaPaquetes", "existenciaKgs", "minimoUnidades", "minimoPaquetes", "minimoKgs", 
				"ultimaVenta", "activo", "created_date", "modified_date"]

def insProducto(prod):		# CHECKED
	prod = mapper.one_to_db(prod, db_map_prod, False)
	return _ins_producto(prod)

def _ins_producto(prod):
	columnas = columnas_prod[:]
	columnas.remove("productoId")
	columnas.remove("ultimaVenta")
	new_fields_prod = { 
		"modified_date": datetime.datetime.now(),
		"created_date": datetime.datetime.now()
	}
	prod = mapper.add_fields(prod, new_fields_prod)
	query = f"insert into productos ({', '.join(columnas)}) "
	query+= f"values (:{', :'.join(columnas)})"
	with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
		res = db.run_sql(conn, query, prod, returnCols=["codigoBarras", "modified_date", "productoId"])
		print(res)
		return res
	
def modProducto(prod):		# CHECKED
	prod = mapper.one_to_db(prod, db_map_prod, False)
	return _mod_producto(prod)

def _mod_producto(prod):
	columnas = columnas_prod[:]
	columnas.remove("productoId")
	columnas.remove("created_date")
	columnas.remove("ultimaVenta")
	new_fields_inv = { 
		"modified_date": datetime.datetime.now()
	}
	prod = mapper.add_fields(prod, new_fields_inv)
	queryStr = "update productos set "
	queryStr+= db.getColValPairStr(columnas)
	queryStr+= " where productoId=:productoId"
	with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
		res = db.run_sql(conn, queryStr, prod, returnCols=[ "codigoBarras", "modified_date", "productoId"] )
		print(res)
		return res

# FIND producto LOGIC USING FILE WITH QUERY

sqlStrFindProducto = db.get_sql_file("find_producto")

def findProducto(searchString, buscaActivo=True):		# CHECKED
	print("findProducto searchString "+searchString)
	sqlStr = sqlStrFindProducto[:]
	#sqlStr = sqlStr.replace(r"{simple_columns}", r"productoId, codigoBarras, codigoNumerico, claves, descripcion, muestraUnidad, muestraPaquete, muestraKg, unidadInv, preferenciaVenta, proveedor, activo")
	sqlStr = sqlStr.replace(r"{simple_columns}", r"a.*")
	sqlStr = sqlStr.replace(r"{conditions}", r"(codigoBarras like '%{searchString}%' or claves like '%{searchString}%' or descripcion like '%{searchString}%' or codigoNumerico like '%{searchString}%') {conditions}")
	if buscaActivo:
		sqlStr = sqlStr.replace(r"{conditions}", r"and (activo and (muestraUnidad or muestraPaquete or muestraKg))")
	else:
		sqlStr = sqlStr.replace(r"{conditions}", r"")
	sqlStr = sqlStr.replace(r"{searchString}", searchString)
	orderString = f"CASE WHEN LOWER(descripcion) = LOWER('{searchString}') " \
		f"OR LOWER(descripcion) LIKE '{searchString} %' " \
		f"OR LOWER(descripcion) LIKE '% {searchString}' " \
		f"OR LOWER(descripcion) LIKE '% {searchString} %' THEN 0 ELSE 1 END, " \
		f"precio, descripcion"
	sqlStr = sqlStr.replace(r"{order_by}", orderString)
	print(sqlStr)
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		res = db.run_sql(conn, sqlStr, data=None, fetchRows=True)
		print(f"findProducto {res}")
		return res


def findProductoEscaso(buscaActivo=True):
	sqlStr = sqlStrFindProducto[:]
	sqlStr = sqlStr.replace(r"{simple_columns}", r"a.*") 
	strCondiciones = r"existenciaUnidades < ifnull(minimoUnidades ,0) or existenciaPaquetes <  ifnull(minimoPaquetes ,0) " \
	r"or existenciaKgs <  ifnull(minimoKgs ,0) {conditions}"
	sqlStr = sqlStr.replace(r"{conditions}", strCondiciones )
	if buscaActivo:
		sqlStr = sqlStr.replace(r"{conditions}", r"and (activo and (muestraUnidad or muestraPaquete or muestraKg))")
	else:
		sqlStr = sqlStr.replace(r"{conditions}", r"")
	sqlStr = sqlStr.replace(r"{order_by}", r"case when numeroUnidades>0 or numeroKgs>0 then existenciaPaquetes else existenciaUnidades end")
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		res = db.run_sql(conn, sqlStr, data=None, fetchRows=True)
		return res


def findProductoBarras(codigoBarras, buscaActivo=True):	# CHECKED
	print("findProductoBarras "+codigoBarras)
	sqlStr = sqlStrFindProducto[:]
	sqlStr = sqlStr.replace(r"{simple_columns}", r"a.*") 
	sqlStr = sqlStr.replace(r"{conditions}", r"codigoBarras=:codigoBarras {conditions}")
	if buscaActivo:
		sqlStr = sqlStr.replace(r"{conditions}", r"and (activo and (muestraUnidad or muestraPaquete or muestraKg))")
	else:
		sqlStr = sqlStr.replace(r"{conditions}", r"")
	sqlStr = sqlStr.replace(r"{order_by}", r"precio, descripcion")
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		res = db.run_sql(conn, sqlStr, data=[{"codigoBarras": codigoBarras}], fetchRows=True)
		return res

def findProductoId(productoId, buscaActivo=True):	# CHECKED
	sqlStr = sqlStrFindProducto[:]
	sqlStr = sqlStr.replace(r"{simple_columns}", r"a.*") 
	sqlStr = sqlStr.replace(r"{conditions}", r"productoId=:productoId {conditions}")
	if buscaActivo:
		sqlStr = sqlStr.replace(r"{conditions}", r"and (activo and (muestraUnidad or muestraPaquete or muestraKg))")
	else:
		sqlStr = sqlStr.replace(r"{conditions}", r"")
	sqlStr = sqlStr.replace(r"{order_by}", r"precio, descripcion")
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		res = db.run_sql(conn, sqlStr, data=[{"productoId": int(productoId)}], fetchRows=True)
		return res
	
def findProductoClaves(claves, buscaActivo=True):	# CHECKED
	sqlStr = sqlStrFindProducto[:]
	sqlStr = sqlStr.replace(r"{simple_columns}", r"a.*") 
	sqlStr = sqlStr.replace(r"{conditions}", r"claves like :claves {conditions}")
	if buscaActivo:
		sqlStr = sqlStr.replace(r"{conditions}", r"and (activo and (muestraUnidad or muestraPaquete or muestraKg))")
	else:
		sqlStr = sqlStr.replace(r"{conditions}", r"")
	sqlStr = sqlStr.replace(r"{order_by}", r"precio, descripcion")
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		res = db.run_sql(conn, sqlStr, data=[{"claves": f"%{claves}%"}], fetchRows=True)
		return res
	
def findProductoNumerico(codigoNumerico, buscaActivo=True):		# CHECKED
	sqlStr = sqlStrFindProducto[:]
	sqlStr = sqlStr.replace(r"{simple_columns}", r"a.*") 
	sqlStr = sqlStr.replace(r"{conditions}", r"codigoNumerico like :codigoNumerico {conditions}")
	if buscaActivo:
		sqlStr = sqlStr.replace(r"{conditions}", r"and (activo and (muestraUnidad or muestraPaquete or muestraKg))")
	else:
		sqlStr = sqlStr.replace(r"{conditions}", r"")
	sqlStr = sqlStr.replace(r"{order_by}", r"precio, descripcion")
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		res = db.run_sql(conn, sqlStr, data=[{"codigoNumerico": f"%{codigoNumerico}%"}], fetchRows=True)
		return res
	#db_map={"codigo": lambda x: f'%{x}%'}, 
	
def _calc_cant_vendidas(prod):
	cantUnidades = None
	cantPaquetes = None
	cantKgs = None
	res = findProductoId(prod["productoId"], False)
	if res["success"] and res["resultado"]!=None and len(res["resultado"])==1:
		prodinv = res["resultado"][0]
		if prod["tipoVentaId"]==-1:
			cantUnidades = prod["cantidad"]
			if prodinv["numeroUnidades"]!=None and prodinv["numeroUnidades"]>1:
				cantPaquetes = round(cantUnidades*1.00 / prodinv["numeroUnidades"],2)
				if prodinv["numeroKgs"]!=None and prodinv["numeroKgs"]>0:
					cantKgs = round(cantPaquetes*prodinv["numeroKgs"],2)
		if prod["tipoVentaId"]==-2:
			cantPaquetes = prod["cantidad"]
			if prodinv["numeroUnidades"]!=None and prodinv["numeroUnidades"]>1:
				cantUnidades = round(cantPaquetes*1.00 * prodinv["numeroUnidades"],2)
			if prodinv["numeroKgs"]!=None and prodinv["numeroKgs"]>0:
				cantKgs = round(cantPaquetes*1.00 * prodinv["numeroKgs"],2)
		if prod["tipoVentaId"]==-3:
			cantKgs = prod["cantidad"]
			if prodinv["numeroKgs"]!=None and prodinv["numeroKgs"]>0:
				cantPaquetes = round(cantKgs*1.00 / prodinv["numeroKgs"],2)
			if prodinv["numeroUnidades"]!=None and prodinv["numeroUnidades"]>1:
				cantUnidades = round(cantPaquetes*1.00 * prodinv["numeroUnidades"],2)
	else:
		raise Exception(f"No se encontro producto: {prod}")
	return cantUnidades, cantPaquetes, cantKgs

# def modInvProductos(conn, venta, marcaUltimaVenta=False):
# 	venta = mapper.many_to_db(venta, db_map_prod)
# 	for prod in venta:
# 		if prod["productoId"]>0:
# 			res = _mod_inv_prods(conn, prod, marcaUltimaVenta)
# 			if not res["success"]:
# 				raise f"No se pudo actualizar producto para {prod}"
# 		else:
# 			prod["fechaInventario"]=datetime.datetime.now()
# 			print(f"**** PRODUCTO NO REQUIERE INVENTARIO {prod}")
# 	res = db.returnBlank()
# 	res["resultado"]=venta
# 	return res

def _mod_inv_prod(conn, prod, marcaUltimaVenta=False):
	if prod["tipoVentaId"]>=-3 and not prod["sinInventario"]:
		cantidadUnidades, cantidadPaquetes, cantidadKgs = _calc_cant_vendidas(prod)
		strUpdate = f"update productos set "
		if cantidadUnidades!=None:
			strUpdate += f" existenciaUnidades = existenciaUnidades {'+' if prod.get('cancelada',False) else '-'} :cantidadUnidades,"
		if cantidadPaquetes!=None:
			strUpdate += f" existenciaPaquetes = existenciaPaquetes {'+' if prod.get('cancelada',False) else '-'} :cantidadPaquetes,"
		if cantidadKgs!=None:
			strUpdate += f" existenciaKgs = existenciaKgs {'+' if prod.get('cancelada',False) else '-'} :cantidadKgs,"
		if (marcaUltimaVenta):
			strUpdate += "ultimaVenta = :ultimaVenta "
		else:
			strUpdate = strUpdate[:-1]
		#strUpdate += "modified_date = :modified_date "
		strUpdate += " where productoId = :productoId"
		newFields = { "cantidadUnidades": cantidadUnidades,
				"cantidadPaquetes": cantidadPaquetes,
				"cantidadKgs" : cantidadKgs,
				"ultimaVenta" : prod["fechaVenta"]
		}
		#returnCols = ["modified_date"]
		mapper.add_fields([prod], newFields)
		print(f"prod to update inv {prod}")
		res = db.run_sql(conn,strUpdate, [prod], returnCols=["existenciaUnidades", "existenciaPaquetes", "existenciaKgs"])
		if res["success"]:
			prod["fechaInventario"]=res["execDatetime"]
			prod["existenciaUnidades"]=res["existenciaUnidades"]
			prod["existenciaPaquetes"]=res["existenciaPaquetes"]
			prod["existenciaKgs"]=res["existenciaKgs"]
			if prod["tipoVentaId"]==-1:
				prod["existencia"]=res["existenciaUnidades"]
			elif prod["tipoVentaId"]==-2:
				prod["existencia"]=res["existenciaPaquetes"]
			elif prod["tipoVentaId"]==-3:
				prod["existencia"]=res["existenciaKgs"]
		else:
			raise Exception(f"No se pudo actualizar cantidad en producto {prod}")
	elif prod["tipoVentaId"]<=-4 or prod["sinInventario"]:
		prod["fechaInventario"]=datetime.datetime.now()
	return db.returnBlank()

def _mod_inv_prods(conn, prods, marcaUltimaVenta=False):
	print(f"upd_inv_prod {prods}")
	# if isinstance(prod, (list, tuple)) and len(prod)==1:
	# 	prod = prod[0]
	resTotal = db.returnBlank()
	for prod in prods:
		res = _mod_inv_prod(conn, prod, marcaUltimaVenta)
		if not res["success"]:
			resTotal = db.returnError()
	return resTotal

def selProductoIds(productosId):	# CHECKED
	strSql = "select * from productos where productoId in (:productoId)"
	newStrSql, newObjs, newDBMap = mapper.genMultiParamStrMap(strSql, productosId, {"productoId": int})
	print(newStrSql, newObjs, newDBMap)
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		res = db.run_sql(conn, query=newStrSql, data=newObjs, fetchRows=True)
		if res["success"]:
			return res
	raise f"No se encontro producto para {productosId}"


def selProductoCodigosNumericos(codigosNumericos):	# CHECKED
	prods = mapper.many_to_db(codigosNumericos, db_map_prod, False)
	strSql = "select * from productos where codigoNumerico in (:codigoEntrega)"
	newStrSql, newObjs, newDBMap = mapper.genMultiParamStrMap(strSql, prods, {"codigoEntrega": int})
	print(newStrSql, newObjs, newDBMap)
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		res = db.run_sql(conn, query=newStrSql, data=newObjs, fetchRows=True)
		if res["success"]:
			return res
	raise f"No se encontro producto para {codigosNumericos}"

def producto_exists(campo, valor, productoId):
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		res = db.run_sql(conn, f"select productoId from productos where {campo}=:valor", data=[{"valor": valor}], fetchRows=True)
		if res["success"]: 
			if productoId:
				if res["resultado"] and len(res["resultado"])>0:
					if int(res["resultado"][0]["productoId"])==int(productoId):
						res["resultado"][0]["exists"]=False
					else:
						res["resultado"][0]["exists"]=True
				else:
					res["resultado"]=[{"exists":False}]
			else:
				if res["resultado"] and len(res["resultado"])>0:
					res["resultado"][0]["exists"]=True
				else:
					res["resultado"]=[{"exists":False}]
			return res

		else:
			raise f"No se encontro {campo} valor {valor} con {productoId}"




