import db.baseDatosDAO as db
from datetime import datetime
from fractions import Fraction
import config
import db.productosDAO as pro
import db.dbMapper as mapper

columnas_venta = ["dispositivoId", "productoId", "tipoVentaId", "precio", "precioVenta", "cantidad", "subtotal", "fechaVenta", "fechaInventario", "extraInfo", "cancelada", "sinInventario"]

db_map_venta = {
    "productoId" :  int,
    "tipoVentaId" : lambda x: int(x) if x  else None,
    "precio": lambda x: float(x) if x  else None,
    "precioVenta": lambda x: float(x) if x  else None,
    "cantidad": lambda x: float(x) if x  else None,
    "subtotal": lambda x: float(x) if x  else None,
    "fechaVenta": "setDateTime",
    "cancelada": int,
    "sinInventario": int
}

def modFechaInvVentas(ventas_inventariadas):    # CHECKED
    ventas_inventariadas = mapper.many_to_db(ventas_inventariadas, db_map_venta)
    return _mod_fecha_inv_ventas(ventas_inventariadas)

def _mod_fecha_inv_ventas(ventas_inventariadas):
    print(f"updateInventarioVentas {ventas_inventariadas}")
    with db.connPorRol(True) as conn:
        res = _mod_fecha_inv(conn, ventas_inventariadas)
        if not res["success"]:
            raise res["error"]
    return db.returnBlank()

### hacer distincion entre productos de una venta, productos sueltos y productos sencillos

# def _mod_fecha_inv_venta(conn, prods):
#     prods = mapper.many_to_db(prods)
#     if not len({r.get("fechaVenta") for r in prods}) == 1:
#         raise Exception(f"Productos en una venta no tienen la misma fecha venta {prods}")
#     return _mod_fecha_inv(conn, prods)

# def _mod_fecha_inv_prods(conn, prods):
#     prods = mapper.many_to_db(prods)
#     for p in prods:
#         _mod_fecha_inv(conn, p)
#     return db.returnBlank()
    
# def _mod_fecha_inv_prod(conn, prod):
#     prod = mapper.one_to_db(prod)
#     return _mod_fecha_inv(conn, prod)

def _mod_fecha_inv(conn, prods):
    print(f"_mod_fecha_inv {prods}")
    if any(row.get("fechaVenta") is None or row.get("fechaInventario") is None for row in prods):
        raise Exception(f"Productos no tienen fecha venta o inventario {prods}")
    for p in prods:
        updStr = "update ventas set fechaInventario=:fechaInventario "
        updStr += "where dispositivoId=:dispositivoId and fechaVenta=:fechaVenta "
        updStr += "and productoId=:productoId and tipoVentaId=:tipoVentaId"
        res = db.run_sql(conn, updStr, [p])
        print(res)
        if not res["success"]:
            print(res["error"])
            raise res["error"]
    return db.returnBlank()

def setVenta(prods):        # CHECKED
    prods = mapper.many_to_db(prods, db_map_venta, setDateTime=True)
    #HERE
    res = _set_productos(prods)
    if res["success"]:
        total =0
        for p in prods:
            total += p["subtotal"]
        fechaVenta = prods[0]["fechaVenta"]
        res["fechaVenta"] = fechaVenta
        res["total"] = total
        return res
    return db.returnError(f"No se pudo registrar ventas {prods}")

def setProducto(prod):      # CHECKED 
    prod = mapper.one_to_db(prod, db_map_venta)
    return _set_productos(prod)

def _set_productos(prods):
    if config.soyRol(config.ESCLAVO_NAME):
        res =  db.returnError(f"No se pudo insertar la venta para {prods}")
        with db.conn_ctx(config.BASE_ESCALVO_NAME, True) as conn:
            res = _ins_productos(conn, prods)
        if res["success"]:
            with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
                pro._mod_inv_prods(conn, prods, marcaUltimaVenta=True)
            res["resultado"]=prods
        return res
    with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
        print("BEGIN TRANSACTION MAESTRO")
        conn.execute("BEGIN")
        res = _ins_productos(conn, prods)
        if res["success"]:
            #venta = res["resultado"]
            print(f"venta insertada : {prods}")
            inv_res = pro._mod_inv_prods(conn, prods, marcaUltimaVenta=True)
            if inv_res["success"] and config.soyRol(config.MAESTRO_NAME):
                res = _mod_fecha_inv(conn, prods)
                if res["success"]:
                    res["resultado"]=prods
                    return res
        raise f"No se pudo actualizar la fecha de inventario en la venta {res['error']}"

def _ins_productos(conn, prods):
    print(f"venta inicial : {prods}")
    insStr = f"insert into ventas ({', '.join(columnas_venta)}) values (:{', :'.join(columnas_venta)})"
    res = db.run_sql(conn, query=insStr, data=prods, returnCols=["fechaVenta"])
    # db_map =db_map_ventas, returnCols=["fechaVenta"]
    if res["success"]:
        # if "fechaVenta" in res:
        #     fv = res["fechaVenta"]
        #     for p in prods:
        #         p.update({"fechaVenta":fv})
        return res
    return db.returnError(f"No se pudo insertar la venta {prods}")

def selVentasSinInventario():       # CHECKED
    res = _sel_ventas("where fechaInventario is null")
    if res["success"]: return res
    else: raise Exception(res["error"])

def _sel_ventas(condiciones, condDict=None):
	sqlStr =  "select * from ventas"
	if (condiciones and len(condiciones.strip())>0):
		sqlStr+=" "+condiciones
	with db.connPorRol() as conn:
		res = db.run_sql(conn, sqlStr, data=condDict, fetchRows=True)
		print(res)
		return res

def del_ventas_viejas_slave():
    print("del_ventas_viejas_slave")
    with db.conn_ctx(config.BASE_ESCALVO_NAME, True) as conn:
        res = db.run_sql(conn, "delete from ventas WHERE fechaVenta < datetime('now', '-1 month') and fechaInventario is not null")
        return res
    return db.returnError()

# def _sel_ventas_maestro(condiciones, condDict=None):
# 	sqlStr =  "select * from ventas"
# 	if (condiciones and len(condiciones.strip())>0):
# 		sqlStr+=" "+condiciones
# 	with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
# 		res = db.run_sql(conn, sqlStr, data=condDict, fetchRows=True)
# 		print(res)
# 		return res
	
def setVentasEsclavos(ventas, dispositivoId):       # CHECKED
    ventas = mapper.many_to_db(ventas, db_map_venta)
    if any(row.get("fechaVenta") is None for row in ventas):
        raise Exception(f"Productos no tienen fecha venta {ventas}")
    if any(row.get("fechaInventario") is not None for row in ventas):
        raise Exception(f"Productos ya tienen fecha inventario {ventas}")
    with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
        conn.execute("BEGIN")
        sqlStr = "delete from ventas_esclavos where dispositivoId=:dispositivoId"
        res = db.run_sql(conn, query=sqlStr, data=[{"dispositivoId": dispositivoId}])
        if res["success"] and ventas!=None and len(ventas)>0:
            sqlStr = f"insert into ventas_esclavos ({', '.join(columnas_venta)}) values (:{', :'.join(columnas_venta)})"
            res = db.run_sql(conn, query=sqlStr, data=ventas)
            # db_map=db_map_venta
            if res["success"]:
                return res
        else:
             return db.returnBlank()
        raise res["error"]
             
select_map_ventas_pend = {
    "fechaVenta": lambda x: x,
    "productoId": int,
    "tipoVentaId": int,
    "precio": lambda x: float(x) if x  else None,
    "precioVenta": lambda x: float(x) if x  else None,
    "cantidad": lambda x: float(x) if x  else None,
    "subtotal": lambda x: float(x) if x  else None,
    "numeroUnidades": lambda x: float(x) if x  else None,
    "numeroKgs": lambda x: float(x) if x  else None,
    "cantidadUnidades": lambda x: float(x) if x  else None,
    "cantidadPaquetes": lambda x: float(x) if x  else None,
    "cantidadKgs": lambda x: float(x) if x  else None,
    "fechaInventario": lambda x: x,
    "cantidadUnidadesAccum": lambda x: float(x) if x  else None,
    "cantidadPaquetesAccum": lambda x: float(x) if x  else None,
    "cantidadKgsAccum": lambda x: float(x) if x  else None,
    "existenciaUnidades": lambda x: float(x) if x  else None,
    "existenciaPaquetes": lambda x: float(x) if x  else None,
    "existenciaKgs": lambda x: float(x) if x  else None,
    "existenciaNuevaUnidades": lambda x: float(x) if x  else None,
    "existenciaNuevaPaquetes": lambda x: float(x) if x  else None,
    "existenciaNuevaKgs": lambda x: float(x) if x  else None,
    "minimoUnidades": lambda x: float(x) if x  else None,
	"minimoPaquetes": lambda x: float(x) if x  else None,
	"minimoKgs": lambda x: float(x) if x  else None,
    "cancelada": bool,
    "sinInventario": bool
}

def selVentasEsclavosPendientes(dispositivoId=None, sinInventario=True):        # CHECKED
    if config.soyRol(config.MAESTRO_NAME):
        print("selVentasEsclavosPendientes", dispositivoId, sinInventario)
        sqlStr = db.get_sql_file("sel_ven_pen")
        data = None
        if dispositivoId!=None:
            sqlStr = sqlStr.replace(r"{and_where}", r"and a.dispositivoId = :dispositivoId {and_where}")
            data=[{"dispositivoId" : dispositivoId}]
        if sinInventario:
            sqlStr = sqlStr.replace(r"{and_where}", r"and c.fechaInventario is null")
        else:
            sqlStr = sqlStr.replace(r"{and_where}", "")
        with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
            res = db.run_sql(conn, sqlStr, data=data, fetchRows=True)
            # select_map=select_map_ventas_pend
            if res["success"]:
                return res
            else: return res["error"]
    return db.returnError("Dispositivo no es maestro")

def selVentasInventariadas(ventas_pendientes):    # CHECKED ventas ya inventariadas en base maestro del esclavo
    ventas_pendientes = mapper.many_to_db(ventas_pendientes)
    sqlStr = "select * from ventas where dispositivoId = :dispositivoId "
    sqlStr += "and fechaInventario is not null and "
    sqlStr += "fechaVenta in (:fechaVenta)"
    newSqlStr, newObject, newExecMap = mapper.genMultiParamStrMap(sqlStr, ventas_pendientes, db_map={"fechaVenta" : lambda x: x})
    if len(newObject)==1:
        newObject[0]["dispositivoId"] = config.DEVICE["MS_SOY"]["dispositivoId"]
    else:
        raise Exception("No se genero query para ventas pendientes ya inventariadas en maestro")
    with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
        res = db.run_sql(conn, newSqlStr, data=newObject, fetchRows=True)
          # db_map=newExecMap, select_map={}
        if res["success"]:
            return res
    raise f"No se obtuvo de inventario ventas inventariadas {ventas_pendientes}"

def delVentasPendientes(dispositivoId=None):    # CHECKED
    print(f"del_ventas_pendientes {dispositivoId}")
    if config.soyRol(config.MAESTRO_NAME):
        sqlStr = "delete from ventas_esclavos where dispositivoId=:dispositivoId"
        if dispositivoId!=None:
            with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
                res = db.run_sql(conn, sqlStr, data=[{"dispositivoId" : dispositivoId}])
                if res["success"]:
                    return res
                else: return res["error"]
        else:
             return db.returnError("Dispositivo no indicado para borrar pendientes")
    return db.returnError("Dispositivo no es maestro")

sel_res_ventas_map = {
    "anio" : int,
    "mes": int,
    "dia": int,
    "subtotal": float
}

def selResumenVentas(anio):     # CHECKED
    if config.soyRol(config.MAESTRO_NAME):
        print(anio)
        sqlStr = "select CAST(strftime('%Y', fechaVenta) AS INTEGER) as anio, CAST(strftime('%m', fechaVenta) AS INTEGER) as mes, " \
        "CAST(strftime('%d',fechaVenta) AS INTEGER) as dia, date(fechaVenta) as fecha, sum(iif(cancelada, 0, subtotal)) as subtotal from ventas " \
	    "where CAST(strftime('%Y', fechaVenta) AS INTEGER)=:anio group by 1,2,3,4 order by 4"
        with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
            res = db.run_sql(conn, sqlStr, data=[{"anio": anio}], fetchRows=True)
            # select_map=sel_res_ventas_map
            if res["success"]:
                return res
            else: return res["error"]
    return db.returnError("Dispositivo no es maestro")

def selVentasDia(anio, mes, dia):       # CHECKED
    if config.soyRol(config.MAESTRO_NAME):
        sqlStr = "select a.*, case a.tipoVentaId when -4 then a.extraInfo else coalesce(b.descripcion,'') end as descripcion, " \
        "case a.tipoVentaId when -5 then a.extraInfo else coalesce(b.codigoBarras,'') end as codigoBarras, " \
        "coalesce(b.codigoNumerico,'') as codigoNumerico, coalesce(b.claves,'') as claves, " \
        "case a.tipoVentaId when -4 then 'comun' when -5 then 'sin inventario' else coalesce(b.unidadInv,'') end as unidadInv " \
        "from ventas a left join productos b on a.productoId =b.productoId " \
        "where CAST(strftime('%Y', a.fechaVenta) AS INTEGER)=:anio and " \
        "CAST(strftime('%m', a.fechaVenta) AS INTEGER)=:mes and CAST(strftime('%d', a.fechaVenta) AS INTEGER)=:dia "\
        "order by a.fechaVenta desc, a.rowid desc"
        with db.conn_ctx(config.BASE_MAESTRO_NAME) as conn:
            res = db.run_sql(conn, sqlStr, data=[{"anio": anio, "mes": mes, "dia":dia}], fetchRows=True)
            #select_map=select_map_ventas
            if res["success"]:
                print(res["resultado"])
                return res
            else: return res["error"]
    elif config.soyRol(config.ESCLAVO_NAME):
        sqlStr = "select a.*, case a.tipoVentaId when -4 then a.extraInfo end as descripcion, " \
        "case a.tipoVentaId when -5 then a.extraInfo end as codigoBarras, " \
        "case when a.tipoVentaId<-3 then '' end as codigoNumerico, " \
        "case when a.tipoVentaId<-3 then '' end as claves, " \
        "case a.tipoVentaId when -4 then 'comun' when -5 then 'sin inventario' end as unidadInv " \
        "from ventas a " \
        "where CAST(strftime('%Y', a.fechaVenta) AS INTEGER)=:anio and " \
        "CAST(strftime('%m', a.fechaVenta) AS INTEGER)=:mes and CAST(strftime('%d', a.fechaVenta) AS INTEGER)=:dia " \
        "order by a.fechaVenta desc, a.rowid desc"
        with db.conn_ctx(config.BASE_ESCALVO_NAME) as conn:
            res = db.run_sql(conn, sqlStr, data=[{"anio": anio, "mes": mes, "dia":dia}], fetchRows=True)
            # select_map=select_map_ventas
            if res["success"]:
                productosId=[]
                for v in res["resultado"]:
                     if v["tipoVentaId"]>-4:
                        val = {"productoId": v["productoId"]}
                        if val not in productosId:
                            productosId.append(val)
                if len(productosId)>0:
                    res2 = pro.selProductoIds(list(productosId))
                    if res2["success"]:
                        # Build index from listB
                        indexProd= {prod["productoId"]: prod for prod in res2["resultado"]}
                        # Extend items in listA
                        resultado = res["resultado"]
                        for v in resultado:
                            extra = indexProd.get(v["productoId"])
                            if extra:
                                v.update(extra)
                        res["resultado"]=resultado
                return res
            else: return res["error"]
    return db.returnError("Dispositivo no es maestro")

def selSemanaVentas(anio, mes, dia):    # CHECKED
    sqlStr = "select CAST(strftime('%Y', fechaVenta) AS INTEGER) as anio, CAST(strftime('%m', fechaVenta) AS INTEGER) as mes, " \
	    "CAST(strftime('%d',fechaVenta) AS INTEGER) as dia, date(fechaVenta) as fecha, sum(iif(cancelada, 0, subtotal)) as subtotal from ventas " \
	    "where fechaVenta > date(:anio||'-'||PRINTF('%02d', :mes)||'-'||PRINTF('%02d', :dia), '-7 days') " \
	    "group by 1,2,3,4 order by 4 desc"
    with db.connPorRol() as conn:
        res = db.run_sql(conn, sqlStr, data=[{"anio": anio, "mes": mes, "dia":dia}], fetchRows=True)
        # select_map=sel_res_ventas_map
        if res["success"]:
            return res
        else: raise res["error"]
    return db.returnError("Dispositivo no es maestro")

def _mod_activo_producto(conn, prod):
    print(f"activarProducto : {prod}")
    sqlStr = f"update ventas set cancelada=:cancelada where dispositivoId=:dispositivoId and "\
    "productoId=:productoId and tipoVentaId=:tipoVentaId and fechaVenta=:fechaVenta"
    res = db.run_sql(conn, query=sqlStr, data=[prod] )
    # db_map=db_map_ventas
    if res["success"]:
        return res
    else: raise res["error"]

def setActivoVenProds(prods):      # CHECKED
    prods = mapper.many_to_db(prods, db_map_venta)
    for prod in prods:
        res = _set_activo_producto(prod)
        if not res["success"]:
            raise f"No se pudo activar venta {prod}"
    res = db.returnBlank()
    #res["resultado"]=prods
    return res

def _set_activo_producto(prod):
    if config.soyRol(config.ESCLAVO_NAME):
        res = db.returnError(f"No se pudo activar venta {prod}")
        with db.conn_ctx(config.BASE_ESCALVO_NAME, True) as conn:
            res = _mod_activo_producto(conn, prod)
        if res["success"]:
            with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
                pro._mod_inv_prod(conn, prod=prod)
        return res
    with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
        print("BEGIN TRANSACTION MAESTRO")
        conn.execute("BEGIN")
        res = _mod_activo_producto(conn, prod)
        if res["success"]:
            #venta = db.apply_db_map(venta, db_map_ventas)
            #print(venta)
            inv_res = pro._mod_inv_prod(conn, prod=prod)
            if not inv_res["success"]:
                raise f"No se actualizo inventario al activar {prod} - {res['error']}"
        res = db.returnBlank()
        #res["resultado"]=db.apply_db_map(prods if isinstance(prods, (list, tuple)) else [prods], db_map_venta)
        return res

def _set_fecha_venta_producto(prod, fechaFinal):
    print(f"_set_fecha_venta_producto : {prod}, {fechaFinal}")
    sqlStr = f"update ventas set fechaVenta=:fechaFinal where dispositivoId=:dispositivoId and "\
    "productoId=:productoId and tipoVentaId=:tipoVentaId and fechaVenta=:fechaVenta"
    with db.conn_ctx(config.BASE_MAESTRO_NAME, True) as conn:
        prod = mapper.add_fields([prod], {"fechaFinal":fechaFinal})
        res = db.run_sql(conn, query=sqlStr, data=prod )
        if res["success"]:
            return res
        else: raise Exception(res["error"])

def setFechaVentaVenProds(prods, nuevaFecha):      # CHECKED
    if config.soyRol(config.MAESTRO_NAME):
        prods = mapper.many_to_db(prods, db_map_venta)
        if any(row.get("fechaVenta") is None for row in prods):
            raise Exception(f"Productos no tienen fecha venta {prods}")
        print(nuevaFecha)
        print(prods)
        for prod in prods:
            dt_original = datetime.fromisoformat(prod["fechaVenta"])
            dt_nueva = datetime.fromisoformat(nuevaFecha)
            dt_final = dt_original.replace(
                year=dt_nueva.year,
                month=dt_nueva.month,
                day=dt_nueva.day
            )
            res = _set_fecha_venta_producto(prod, dt_final)
            if not res["success"]:
                raise f"No se pudo cambiar fecha de venta {prod}"
        return db.returnBlank()
        #res["resultado"]=prods
    return db.returnError("No soy maestro")