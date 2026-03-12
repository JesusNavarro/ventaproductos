import db.baseDatosDAO as db
import db.dbMapper as mapper
import config

registro_columnas = ["dispositivoId", "direccionIP", "nombre", "rol", "soy"]

registro_db_map = {
    "dispositivoId" : lambda x: db.createTimeCode() if not x else x,
    "soy" : bool
}

def insRegistro(registro):      # CHECKED
    registro = mapper.one_to_db(registro, registro_db_map)
    return _ins_registro(registro)

def _ins_registro(registro):
    with db.conn_ctx(config.BASE_DEVICE_NAME, True) as conn:
        sqlStr = f"insert into registros ({','.join(registro_columnas)}) values (:{', :'.join(registro_columnas)})"
        res = db.run_sql(conn, sqlStr, data=registro, returnCols=["dispositivoId", "direccionIP"])
        return res

def selRegistros():     # CHECKED
    if db.exists_db(config.BASE_DEVICE_NAME):
        with db.conn_ctx(config.BASE_DEVICE_NAME) as conn:
            if db.exists_table(conn, "registros"):
                print("registro exists")
                res = db.run_sql(conn, "select * from registros", data=None, fetchRows=True)
                if res["success"]: return res 
    return db.returnBlank()

def modRegistro(registro):  # CHECKED
    registro = mapper.one_to_db(registro, registro_db_map)
    return _mod_registro(registro)

def _mod_registro(registro):    
    with db.conn_ctx(config.BASE_DEVICE_NAME, True) as conn:
        sqlStr = "update registros set direccionIP=:direccionIP where dispositivoID=:dispositivoId"
        return db.run_sql(conn, sqlStr, data=registro)

