import sys, json, time, random, os
from config import PROCESS_JOBS_PATH, TRUPER_IMAGENES_PATH
from datetime import datetime

final_progress = 1

def set_final_progress(total):
    global final_progress
    if total and total > 0:
        final_progress = int(total)


def printProgress(prog):
    print(f"PROGRESS:{prog}", flush=True)

def log(msg):
    print(f"LOG:{msg}", flush=True)

def progress(p):
    percent = int((p / final_progress) * 100)
    if percent > 100:
        percent = 100
    printProgress(percent)

def result(data):
    #print(f"RESULT:{json.dumps(data)}", flush=True)
    print(f"RESULT:{json.dumps(data, default=_json_default)}", flush=True)
    printProgress(100)

def _json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def merge_simpledf(source_df, target_df, key, columns=None):
        merge_cols = set(columns)
        merge_cols.discard(key)
        target_index = target_df.index_by(key)
        for src_row in source_df.rows:
            src_key = src_row.get(key)
            if src_key is None:
                continue
            if src_key in target_index:
                tgt_row = target_index[src_key]
                for col in merge_cols:
                    src_val = src_row.get(col)
                    tgt_val = tgt_row.get(col)
                    if src_val != tgt_val:
                        tgt_row[col] = src_val
            else:
                # Insert new row — project to target schema
                new_row = {}
                for col in target_df.columns:
                    if col == key:
                        new_row[col] = src_key
                    else:
                        new_row[col] = src_row.get(col)
                target_df.add_row(new_row)

def codigoPrograma(temp_files):
    # Importar librerias
    # pip3 install Pillow
    # Procesa nuevo inventario usando inventario de PV y Catalogo Truper
    import json
    import pandas as pd
    import re
    from difflib import SequenceMatcher
    from procesos.jobs.pandasReader import SimpleDF
    from unidecode import unidecode
    import json
    import re, math
    from fractions import Fraction

    process_log_path = os.path.join(PROCESS_JOBS_PATH, "procesaInventario")

    res = []
    colsArchivo = ["codigo", "descripcion", "precioCosto", "precioVenta", "precioMayoreo", "inventario", "invMinimo", "departamento"]
    
    try:
        NUEVO_INVENTARIO = "inventario_procesado.txt"
        #CATALOGO_TRUPER = "../Truper/catalogo_truper.json"
        #INVENTARIO_PV = "inventario.txt"
        #NUEVO_INVENTARIO = "inventario_procesado.txt"

        # INVENTARIO_PV = "inventario_ajustes.txt"
        # NUEVO_INVENTARIO = "inventario_procesado_ajustes.txt"

        # cat_truper_json = ""
        # with open(CATALOGO_TRUPER, "r") as f:
        #     content = f.read()
        #     cat_truper_json = content[:]
        # cat_truper_json = cat_truper_json.replace("cat_inv =","")
        # #print(cat_truper_json[:100])
        # cat_truper_json = json.loads(cat_truper_json)
        
        catTruper = temp_files["truperExistente"]
        dfTruper = SimpleDF.read_tsv(catTruper)
        dfTruper.normalizeColumns()
        dfTruper.clean_all_spaces()

        inventario = temp_files["inventarioNuevo"]
        df_inv= SimpleDF.read_tsv(inventario)
        df_inv.normalizeColumns()
        df_inv.clean_all_spaces()

        if set(colsArchivo)!=set(df_inv.columns):
            raise Exception(f"Archivo {df_inv.columns} no contiene columnas esperadas {colsArchivo}")

        # lineterminator="\n",
        #df_inv = pd.read_csv(INVENTARIO_PV, sep='\t', dtype = str, keep_default_na=False, encoding="utf-16", na_filter=False)

        df_inv.rename_columns({'codigo': 'codigoBarras', 
                            'precioCosto': 'costo', 
                            'precioVenta': 'precio', 
                            'precioMayoreo':'mayoreo',
                            'invMinimo':'minimo'
                            })
        
        columnasNuevas = ["codigoNumerico", "codigoNumericoNuevo", "codigosBuscar", "codigosBuscarNuevo", "codigoBarrasNuevo", "comentario", "huboCambio", "descripcionTruper", 
        "descripcionTruperInv", "costoPaqueteTruper", "costoUnidadTruper", "costoKgTruper", "sugeridoPaqueteTruper", "sugeridoUnidadTruper", "sugeridoKgTruper","pesoKg", 
        "numeroUnidades", "unidad", "unidadInv", "numeroKgs", "costoUnidadComparacion", "costoPaqueteComparacion", "costoComparacion", 
        "precioUnidadComparacion", "precioPaqueteComparacion", "precioComparacion", "precioEs", "costoEs", "diffDescripcionInv", 
        "descripcionLimpia", "proveedor"]

        for col in columnasNuevas:
            df_inv.ensure_column(col, "")

        def obtenDescLimpia(desc, codigosBuscar):
            descLimpia = desc[:]
            if codigosBuscar:
                for c in codigosBuscar:
                    if not c.isdigit():
                        match_c= re.search(r"\d{5,}", c)
                        if match_c:
                            c=match_c.group(0)
                    descLimpia = descLimpia.replace(c,"").replace("()","").strip()
                    #p = rf"[^\w\s]?{c}[^\w\s]?"
                    #match = re.search(p, descLimpia)
                    #if (match):
                        #descLimpia = descLimpia.replace(match.group(0),"").strip()
                    descLimpia = descLimpia.strip(".,- ")
            return descLimpia

        # difference between two strings
        def similarity_percentage(a, b):
            ratio = SequenceMatcher(None, a.lower(), b.lower()).ratio()
            return int(ratio * 100)   # convert to percentage

        def comparaGuardaValores(ele, i, listaComparacion, listaColsResultado, label):

            comp1=""
            if listaComparacion[1]!="":
                comp1 = round(listaComparacion[0]-float(listaComparacion[1]),3)
                ele[listaColsResultado[0]]=comp1

            comp2=""
            if listaComparacion[2]!="":
                comp2 = round(listaComparacion[0]-float(listaComparacion[2]),3)
                ele[listaColsResultado[1]]=comp2
            
            if comp1!="" and comp2!="":
                if abs(comp1)<abs(comp2):
                    ele[listaColsResultado[2]]=comp1
                    ele[f"{label}Es"] = "unidad"
                else:
                    ele[listaColsResultado[2]]=comp2
                    ele[f"{label}Es"] = "paquete"
            elif comp1=="":
                ele[listaColsResultado[2]]=comp2
                ele[f"{label}Es"] = "paquete"
            elif comp2=="":
                ele[listaColsResultado[2]]=comp1
                ele[f"{label}Es"] = "unidad"
            else:
                ele[listaColsResultado[2]]=""
                ele[listaColsResultado[1]]=""
                ele[f"{label}EsUnidad"] = ""
                ele[f"{label}EsPaquete"] = ""

        def extraeCostoPrecio(ele, i, prod_truper, costoInv, precioInv):
            descripcionTruper = prod_truper[0]["descripcion"].strip()
            descripcionTruperInv = prod_truper[0]["descripcionInv"].strip()
            descripcion = ele["descripcion"]

            ele["diffDescripcionInv"]=similarity_percentage(descripcion, descripcionTruperInv)
            
            unidad = prod_truper[0]["unidad"].strip()
            unidad_inv = prod_truper[0]["unidadInv"].strip()
            numero = prod_truper[0]["numeroUnidades"].strip()
            pesoKg = prod_truper[0]["pesoKg"].strip()
            costoUnidadTruper = prod_truper[0]["costoUnidad"]
            costoPaqueteTruper = prod_truper[0]["costoPaquete"]
            costoKgTruper = prod_truper[0]["costoKg"]
            sugeridoPaqueteTruper=prod_truper[0]["sugeridoPaquete"]
            sugeridoUnidadTruper=prod_truper[0]["sugeridoUnidad"]
            sugeridoKgTruper=prod_truper[0]["sugeridoKg"]
            numeroKgs = prod_truper[0]["numeroKgs"]
            
            ele["descripcionTruper"]=descripcionTruper
            ele["descripcionTruperInv"]=descripcionTruperInv
            ele["unidad"]=unidad
            ele["unidadInv"]=unidad_inv
            ele["numeroUnidades"]=numero
            ele["pesoKg"]=pesoKg
            ele["costoUnidadTruper"]=costoUnidadTruper
            ele["costoPaqueteTruper"]=costoPaqueteTruper
            ele["costoKgTruper"]=costoKgTruper
            ele["sugeridoPaqueteTruper"]=sugeridoPaqueteTruper
            ele["sugeridoUnidadTruper"]=sugeridoUnidadTruper
            ele["sugeridoKgTruper"]=sugeridoKgTruper

            if numeroKgs and float(numeroKgs)>0.1:
                ele["numeroKgs"]=numeroKgs

            comparaGuardaValores(ele, i, [costoInv, costoUnidadTruper, costoPaqueteTruper], 
                            ["costoUnidadComparacion","costoPaqueteComparacion", "costoComparacion"], "costo")
            comparaGuardaValores(ele, i, [precioInv, sugeridoUnidadTruper, sugeridoPaqueteTruper], 
                ["precioUnidadComparacion","precioPaqueteComparacion", "precioComparacion"], "precio")
            
        def quitaParteFinal(descripcion):
            descripcionResiduo = re.findall(r',\s*[A-Z][a-zA-z\s]+$', descripcion)
            if len(descripcionResiduo)>0:
                descripcionResiduo=descripcionResiduo[0]
                descripcion=descripcion.replace(descripcionResiduo,"")
            return descripcion


        def limpiaFracciones(descripcion):
            patterns = [
            [ rf"(\d)\s*(['\"])?\s*(?:[xX]|[Pp][Oo][Rr])\s*(\d)", r"\1\2x\3"]  # Sustituye X o POR por x
            ,[ rf"(\d)\s*(?:[Pp]ul|[Pp]ulgada[s]?)(\W|$)", r"\1'\2"]   # Quita palabras Pulgadas o Pul si hay un numero antes
            ,[ rf"((?:[^\/\w]|x)\d?\d)\s+(\d\d?\/)", r"\1-\2"] # Une u numero de 2 cifras con una fraccion 12 3/4: 12-3/4
            ,[ rf"(\d+)\s+((?:[MmCc]?[Mm]|[Kk][Gg]|[Ll][Tt]?|[Ll]itro[s]?))", r"\1\2" ] # Une un numero con su unidad: 1 m: 1m
            ]
            desc = descripcion[:]
            #print(desc)
            for p in patterns:
                desc = re.sub(p[0], p[1], desc)
                #print(f"\t{desc}")
            return desc.strip(" ,.-")
        
        set_final_progress(len(df_inv))

        for i in range(0, len(df_inv)): #range(0,df_inv.tail(1).index.item()+1): 
            ele = df_inv[i]
            descripcion = ele["descripcion"]
            #codigos_buscar = set(re.findall(r'([^-\s]*\d{5,}[^-\s]*|(?:ART\d{1,}(?:-\d{1,})?))', descripcion))
            codigos_buscar = set(re.findall(r'((?:ART\d{1,}(?:-\d{1,})?))', descripcion))
            codigo_numerico = set(re.findall(r'([^-\s]*\d{4,}[^-\s]*)', descripcion))
            codigos_encontrados = set(codigos_buscar)
            for c in set(codigo_numerico):
                if c.isdigit():
                    codigos_encontrados.add(c)
                else:
                    codigo_numerico.discard(c)
            if codigos_encontrados:
                codigos_encontrados = sorted(list(codigos_encontrados))
            descLimpia =  obtenDescLimpia(descripcion, codigos_encontrados)
            descLimpia = limpiaFracciones(descLimpia)
            ele["descripcionLimpia"] = quitaParteFinal(descLimpia)
            codigoBarras = ele["codigoBarras"].strip()
            ele["codigoBarras"] = codigoBarras
            ele["codigoBarrasNuevo"]= codigoBarras
            ele["codigosBuscar"] = ",".join(codigos_buscar)
            ele["codigosBuscarNuevo"] = ",".join(codigos_buscar)
            ele["codigoNumerico"] = ",".join(codigo_numerico)
            val_orig = (codigoBarras, codigo_numerico)
            #print(codigoBarras)
            #print(codigos_encontrados)
            buscarPorCodigos = True
            codigosBuscarResultado = set()
            codigoNumericoResultado = set()
            if (codigoBarras!="" and codigoBarras.isdigit()):
                prod_truper_barras = list(filter(lambda x: x["codigoBarras"].strip() == codigoBarras.strip(), dfTruper.rows))
                if len(prod_truper_barras)>0:
                    buscarPorCodigos=False
                    ele["proveedor"]="Truper"
                    costoInv = float(ele["costo"].replace("$","").replace(",",""))
                    precioInv = float(ele["precio"].replace("$","").replace(",",""))
                    extraeCostoPrecio(ele, i, prod_truper_barras, costoInv, precioInv)

                    if prod_truper_barras[0]["codigo"] in codigo_numerico:
                        codigoNumericoResultado.update(codigo_numerico)
                    else:
                        codigoNumericoResultado.add(prod_truper_barras[0]["codigo"])
                        for cod in codigos_buscar:
                            if cod.lower().startswith("art"):
                                codigosBuscarResultado.add(cod)
            codigos_a_buscar = []
            if (len(codigo_numerico)>0 and buscarPorCodigos):
                codigos_a_buscar = codigo_numerico
            elif len(codigo_numerico)==0 and buscarPorCodigos and codigoBarras.isdigit() and len(codigoBarras)<=6:
                codigos_a_buscar = [codigoBarras]
            if len(codigos_a_buscar)>0:
                for cod in codigos_a_buscar:
                    if cod.isdigit():
                        prod_truper_codigo = list(filter(lambda x: x["codigo"].strip() in codigos_a_buscar, dfTruper.rows))
                        if len(prod_truper_codigo)>0:
                            ele["proveedor"]="Truper"
                            # COMPARAR COSTO COMO EN EL BLOQ UE ANTERIOR
                            costoInv = float(ele["costo"].replace("$","").replace(",",""))
                            precioInv = float(ele["precio"].replace("$","").replace(",",""))
                            extraeCostoPrecio(ele, i, prod_truper_codigo, costoInv, precioInv)

                            if prod_truper_codigo[0]["codigoBarras"] != codigoBarras:
                                if prod_truper_codigo[0]["codigoBarras"] not in ["False","nan"]:
                                    #print("Cambiando codigo de barras: ",ele["CodigoBarras"],prod_truper_codigo[0]["codigo_barras"])
                                    ele["codigoBarrasNuevo"]=prod_truper_codigo[0]["codigoBarras"]
                                    ele["comentario"]="Cambio codigo de barras"
                                else:
                                    ele["comentario"]="Codigo barras no esta en Truper"
                    codigoNumericoResultado.add(cod)
            # QUITAR CODIGOS BUSCAR RESUTADO, COMPRARAR CON CODIGOS BUSCAR 
            ele["codigoNumericoNuevo"] = ",".join(sorted(codigoNumericoResultado))
            val_new = (ele["codigoBarrasNuevo"], sorted(codigoNumericoResultado))

            if val_orig==val_new:
                #print(val_new, " "*22, df_inv.iloc[i]["DescripcionNueva"], "\n")
                pass
            else:
                ele["huboCambio"]="Cambio"
                #print (val_orig , " "*8, i, " "*8, descripcion)
                #print(val_new, "****", " "*25, df_inv.iloc[i]["DescripcionTruperInv"], "\n")
            progress(i)
        df_inv.save(NUEVO_INVENTARIO)


        res = df_inv.rows

    except Exception as e:
        print(e)
        raise e
    
    return res
# TERMINA CODIGO DEL PROGRAMA **********************

# def main():
#     log("Proceso comenzo")
#     file_name = os.path.basename(__file__)
#     params = json.loads(sys.argv[1])
#     log(f"Starting file {file_name} with {params}")

#     # parametros 
#     archivo = params.get("archivo")
#     procesaBarras = params.get("procesaBarras")
#     procesaImagenes = params.get("procesaImagenes")

#     codigoPrograma(archivo, procesaImagenes,procesaBarras)
#     # /********* CODIGO DEL PROGRAMA *************/ 

#     rows = []
#     result(rows)


# TERMINA CODIGO DEL PROGRAMA **********************

def main():
    log("Proceso comenzo")
    file_name = os.path.basename(__file__)
    params = json.loads(sys.argv[1])
    log(f"Starting file {file_name} with {params}")

    # parametros 
    temp_files = params.get("temp_files")
    log(f"params {params}")

    res = []
    res = codigoPrograma(temp_files)
    # /********* CODIGO DEL PROGRAMA *************/ 
    print(res)
    result(res) 

if __name__ == "__main__":
    main()