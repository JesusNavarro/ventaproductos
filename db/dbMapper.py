# dbMapper.py
import datetime

_DB_CONVERTED = "__db_converted__"
_DB_CONVERTED_BY = "__db_converted_by__"

def _normalize_rows(data):
    res= []
    if data is not None:
        if isinstance(data, (list, tuple)):
            res= list(data)
        else: 
            res=[data]
    if len(res)==0:
        raise Exception(f"data a normalizar esta vacio {data}")
    else:
        return res

def _dict_to_db(row: dict, db_map: dict, execDateTime=None):
    out = {}
    for key, value in row.items():
        if key.startswith("__"):
            continue

        if value is None:
            out[key] = None
        elif key in db_map and db_map[key] != "setDateTime":
            out[key] = db_map[key](value)
        else:
            out[key] = value

    if execDateTime is not None:
        for key, rule in db_map.items():
            if rule == "setDateTime" and row.get(key) is None:
                out[key] = execDateTime
    return out

def one_to_db(data, db_map=None, setDateTime=False):
    row = _normalize_rows(data)
    if len(row)!=1:
        raise Exception(f"No es un solo registro {data}")
    if db_map is None:
        return row
    return many_to_db(row, db_map, setDateTime)

def many_to_db(data, db_map=None, setDateTime=False):
    rows = _normalize_rows(data)
    if db_map is None:
        return rows
    out = []
    signature = id(db_map)
    execDateTime = None
    if (setDateTime):
        execDateTime = datetime.datetime.now().replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S.%f")
    for row in rows:
        if isinstance(row, dict) and row.get(_DB_CONVERTED_BY) == signature:
            out.append(row)
            continue
        converted = dict(_dict_to_db(row, db_map, execDateTime))
        converted[_DB_CONVERTED] = True
        converted[_DB_CONVERTED_BY] = signature
        out.append(converted)
    return out

def _dict_from_db(row: dict, select_map=None):
    out = {}
    for key in row.keys():
        val = row[key]
        if key in select_map:
            out[key] = select_map[key](val)
        else:
            out[key] = val
    return out

def db_to_one(row: list, select_map=None):
    if len(row>1):
        raise Exception(f"No es solo un registro desde la BD {row}")
    if select_map is None:
        return row
    return [_dict_from_db(r, select_map) for r in row]

def db_to_many(rows: list, select_map=None):
    if select_map is None:
        return rows
    return [_dict_from_db(r, select_map) for r in rows]

def add_fields(dicts, props):
    if not isinstance(dicts, (list)):
        raise Exception(f"No es una lista normalizada {dicts}")
    for d in dicts:
        d.update(props)
        # for k, v in props.items():
        #     d[k]= v
    return dicts

def genMultiParamStrMap(sqlStr, objList, db_map):
    if not isinstance(objList, (list)) or db_map is None or len(db_map)!=1:
         return None, None, None
    resList = []
    resDBMap = {}
    resStr = sqlStr[:]
    colName = list(db_map.keys())[0]
    resObjects = {}
    converter = db_map[colName]
    for i in range(len(objList)):
        obj = objList[i]
        val = obj[colName]
        newParamName = colName+str(i)
        resList.append(newParamName)
        resDBMap[newParamName]=converter
        resObjects[newParamName] = val
    resStr = resStr.replace(f":{colName}", f":{', :'.join(resList)}")
    return resStr, [resObjects], resDBMap

# ***** MAPPINGS ******

# PROVEEDORES *****

