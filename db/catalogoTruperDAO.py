import db.baseDatosDAO as db
import datetime
from fractions import Fraction
import db.dbMapper as mapper
import config

# CATALOGO TRUPER **********************************

def selTruperKgUnidades():
	sqlFile = db.get_sql_file("truper_kg_unidades")
	with db.connPorRol() as conn:
		return db.run_sql(conn, sqlFile, fetchRows=True)

db_map = {
	"codigoBarras": lambda x: x.split(".")[0] if "." in x else x,
    "precioDistribuidorConIva": float,
    "precioPublicoConIva": lambda x: float(x) if x not in ["*","",None] else None,
    "pesoKg": float,
    "barrasVerificada": bool,
	"imagenVerificada": bool,
    "numeroUnidades": lambda x: float(Fraction(x)) if "/" in x else (float(x) if x not in ["*","",None] else None),
    "costoUnidad":  lambda x: float(x) if x not in ["*","",None] else None,
    "costoPaquete": lambda x: float(x) if x not in ["*","",None] else None,
	"costoKg": lambda x: float(x) if x not in ["*","",None] else None,
    "sugeridoUnidad": lambda x: float(x) if x not in ["*","",None] else None,
    "sugeridoPaquete": lambda x: float(x) if x not in ["*","",None] else None,
	"sugeridoKg": lambda x: float(x) if x not in ["*","",None] else None,
    "numeroKgs": lambda x: float(Fraction(x)) if "/" in x else (float(x) if x not in ["*","",None] else None),
	"activo": lambda x: int(x) if x is not None else 1,
	"createdDate": "setDateTime",
	"modifiedDate": "setDateTime"
}

columnasTruper = ["codigo", "clave", "descripcion", "unidad", "precioDistribuidorConIva", "precioPublicoConIva", "descripcionFamilia", "pesoKg", "codigoBarras", 
		"barrasVerificada", "imagenVerificada", "unidadInv", "numeroKgs", "numeroUnidades", "descripcionInv", "costoUnidad", "costoPaquete", "costoKg", "sugeridoUnidad", "sugeridoPaquete", 
		"sugeridoKg", "createdDate", "modifiedDate", "activo"]

def crea_catalogo_truper():
	with open("sql/create_catalogo_truper.sql", "r") as f:
		query = f.read()
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		db.run_sql(conn, query)

def tira_catalogo_truper():
	db.drop_table(config.BASE_MAESTRO_NAME, "catalogo_truper")

def selCatalogoTruper(activo=True):
	#with open("sql/create_catalogo_truper.sql", "r") as f:
    #	query = f.read()
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		sqlStr = "select * from catalogo_truper"
		if activo:
			sqlStr+= " where activo = 1"
		return db.run_sql(conn, sqlStr, fetchRows=True)
		
def setCatalogoTruper(catalogo):
	#with open("sql/create_catalogo_truper.sql", "r") as f:
    #	query = f.read()
	catalogo = mapper.many_to_db(catalogo, db_map, setDateTime=True)
	with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
		conn.execute("BEGIN")
		db.run_sql(conn, "delete from catalogo_truper where activo=0")
		db.run_sql(conn, "update catalogo_truper set activo=0 where activo=1")
		sqlStr = f"insert into catalogo_truper ({', '.join(columnasTruper)}) values (:{', :'.join(columnasTruper)})"
		return db.run_sql(conn, sqlStr, catalogo)

def reload_catalogo_truper():
	inv_rows = db.read_tsv_to_dicts("../Truper/procesa_catalogo/catalogo_con_imagenes.tsv")
	#print(inv_rows)
	mapper.add_fields(inv_rows, {"created_date": datetime.datetime.now(), "modified_date": datetime.datetime.now()})
	with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
		print(db.run_sql(conn, "delete from catalogo_truper"))
		query = f"insert into catalogo_truper values ({', '.join(columnasTruper)}) "
		query+= f"values (:{', :'.join(columnasTruper)})"
		print(db.run_sql(conn, query, inv_rows))

# ************** INVENTARIO ********************

db_map_wip = {
    "costo": lambda x: float(x.replace("$","").replace(",","")),
    "precio": lambda x: float(x.replace("$","").replace(",","")) if x!="" else None,
    "inventario": lambda x: float(x) if x not in ["", "N/A"] else 0,
    "minimo": float,
    "costoPaqueteTruper": lambda x: float(x.replace("$","").replace(",","")) if x!="" else None,
    "costoUnidadTruper": lambda x: float(x.replace("$","").replace(",","")) if x!="" else None,
    "precioPaqueteTruper": lambda x: float(x.replace("$","").replace(",","")) if x!="" else None,
    "precioUnidadTruper": lambda x: float(x.replace("$","").replace(",","")) if x!="" else None,
    "pesoKg": lambda x: float(x) if x!="" else None,
    "numeroUnidades": lambda x: float(x) if x!="" else None,
    "costoUnidadComparacion": lambda x: float(x) if x!="" else None,
    "costoPaqueteComparacion": lambda x: float(x) if x!="" else None,
    "costoComparacion": lambda x: float(x) if x!="" else None,
    "precioUnidadComparacion": lambda x: float(x) if x!="" else None,
    "precioPaqueteComparacion": lambda x: float(x) if x!="" else None,
    "precioComparacion": lambda x: float(x) if x!="" else None,
    "diffDescripcionInv": lambda x: float(x) if x!="" else None,
    "numeroKgs": lambda x: float(x) if x!="" else None,
	"createdDate": "setDateTime",
	"modifiedDate": "setDateTime",
	"ultimaVenta": "setDateTime",
	"versionInventario": lambda x: 1
}

def crea_inventario_wip():
	with open("sql/create_inventario_wip.sql", "r") as f:
		query = f.read()
	with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
		db.run_sql(conn, query)

def tira_inventario_wip():
	db.drop_table(config.BASE_MAESTRO_NAME, "inventario_wip")

def sel_inventario_wip():
	#with open("sql/create_catalogo_truper.sql", "r") as f:
    #	query = f.read()
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		print(db.run_sql(conn, "select * from inventario_wip", fetchRows=True))

columnas_wip = ["codigoBarras", "codigoBarrasNuevo", "proveedor", "descripcion", "descripcionLimpia", "descripcionTruper", 
"descripcionTruperInv", "costo", "precio", "inventario", "minimo", "departamento", "pesoKg", "codigoNumerico", "codigoNumericoNuevo",
"codigosBuscar", "codigosBuscarNuevo", "unidad", "unidadInv", "numeroUnidades", "numeroKgs", "seCompraPor", "preferenciaVenta", 
"seVendePor", "costoEs", "costoUnidadSinIva", "costoUnidad", "costoUnidadTruper", "costoPaqueteSinIva", "costoPaquete", 
"costoPaqueteTruper", "costoKgSinIva", "costoKg", "costoKgTruper", "precioEs", "precioUnidad", "sugeridoUnidadTruper", 
"precioPaquete", "sugeridoPaqueteTruper", "precioKg", "sugeridoKgTruper", "costoUnidadComparacion", "costoPaqueteComparacion", 
"costoComparacion", "precioUnidadComparacion", "precioPaqueteComparacion", "precioComparacion", "diffDescripcionInv", 
"ultimaVenta", "activo", "createdDate", "modifiedDate", "comentario", "huboCambio", "versionInventario"]

new_fields_wip = {"createdDate": None, 
			"modifiedDate": None, 
			"ultimaVenta": None,
			"seCompraPor": "",
			"seVendePor": "",
			"preferenciaVenta": "",
			"costoPaquete": "",
			"costoPaqueteSinIva": "",
			"costoUnidad": "",
			"costoUnidadSinIva": "",
			"costoKg": "",
			"costoKgSinIva": "",
			"precioPaquete": "",
			"precioUnidad": "",
			"precioKg": "",
			"activo": 1,
			"versionInventario": 1
}

def reload_inventario_wip():
	inv_rows = db.read_tsv_to_dicts("../inventario/inventario_procesado.txt")
	#print(inv_rows)
	inv_rows = mapper.add_fields(inv_rows, new_fields_wip)
	with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
		print(db.run_sql(conn, "delete from inventario_wip"))
		query = f"insert into inventario_wip ({', '.join(columnas_wip)}) "
		query+= f"values (:{', :'.join(columnas_wip)})"
		db.run_sql(conn, query, inv_rows, db_map_wip)

def ajustes_inventario_wip():
	inv_rows = db.read_tsv_to_dicts("../inventario/inventario_procesado_ajustes.txt")
	#print(inv_rows)
	inv_rows = mapper.add_fields(inv_rows, new_fields_wip)
	with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
		print(db.run_sql(conn, "delete from inventario_wip where CodigoBarras=:CodigoBarras", inv_rows))
		query = f"insert into inventario_wip ({', '.join(columnas_wip)}) "
		query+= f"values (:{', :'.join(columnas_wip)})"
		db.run_sql(conn, query, inv_rows)

def backup_inventario_wip():
	with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
		db.run_sql(conn, "drop table if exists inventario_loaded")
		db.run_sql(conn, "create table inventario_loaded as select * from inventario_wip")

def setInventarioWIP(inventarioWip):
	#with open("sql/create_catalogo_truper.sql", "r") as f:
    #	query = f.read()
	inventarioWip = mapper.add_fields(inventarioWip, new_fields_wip)
	inventarioWip = mapper.many_to_db(inventarioWip, db_map_wip, setDateTime=True)
	with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
		conn.execute("BEGIN")
		db.run_sql(conn, "delete from inventario_wip where versionInventario<-3")
		db.run_sql(conn, "update inventario_wip set versionInventario=versionInventario-1")
		sqlStr = f"insert into inventario_wip ({', '.join(columnas_wip)}) values (:{', :'.join(columnas_wip)})"
		return db.run_sql(conn, sqlStr, inventarioWip)	