import db.baseDatosDAO as db
from fractions import Fraction
import datetime
import db.dbMapper as mapper
import config

def _tira_proveedor():
	db.drop_table(config.BASE_MAESTRO_NAME, "proveedor")

def selProveedores():		# CHECKED
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		return db.run_sql(conn, "select * from proveedores", fetchRows=True)
	
def setAjustesVariable(registro_variable):		# CHECKED
	registro_variable = mapper.one_to_db(registro_variable)
	return _ups_ajustes_variable(registro_variable)

def _ups_ajustes_variable(registro_variable):
	sqlStr = "INSERT INTO ajustes (variable, valor, desde) VALUES (:variable, :valor, :desde) " \
        "ON CONFLICT(variable, desde) " \
        "DO UPDATE SET valor = excluded.valor"
	with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
		return db.run_sql(conn, sqlStr, data=registro_variable)

def delAjustesVariable(registro_variable):	# CHECKED
	registro_variable = mapper.one_to_db(registro_variable)
	return _del_ajustes_variable

def _del_ajustes_variable(registro_variable):
	sqlStr = "delete from ajustes where variable=:variable and desde=:desde"
	with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
		return db.run_sql(conn, sqlStr, data=registro_variable)
	
def selAjustesVariables():		# CHECKED
	sqlStr = "select * from ajustes order by variable, desde"
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		return db.run_sql(conn, sqlStr, fetchRows=True)

def selAjustesVariable(nombre, desde=None):		# CHECKED
	print(f"sel_ajuste {nombre, desde}")
	data={"variable" : nombre}
	if desde is None:
		desde = datetime.datetime.now()
	data["desde"]=desde
	print(f"data {data}")
	sqlStr = "select * from ajustes WHERE variable = :variable AND desde <= :desde "\
		"ORDER BY desde DESC LIMIT 1"
	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
		return db.run_sql(conn, sqlStr, [data], fetchRows=True)



