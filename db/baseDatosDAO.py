import sqlite3, os, re, csv, datetime
from contextlib import contextmanager
import config

##### CORRECT DB PATH WITH OR WITHOUT FLASK

def db_path(database_name):
    return os.path.join(config.MODELS_PATH, f"{database_name}")

def sql_file_path(file_name):
    return os.path.join(config.SQL_PATH, f"{file_name}")

def get_sql_file(sqlFile):
    with open(sql_file_path(f"{sqlFile}.sql"), "r") as f:
        return f.read()
    
# def attach_db(conn, database_name, alias):
#     res = run_sql(conn, f"attach database '{db_path(database_name)}.db' as {alias}")
#     if res["success"]:
#         return True
#     return False

@contextmanager
def attach_db(conn, database_name, alias):
    conn.execute(f"ATTACH DATABASE '{db_path(database_name)}.db' AS {alias}")
    try:
        yield
    finally:
        conn.execute(f"DETACH DATABASE {alias}")

##### CREATE DATABASE

def exists_db(database_name):
    return os.path.exists(f"{db_path(database_name)}.db")

def exists_table(conn, table_name):
    res = run_sql(conn, f"select * from sqlite_master WHERE type='table' AND name='{table_name.strip()}'", fetchRows=True)
    if res["success"] and res["resultado"]!=None and len(res["resultado"])>0 and res["resultado"][0]["name"]==table_name:
        return True
    return False

def create_db(database_name):
    if not os.path.exists(f"{db_path(database_name)}.db"):
        print(f"DB {db_path(database_name)}.db does not exist — creating it now...")
        conn = sqlite3.connect(f"{db_path(database_name)}.db")
        if (conn):
            conn.row_factory = dict_factory #sqlite3.Row
        return conn
    else:
        raise Exception(f"DB {db_path(database_name)}.db ya existe")

def overwrite_db(database_name):
    if not os.path.exists(f"{db_path(database_name)}.db"):
        print(f"DB {db_path(database_name)}.db does not exist — creating it now...")
    else:
        print(f"DB {db_path(database_name)}.db ya existia")
    return sqlite3.connect(f"{db_path(database_name)}.db")

def drop_db(database_name):
    if os.path.exists(f"{db_path(database_name)}.db"):
        print(f"DB {db_path(database_name)}.db exists — dropping it now...")
        os.remove(f"{db_path(database_name)}.db")
    else:
        raise Exception(f"DB {database_name}.db ya existia")

##### DATABASE CONNECTIONS

def dict_factory(cursor, row):
    """
    Converts SQLite rows into Python dictionaries automatically.
    cursor.description gives column names, row is tuple of values.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def connPorRol(write=False):
    if config.myRol() is not None:
        print(config.myRol())
        return conn_ctx(f"base_{config.myRol()}", write)
    raise Exception("No hay rol MS para conexion BD")

@contextmanager
def conn_ctx(database_name, write=False):
    conn = None
    try:
        mode = "rw" if write else "ro"
        conn = sqlite3.connect(
            f"file:{db_path(database_name)}.db?mode={mode}", 
            uri=True,
            timeout=5
        )
        conn.row_factory = dict_factory
        yield conn  # This is where your query runs
        if write:
            conn.commit()      # GUARANTEED COMMIT if no exception
    except Exception as e:
        if write and conn:
            print("*** ROLLBACK ***")
            conn.rollback()    # GUARANTEED ROLLBACK on error
        raise e                # Re-raise so you see the error
    finally:
        if conn:
            conn.close()       # GUARANTEED CLOSE

def get_conn(database_name):
    try:
        conn = sqlite3.connect(f"file:{db_path(database_name)}.db?mode=ro", uri=True)
        if (conn):
            conn.row_factory = dict_factory
        return conn
    except Exception as e:
        print(f"Conexion a {database_name} no lograda: {e}")
    

def get_conn_rw(database_name):
    try:
        conn = sqlite3.connect(f"file:{db_path(database_name)}.db?mode=rw", uri=True)
        if (conn):
            conn.row_factory = dict_factory
        return conn
    except Exception as e:
        print(f"Conexion a {database_name} no lograda")

##### BACKUP DATABASE

def backup_db(database_name, backup_name=None):
    if backup_name is None:
        backup_name = f"{database_name}_backup"
    try:
        with conn_ctx(database_name, True) as conn:
            with overwrite_db(backup_name) as conn_backup:
                conn.backup(conn_backup)
         # sanity check
        with conn_ctx(backup_name) as test_conn:
            test_conn.execute("PRAGMA schema_version;")
        return returnBlank()
    except Exception as e:
        print(f"Backup failed: {e}")
        return returnError(f"Backup failed: {e}")

def backup_db_for_slave(database_name, backup_name=None):
    if backup_name is None:
        backup_name = f"{database_name}_backup_slave"
    try:
        print("************ backup_db_for_slave")
        print(database_name)
        print(backup_name)
        print("Checar si existe bd")
        if exists_db(backup_name):
            print("**** borrando bd")
            drop_db(backup_name)
        print("creando bd")
        #overwrite_db(backup_name)
        slave_attach_name = f"{db_path(backup_name)}.db"
        print(slave_attach_name)
        with conn_ctx(database_name, True) as src:
            print("Coneccion a base de datos")
            #with conn_ctx(backup_name, True) as dst:
            # Attach destination
            print("Coneccion a base de datos esclavo")
            print("Slave path:", slave_attach_name)
            print("Exists:", os.path.exists(slave_attach_name))
            src.execute(f"ATTACH DATABASE '{slave_attach_name}' AS partial;")
            print("Se agrego base de datos")
            for table in ["productos", "proveedores", "ajustes"]:
                # Copy schema
                src.execute(f"""
                    CREATE TABLE partial.{table}
                    AS SELECT * FROM main.{table};
                """)
                print("Se crearon tablas")
            tabla_ventas = "ventas"
            print("a crear ventas")
            src.execute(f"""
                    CREATE TABLE partial.ventas
                    AS SELECT a.* FROM main.ventas a, main.ventas_esclavos b
                    where a.dispositivoId =b.dispositivoId and a.fechaVenta =b.fechaVenta;""")
            print("Se crearon ventas")
            src.execute("DETACH DATABASE partial;")
            print("Se quito bd")
            src.commit()
            print("Se hizo commit")
        with conn_ctx(backup_name) as test_conn:
            test_conn.execute("PRAGMA schema_version;")
            print("Se verifico conexion a bd esclavo")
        print("a regresar exito")
        return returnBlank()
    except Exception as e:
        print(f"Backup failed: {e}")
        return returnError(f"Backup failed: {e}")

##### TARNSACTION DECORATOR

# Decorator for transactional functions
def transactional(func):
    def wrapper(*args, **kwargs):
        conn = get_conn_rw()
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    return wrapper

##### QUERY EXECUTIONS


def sql_extract_params(query):
    """Extracts all parameter names from :param in SQL query."""
    return list(dict.fromkeys(re.findall(r":(\w+)", query)))  # unique & ordered

def extract_param_rows(data, param_list):
    """
    Normalize input into a list of dictionaries with needed params.
    Accepts:
        - dict
        - object
        - list of dicts
        - list of objects
    """
    rows = []
    if data is None or not isinstance(data, (list, tuple)):
        return rows
    for item in data:
        row = {}
        if isinstance(item, dict):
            for p in param_list:
                row[p] = item.get(p, None)
        # else:
        #     # Extract values from object attributes
        #     for p in param_list:
        #         row[p] = getattr(item, p, None)
        rows.append(row)
    return rows

def run_script(conn, query):
    try:
        cur = conn.cursor()
        cur.executescript(query)
        return returnBlank()
    except Exception as e:
        return returnError(e)

def _extract_table_name(query: str) -> str:
    """
    Extracts table name from:
    INSERT INTO table (...)
    UPDATE table SET ...
    """
    q = query.strip().upper()

    if q.startswith("INSERT"):
        m = re.search(r"INSERT\s+INTO\s+([^\s(]+)", query, re.IGNORECASE)
    elif q.startswith("UPDATE"):
        m = re.search(r"UPDATE\s+([^\s]+)", query, re.IGNORECASE)
    else:
        raise Exception("Cannot extract table name for RETURNING fallback")
    if not m:
        raise Exception("Failed to parse table name")
    return m.group(1)

def run_sql(conn, query, data=None, fetchRows=False, returnCols=None):
    try:
        param_list = sql_extract_params(query)
        param_data = None
        if data:
            param_data = extract_param_rows(data, param_list)
        if data and len(param_data) == 0:
            raise Exception(f"No se pudo extraer parametros de los datos del registro {data}")

        execDatetime = datetime.datetime.now()
        cur = conn.cursor()
        using_returning = (
            not fetchRows
            and returnCols
            and len(returnCols) > 0
            and not config.OLD_SQL_LITE
        )
        if param_data:
            if len(param_data) > 1:
                print(f"query: {query} *** data: {param_data[0]}")
                cur.executemany(query, param_data)
            else:
                final_query = query
                if using_returning:
                    final_query += " RETURNING " + ",".join(returnCols)
                print(f"query: {query} *** data: {param_data[0]}")
                cur.execute(final_query, param_data[0])
        else:
            print(f"query: {query}")
            cur.execute(query)
        # ---------------- FETCH ROWS ----------------
        if fetchRows:
            rows = cur.fetchall()
            return {
                "success": True,
                "rowCount": cur.rowcount,
                "rowId": cur.lastrowid,
                "resultado": rows,
                "error": None,
                "execDatetime": execDatetime
            }
        # ---------------- NO FETCH ROWS ----------------
        res = {
            "success": True,
            "rowCount": cur.rowcount,
            "rowId": cur.lastrowid,
            "resultado": None,
            "error": None,
            "execDatetime": execDatetime
        }
        # ---------- RETURNING (modern SQLite) ----------
        if using_returning:
            row = cur.fetchone()
            if row:
                for c in returnCols:
                    res[c] = row[c]
            return res
        # ---------- FALLBACK (old SQLite) ----------
        if (
            config.OLD_SQL_LITE
            and param_data is not None
            and len(param_data) == 1
            and returnCols
            and len(returnCols) > 0
            and cur.lastrowid
        ):
            table = _extract_table_name(query)
            cols = ",".join(returnCols)
            select_sql = f"SELECT {cols} FROM {table} WHERE rowid = ?"
            print(f"returningQuery: {select_sql} *** data: {cur.lastrowid}")
            cur.execute(select_sql, (cur.lastrowid,))
            row = cur.fetchone()
            if row:
                for c in returnCols:
                    res[c] = row[c]
        return res
    except Exception as e:
        raise e
    
# def run_sql(conn, query, data=None, fetchRows=False, returnCols=None):
#     """
#     Executes SQL using named parameters automatically extracted from the query.
#     Supports:
#         - Single dict or object
#         - List of dicts or objects
#     """
#     try:
#         param_list = sql_extract_params(query)
#         param_data=None
#         if data:
#             param_data = extract_param_rows(data, param_list)
#             #rows_data =  apply_db_map(rows_data, db_map, setDateTime)
#         if data and len(param_data)==0:
#             raise Exception(f"No se pudo extraer parametros de los datos del registro {data}")
#         execDatetime = datetime.datetime.now()
#         cur = conn.cursor()
#         if param_data:
#             # executemany if list, execute if single
#             if len(param_data) > 1:
#                 print(f"query: {query} *** data: {param_data[0]}")
#                 cur.executemany(query, param_data)
#             else: 
#                 if not fetchRows and returnCols is not None and len(returnCols)>0:
#                     query+= " RETURNING "+",".join(returnCols)
#                 print(f"query: {query} *** data: {param_data[0]}")
#                 cur.execute(query, param_data[0])
#         else:
#             cur.execute(query)
#             print(f"query: {query}")

#         if fetchRows:
#             rows = cur.fetchall()
#             # rows = [
#             #     convert_from_db(r, select_map or {})
#             #     for r in rows
#             # ]
#             return {
#                 "success": True,
#                 "rowCount": cur.rowcount,
#                 "rowId": cur.lastrowid,
#                 "resultado": rows,
#                 "error": None,
#                 "execDatetime": execDatetime
#             }
#         else:
#             res = {
#                 "success": True,
#                 "rowCount": cur.rowcount,
#                 "rowId": cur.lastrowid,
#                 "resultado": None,
#                 "error": None,
#                 "execDatetime": execDatetime
#             }
#             if param_data!=None and len(param_data) == 1 and returnCols is not None and len(returnCols)>0 and not fetchRows:
#                 row = cur.fetchone()
#                 for c in returnCols:
#                     res[c]=row[c]
#             return res
#     except Exception as e:
#         raise e
#         return {
#             "success": False,
#             "rowCount": 0,
#             "rowId": None,
#             "resultado": None,
#             "error": str(e),
#             "execDatetime": datetime.datetime.now()
#         }

def returnError(excep=None):
    return {
        "success": False,
        "rowCount": 0,
        "rowId": None,
        "resultado": None,
        "error": "Error por defecto" if excep==None else str(excep)
    }

def returnBlank():
    return {
        "success": True,
        "rowCount": None,
        "rowId": None,
        "resultado": None,
        "error": None
    }

###### READ FILES 

def read_tsv_to_dicts(path):
    rows = []
    with open(path, "r", encoding="utf-16") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(dict(row))  # convert OrderedDict → dict
    return rows

##### ELIMINAR TABLA

def drop_table(database_name, tabla):
    with conn_ctx(database_name, True) as conn:
        print(run_sql(conn, f"drop table {tabla}"))

##### DESCRIBIR TABLA 

def describir(database_name, tabla):
    with conn_ctx(database_name) as conn:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({tabla})")
        rows = cur.fetchall()
        for r in rows:
            print(r)

###### STRING SQLS

def getColValPairStr(columnas):
    return ", ".join(f"{c} = :{c}" for c in columnas)

def createTimeCode():
	dt = str(datetime.datetime.now())
	return dt[:dt.rfind(".")].replace("-","").replace(" ","").replace(":","")

def create_registro():
    if not exists_db(config.BASE_DEVICE_NAME):
        create_db(config.BASE_DEVICE_NAME)
    with conn_ctx(config.BASE_DEVICE_NAME, True) as conn:
        if not exists_table(conn, "registros"):
            r= run_sql(conn, query=get_sql_file("create_registros"))
            if not r["success"]: raise r["error"]

def create_esclavo():
    if not exists_db(config.BASE_ESCALVO_NAME):
        create_db(config.BASE_ESCALVO_NAME)
    with conn_ctx(config.BASE_ESCALVO_NAME, True) as conn:
        if not exists_table(conn, "ventas"):
            r= run_sql(conn, get_sql_file("create_ventas"))
            if not r["success"]: raise r["error"]

def create_maestro():
    if not exists_db(config.BASE_MAESTRO_NAME):
        create_db(config.BASE_MAESTRO_NAME)
    with conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
        if not exists_table(conn, "ventas"):
            strFile = get_sql_file("create_ventas")
            r = run_sql(conn, strFile)
            if not r["success"]: raise r["error"]
        if not exists_table(conn, "ventas_esclavos"):
            r = run_sql(conn, strFile.replace(" ventas ", " ventas_esclavos "))
            if not r["success"]: raise r["error"]
        if not exists_table(conn, "proveedores"):
            r = run_script(conn, get_sql_file("create_proveedores"))
            if not r["success"]: raise r["error"]
        if not exists_table(conn, "catalogo_truper"):
            r = run_sql(conn, get_sql_file("create_catalogo_truper"))
            if not r["success"]: raise r["error"]
        if not exists_table(conn, "productos"):
            r = run_sql(conn, get_sql_file("create_productos"))
            if not r["success"]: raise r["error"]
        if not exists_table(conn, "productos_wip"):
            strFile = get_sql_file("create_productos")
            r = run_sql(conn, strFile.replace("productos", "productos_wip"))
            if not r["success"]: raise r["error"]
        if not exists_table(conn, "ajustes"):
            r = run_sql(conn, get_sql_file("create_ajustes"))
            if not r["success"]: raise r["error"]
        if not exists_table(conn, "catalogo_truper"):
            r = run_sql(conn, get_sql_file("create_catalogo_truper"))
            if not r["success"]: raise r["error"]
        if not exists_table(conn, "inventario_wip"):
            r = run_sql(conn, get_sql_file("create_inventario_wip"))
            if not r["success"]: raise r["error"]