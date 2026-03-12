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

def codigoPrograma(temp_files, procesaImagenes=False, procesaBarras=True):
    # Importar librerias
    # pip3 install Pillow
    from PIL import Image
    import os
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    import time
    from io import BytesIO
    # pip3 install pandas
    import csv
    from procesos.jobs.pandasReader import SimpleDF
    from unidecode import unidecode
    import json
    import re, math
    from fractions import Fraction

    # pd.set_option("display.max_colwidth", None)
    # pd.set_option("display.max_rows", 200)   # or any number you want
    # pd.set_option("display.max_columns", None)

    process_log_path = os.path.join(PROCESS_JOBS_PATH, "procesaTruper")
    log_imagenes_no_encontradas= os.path.join(process_log_path, "imagenes_no_encontradas.txt")
    log_barras_no_encontradas= os.path.join(process_log_path, "barras_no_encontradas.txt")
    #archivo_Truper = os.path.join(process_log_path, "ListasPreciosPublica.txt")
    #catalogo_procesado = os.path.join(process_log_path, "catalogo_con_imagenes.tsv")


    # PANDAS SUBSTITUTION LOGIC 

    # def read_tsv(path, encoding="utf-16", sep="\t"):
    #     with open(path, newline="", encoding=encoding) as f:
    #         reader = csv.DictReader(f, delimiter=sep)
    #         rows = list(reader)
    #         columns = reader.fieldnames
    #     return SimpleDF(rows, columns)
    
    # def clean_all_spaces(df: SimpleDF):
    #     for row in df.rows:
    #         for k, v in row.items():
    #             if isinstance(v, str):
    #                 row[k] = re.sub(r"\s+", " ", v).strip()
    
    # def index_by(df: SimpleDF, key):
    #     return {row[key]: row for row in df.rows if row.get(key)}
    
    # def normalize_columns(columns):
    #     new_cols = []
    #     for c in columns:
    #         c = c.replace("[", " ").replace("]", " ")
    #         c = c.strip().replace(" ", "_").lower()
    #         c = unidecode(c)
    #         new_cols.append(c)
    #     return new_cols

    # Abrimos archivo de Truper que guardamops como CSV con extension TXT, actualizamos nombres de las columnas

    # def clean_all_spaces(df):
    #     for col in df.columns:
    #         if df[col].dtype == object:
    #             df[col] = df[col].map(lambda v: re.sub(r"\s+", " ", v) if isinstance(v, str) else v)
    #     return df

    # def insert_column_after(df, after_col, new_col_name, default_value=None):
    #     """Insert a new column with a default value after a given existing column."""
    #     if after_col not in df.columns:
    #         raise ValueError(f"Column '{after_col}' not found in DataFrame")
    #     # Determine the position to insert the new column
    #     pos = df.columns.get_loc(after_col) + 1
    #     # Insert new column
    #     df.insert(pos, new_col_name, default_value)
    #     return df

    res = []
    colsArchivo = ["codigo", "clave", "descripcion", "margenDeMercado", "caja", "master", "precio", "unidad", "ean", 
                   "precioMinimoDeVenta", "altaRotacion", "precioMayoreoConIva", "precioDistribuidorConIva", "precioPublicoConIva",
                     "precioMayoreoSinIva", "precioDistribuidorSinIva", "precioPublicoSinIva", "marca", "precioMedioMayoreoSinIva", 
                     "precioMedioMayoreoConIva", "codigoSat", "descripcionSat", "familia", "descripcionFamilia", "pesoKg", "volumenCm3"]
    
    colsArchivo =["codigo", "clave", "descripcion", "unidad", "precioDistribuidorConIva", "precioPublicoConIva", "descripcionFamilia", "pesoKg"]
    try:

        archivo_Truper = temp_files["truperNuevo"]
        catalogo_procesado = temp_files.get("truperExistente")
        truperKgUnidades = temp_files.get("truperKgUnidades")

        dfTruper = SimpleDF.read_tsv(archivo_Truper)
        dfTruper.normalizeColumns()
        dfTruper.clean_all_spaces()
        if not set(colsArchivo).issubset(set(dfTruper.columns)):
            msg = f"Archivo nuevo {dfTruper.columns} no tiene columnas esperadas {colsArchivo}"
            log(msg)
            raise Exception(msg)
        
        extra_cols = [
            "imgUrl", "codigoBarras", "unidadInv",
            "numeroKgs", "numeroUnidades", "descripcionInv",
            "costoUnidad", "costoPaquete", "costoKg",
            "sugeridoUnidad", "sugeridoPaquete", "sugeridoKg"
        ]
        for col in extra_cols:
            dfTruper.ensure_column(col)

        for col in ["createdDate", "modifiedDate"]:
            dfTruper.ensure_column(col, datetime.now())

        dfTruper.ensure_column("barrasVerificada", 0)
        dfTruper.ensure_column("imagenVerificada", 0)
        dfTruper.ensure_column("activo", 1)


        #dfTruper = pd.read_csv(archivo_Truper, encoding="utf-16", sep="\t", dtype=str, na_filter=False, keep_default_na=False)
        #cols = list(dfTruper.columns)
        # print(cols)
        #  pip3 install Unidecode
        # from unidecode import unidecode
        # new_cols = list(map(lambda x: x.replace("[", " " ), cols))
        # new_cols = list(map(lambda x: x.replace("]", " " ), new_cols))
        # new_cols = list(map(lambda x: x.strip(" " ), new_cols))
        # new_cols = list(map(lambda x: x.replace(" ", "_" ), new_cols))
        # new_cols = list(map(lambda x: x.strip(), new_cols))
        # new_cols = list(map(lambda x: x.lower(), new_cols))
        # new_cols = list(map(lambda x: unidecode(x), new_cols))
        #dfTruper = clean_all_spaces(dfTruper)
        #dfTruper.columns = new_cols



        # dfTruper["img_url"]=None
        # dfTruper["codigo_barras"]=None
        # #dfTruper['codigo_barras'] = dfTruper['codigo_barras'].astype(str)
        # dfTruper["updated"] = False  # reset marker
        # dfTruper["unidad_inv"]=None
        # dfTruper["contenido_kg"]=None
        # dfTruper["numero_unidades"]=None
        # dfTruper["descripcion_inv"]=None
        # dfTruper["costo_unidad"]=None
        # dfTruper["costo_paquete"]=None
        # dfTruper["sugerido_unidad"]=None
        # dfTruper["sugerido_paquete"]=None

        # extra_cols = [
        #     "img_url", "codigo_barras", "updated", "unidad_inv",
        #     "contenido_kg", "numero_unidades", "descripcion_inv",
        #     "costo_unidad", "costo_paquete",
        #     "sugerido_unidad", "sugerido_paquete"
        # ]

        if catalogo_procesado!= None and os.path.exists(catalogo_procesado):
            print("Ya existe y vamos a actualizar el archivo "+catalogo_procesado)
            # Si existe, abrimos el archivo que ya procesamos antes y lo actualizamos con los nuevos productos o nuevos datos que cambiaron
            #df = pd.read_csv(catalogo_procesado, encoding="utf-16", sep="\t", dtype = str, keep_default_na=False, na_filter=False)
            df = SimpleDF.read_tsv(catalogo_procesado)
            #df.save(catalogo_procesado.replace(".tsv", "_backup.tsv"))
            
            # df.normalizeColumns()
            # for col in extra_cols:
            #     df.ensure_column(col)
            # df.clean_all_spaces()

            #df= clean_all_spaces(df)
            
            #df.to_csv(catalogo_procesado.replace(".tsv", "_backup.tsv"), index=False, encoding="utf-16", sep="\t")
            #df.save(catalogo_procesado.replace(".tsv", "_backup.tsv"))
            #df = insert_column_after(df, "unidad_inv", "contenido_kg")

            # if not set(df.columns).issubset(set(dfTruper.columns)):
            #     print(f"Las columnas de los archivos {archivo_Truper} y {catalogo_procesado} no coinciden")
            #     print(f"{archivo_Truper}:", list(dfTruper.columns) )
            #     print(f"{catalogo_procesado}:", list(df.columns))
            #     raise Exception(f"Las columnas de los archivos {archivo_Truper} y {catalogo_procesado} no coinciden")
            # else:

                #df['codigo_barras'] = df['codigo_barras'].astype(str)
                # Columna para ver que renglones cambiaron
                #df["updated"] = False  # reset marker
                # Actualizamos df segun los cambios o nuevos productos que hay en dfTruper
                # --- Step 1: merge by codigo ---
                #df = df.merge(dfTruper, on="codigo", how="outer", suffixes=("", "_new"))
               
                # --- Step 2: update values with new ones when available ---
                # for col in new_cols:
                #     if col!="codigo":
                #         changed = df[col + "_new"].notna() & (df[col + "_new"] != df[col])
                #         df.loc[changed, "updated"] = True
                #         df[col] = df[col + "_new"].combine_first(df[col])

            old_index = df.index_by("codigo")
            colsArchivo.remove("codigo")
            merge_cols = set(colsArchivo) & set(df.columns)
            for new_row in dfTruper.rows:
                codigo = new_row["codigo"]
                if codigo in old_index:
                    old_row = old_index[codigo]
                    for col in merge_cols:
                        if col != "codigo" and new_row[col] and new_row[col] != old_row[col]:
                            old_row[col] = new_row[col]
                            old_row["modifiedDate"] = datetime.now()
                else: 
                    df.add_row(new_row)

                #merge_simpledf(dfTruper, df, "codigo", [""])

                # --- Step 3: drop helper columns explicitly ---
                # helper_cols = [col for col in df.columns if col.endswith("_new")]
                # df = df.drop(columns=helper_cols)
                # Guardamos el archivo actualizado
                #df.to_csv(catalogo_procesado, index=False, encoding='utf-8-sig', sep='\t')
                
                #df.to_csv(catalogo_procesado, index=False, encoding="utf-16", sep="\t")
                #   
            print("Archivo actualizado con datos nuevos de Truper")
        else:
            #dfTruper.to_csv(catalogo_procesado, index=False, encoding="utf-16", sep="\t")
            #df = pd.read_csv(catalogo_procesado, encoding="utf-16", sep="\t", dtype = str, keep_default_na=False, na_filter=False)
            #df= clean_all_spaces(df)
            #dfTruper.save(catalogo_procesado)
            #df = SimpleDF.read_tsv(catalogo_procesado)
            # for col in ["createdDate", "modifiedDate"]:
            #     dfTruper.add_column(col)
            df = dfTruper
            #df.clean_all_spaces()
            #del dfTruper
            print("Archivo guardado primera vez a procesar")

        ####### se modifico el archivo con los nuevos datos

        ####### logica para imagenes

        def ultimo_baja_imagen(codigo, clave, img_clave, download_image = True):
            url = "https://www.truper.com/BancoContenidoDigital/index.php?r=site%2Fsearch&Productos%5Bclave%5D="+str(codigo)
            # Create folder if it doesn't exist

            # if download_image:
            #     if not os.path.exists(folder):
            #         os.makedirs(folder)

            # Get HTML content
            #print("Intento 3 a - "+url)
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all images with the specified class
            #images = soup.find_all("img", class_=img_class)
            #images = soup.find_all("img", id="img1")

            div = soup.find("div", class_="card-img")

            images=[]
            if div:
                img = div.find("img")
                if img and img.get("src"):
                    #print("Image source:", img["src"])
                    images.append(img)
            
                else:
                    #print("No <img> tag or src found inside div.card-img")
                    pass
            else:
                #print("No div with class 'card-img' found")
                pass

            #print(f"Found {len(images)} images with class '{img_class}'")
            img_data=None
            img_url = ""
            for i, img in enumerate(images, start=1):
                # Get src attribute
                img_url = img.get("src")
                if not img_url:
                    #print("Intento 3 a - NO IMAGE URL")
                    continue

                # Handle relative URLs
                img_url = urljoin(url, img_url)

                if download_image:
                    # Download the image
                    #try:
                        #print("IMG URL", img_url)
                        r = requests.get(img_url)
                        #print("Intento 3: "+img_url)
                        if r.status_code == 404:
                            e_msg = f"*** Imagen no encontrada para {codigo} {clave} {img_clave} {img_url}"
                            print("\t", e_msg)
                            #raise Exception(e_msg)
                        img_data = r.content
                        
                        # Extract file extension
                        #ext = os.path.splitext(img_url)[1] or ".jpg"
                        #filename = os.path.join(folder, f"image_{code}{ext}")
            
                        #with open(filename, "wb") as f:
                        #    f.write(img_data)
            
                        #print(f"Downloaded: {filename}")
                    # except Exception as e:
                    #     print(f"Failed to download {img_url}: {e}")
                    #     raise e
            return img_url, img_data

        def dl_img(codigo, clave, img_clave, img_url):
            r = requests.get(img_url)
            if r.status_code == 404:
                e_msg = f"*** Imagen no encontrada para {codigo} {clave} {img_clave} {img_url}"
                print("\t", e_msg)
                raise Exception(e_msg)
            return r.content

        def resize_image_keep_aspect(input_path, max_height=500):
            ip_sep = input_path.split(".")
            output_path = ip_sep[0]+"_rs."+ip_sep[1]
            
            # Open the image
            img = Image.open(input_path)
            
            # Get current size
            width, height = img.size
            
            # Only resize if taller than max_height
            if height > max_height:
                # Compute new width keeping aspect ratio
                new_width = int((max_height / height) * width)
                    
                # Resize the image
                img = img.resize((new_width, max_height), Image.LANCZOS)
            
            # Save the image
            img.save(output_path)

        def download_image(codigo, clave, folder="imagenes_catalogo", download_image = False, max_height=500, print_ya_esta=False, segundo_link=False, tercer_link=False, i=0):
            img_clave = clave.strip().replace(" ", "-").replace("/", "-").replace("--", "-").replace("Ñ", "N")
            img_url=""
            img_nombre = f"truper_{codigo}"
            #image_path = os.path.join(f"image_{codigo}_{img_clave}")

            folder = r'../../static/imagenes/truper'
            folder = r'procesaTruper'
            folder = TRUPER_IMAGENES_PATH
            image_path = os.path.join(r"..",r"..", r"static", r"imagenes", r"truper")
            #print(os.path.exists(image_path))
            if any(os.path.splitext(f)[0] == img_nombre for f in os.listdir(folder)):
                if print_ya_esta:
                    print(codigo, "\tYa existia")
                img_url = "YA_EXISTIA"
            else:
                print("index", str(i), "-", codigo)
                image_downloaded = False
                try:
                    img_url = f"https://www.elferretero.com.mx/imageOriginal/{img_clave}.JPG"
                    img_data = dl_img(codigo, clave, img_clave, img_url)
                    image_downloaded = True
                except Exception as e:
                    #print("Fallo baja imagen intento 1")
                    pass
                if not image_downloaded and segundo_link:
                    time.sleep(2)
                    try:
                        img_url = f"https://www.truper.com/media/import/imagenes/{img_clave}.jpg"
                        img_data = dl_img(codigo, clave, img_clave, img_url)
                        image_downloaded = True
                    except Exception as e:
                        #print("Fallo baja imagen intento 2")
                        pass
                if not image_downloaded and tercer_link:
                    time.sleep(2)
                    try:
                        img_url, img_data = ultimo_baja_imagen(codigo, clave, img_clave, download_image=True)
                        if img_url!="" and img_data!=None:
                            image_downloaded = True
                    except Exception as e:
                        #print("Fallo baja imagen intento 3")
                        pass
                if not image_downloaded:
                    #print("\t", "*"*10, "La imagen no se encontro", "*"*10)
                    with open(log_imagenes_no_encontradas, "a") as f:
                        f.write(f"{codigo} Clave: {clave} URL: {img_url}\n")
                        
                if download_image and image_downloaded:
                    print("***", codigo, clave, img_clave, img_url, image_downloaded)
            
                    # Get current size
                    img = Image.open(BytesIO(img_data))
                    width, height = img.size
            
                    # Only resize if taller than max_height
                    if height > max_height:
                        # Compute new width keeping aspect ratio
                        new_width = int((max_height / height) * width)
                        
                        # Resize the image
                        img = img.resize((new_width, max_height), Image.LANCZOS)
                        
                    ext = os.path.splitext(img_url)[1] or ".jpg"
                    filename = os.path.join(folder, f"{img_nombre}{ext}")
            
                    #with open(filename, "wb") as f:
                    #    f.write(img_data)
                    img.save(filename)
            
                    #resize_image_keep_aspect(filename)
                    
                time.sleep(2) 
                return img_url

        def baja_imagen(df, i):
            ele = df[i]
            #url_image_page = "https://www.truper.com/ficha_tecnica/Serruchos-Dorado.html?code="+str(ele["código"])
            #url_image_page = "https://www.truper.com/BancoContenidoDigital/index.php?r=site%2Fsearch&Productos%5Bclave%5D="+str(ele["código"])
            #print(i, ele["código"], ele["descripción"], url_image_page)
            if int(ele["imagenVerificada"])==0:
                img_url = download_image(ele["codigo"], ele["clave"], "../imagenes_truper", download_image=True, tercer_link=True, i=i)
                if img_url!="YA_EXISTIA":
                    #df.at[i, "img_url"] = img_url
                    ele["imgUrl"]=img_url
                    ele["imagenVerificada"]=1
            else:
                print(f"{i}: YA PREVIA")


        def baja_imagenes(df, index_inicio, index_fin):
            #for i in range(index_inicio,index_fin):
            for i in range(index_inicio, index_fin):
                #ele = df.iloc[i]
                baja_imagen(df, i)
                if i%100==0:
                    #df.to_csv(catalogo_procesado, index=False, encoding="utf-16", sep="\t")
                    #df.save(catalogo_procesado)
                    # PROGRESS
                    pass
            #df.to_csv(catalogo_procesado, index=False, encoding="utf-16", sep="\t")
            #df.save(catalogo_procesado)
            print("FINISHED")

        # if procesaImagenes:
        #     baja_imagenes(df, 0, len(df))

        def download_codigobarras(code, i):
            time.sleep(2)
            url = "https://www.elferretero.com.mx/Carrito/Producto.aspx?NumeroProducto="+str(code).strip()
            codigo_barras=""
            r = requests.get(url)
            if r.status_code == 404:
                e_msg = f"Pagina no encontrada para {code} {url}"
                print("\t***", i, e_msg)
            else:
                try:
                    soup = BeautifulSoup(r.text, "html.parser")
                    span = soup.find("span", id="ContentPlaceHolder1_lblCodigoDeBarras")
                    codigo_barras = span.decode_contents()
                except Exception as e:
                    e_msg = f"Barras no encontradas para {code} {url}"
                    print("\t***", i, e_msg)
            if codigo_barras=="":
                with open(log_barras_no_encontradas, "a") as f:
                        f.write(f"{code} URL: {url}\n")
            return codigo_barras.strip()
        
        def baja_codigobarras(df, i):
            ele = df[i]
            if int(ele["barrasVerificada"])==0:
                #url_image_page = "https://www.truper.com/ficha_tecnica/Serruchos-Dorado.html?code="+str(ele["código"])
                #url_image_page = "https://www.truper.com/BancoContenidoDigital/index.php?r=site%2Fsearch&Productos%5Bclave%5D="+str(ele["código"])
                #print(i, ele["código"], ele["descripción"], url_image_page)
                cb = ele["codigoBarras"]
                #print("cb", cb)
                if cb is None or cb==None or cb=="" or len(cb)==0:
                    codigo_barras = download_codigobarras(ele["codigo"], i=i)
                    if codigo_barras!="":
                        # if "." in codigo_barras:
                        #     codigo_barras = codigo_barras.split(".")[0]
                        #df.at[i, "codigo_barras"] = str(codigo_barras)
                        ele["codigoBarras"] = str(codigo_barras)
                        ele["barrasVerificada"] = 1
                        print("Index", i, ele["codigo"], codigo_barras)
                else:
                    print(f"codigo barras ya existe {cb} para {ele["codigo"]}")
                    #print("Index", i, ele["codigo"], ele["codigo_barras"], "Ya existia")
            else:
                print(f"{i}: YA PREVIA")


        def baja_codigosbarras(df, index_inicio, index_fin):
            for i in range(index_inicio,index_fin):
                #ele = df.iloc[i]
                baja_codigobarras(df, i)
                if i%100==0:
                    #df.to_csv(catalogo_procesado, index=False, encoding="utf-16", sep="\t")
                    #df.save(catalogo_procesado)
                    print(f"Guardado al indice {i}")
                    # PROGRESS
            #df.to_csv(catalogo_procesado, index=False, encoding="utf-16", sep="\t")
            #df.save(catalogo_procesado)
            print("FINISHED")
        
        # if procesaBarras:
        #     baja_codigosbarras(df, 0, len(df))

        set_final_progress(len(dfTruper.rows)* (1+int(procesaBarras or procesaImagenes)))

        def baja_imagenes_barras(df, index_inicio, index_fin):
            for i in range(index_inicio,index_fin):
                if procesaBarras:
                    baja_codigobarras(df, i)
                if procesaImagenes:
                    baja_imagen(df, i)
                progress(i)
            #df.save(catalogo_procesado)

        baja_imagenes_barras(df, 0, len(df))

        # OBTENER DATOS PARA INVENTARIO (PAQUETES PIEZAS, DESCRIPCIONES, ETC) DEL CATALOGO DE TRUPER

        def dictObtenReversa(d, includeKey=False):
            dict_reversa = {}
            for k, i in d.items():
                if type(i) == str:
                    i = i.strip()
                    i = i.split(",")
                for j in  i:
                    dict_reversa[j]=k
                if includeKey:
                    dict_reversa[k]=k
            return dict_reversa
            
        # mapa_unidades = {"m":["metro"],
        #                 "kg": ["kilo"],
        #                 "lt": ["litro"],
        #                 "pz": ["pieza","pza"],
        #                 "g": ["gramo"]
        #             }
    
        mapa_unidades = {"metro":["m"],
                        "kilo": ["kg"],
                        "litro": ["lt"],
                        "pieza": ["pz","pza"]
                        ,"gramo": ["g"]
                    }
            
        def palabrasParaRegexp(palabras):
            exp_list=[]
            for p in palabras:
                p_str = ""
                for l in p:
                    p_str+=f"[{l.upper()}{l.lower()}]"
                p_str+=f"[Ss]?"
                exp_list.append(p_str)
            return exp_list

        def mapa_uni_exp_reg():
            unis = []
            for k, i in mapa_unidades.items():
                palabras = i[:] + [k]
                unis.extend(palabrasParaRegexp(palabras))
            return "|".join(unis)

        unidades = mapa_uni_exp_reg()

        #print(unidades)

        contenedores_arr = ["bolsa", "caja", "blister", "blíster", "paquete", "pack", "carrete", "juego", "estuche", "rollo", "kit", "bote", "exhibidor"]

        contenedores = "|".join(palabrasParaRegexp(contenedores_arr))
        #unidades = "m|metros|kg|kilo|pz"
        patterns = [rf"^(\d+)\s+(?:([Mm]etro|[Kk]ilo)s?\s+[Dd]e\s)?",   # Si la descripcion empieza con metro o kilo o es solo un numero
                    rf"(?:[Ee]n\s+)?(?:{contenedores})\s+(?:(?:con\s+|c\/|[dD]e\s+))?([\d\/]+)(?:\s*({unidades})?(?:\s+(?:[Dd]e\s+)?|$))",
                    rf"^[Rr]ollo.+?(\d+)\s*({unidades})(?:\W|$)",
                    #rf"(?:[\s,]+)([\d\/\.]+)\s+([lL]itro)[s]?"
                    rf"(?:\s+[Dd][Ee]|[,])?\s+([\d\/\.]+)\s+([lL]itro)[s]?"
        ]

        mapa_unidades_rev = dictObtenReversa(mapa_unidades, True)
        #print(mapa_unidades)
        #print(mapa_unidades_rev)

        # Quita marca al final de descripcion Truper, como ", Volteck" o ", HERMEX BASIC"
        def quitaParteFinal(descripcion):
            descripcionResiduo = re.findall(fr'(?:en\s+(?:{contenedores}))?(?:\s*,\s*[A-Z][a-zA-z\s]+)?$', descripcion)
            if len(descripcionResiduo)>0:
                descripcionResiduo=descripcionResiduo[0]
                descripcion=descripcion.replace(descripcionResiduo,"")
            return descripcion

        def comienzaConKiloMetro(descripcion):
            descripcionResiduo = re.findall(rf"^([Kk]ilo|[Mm]etro)\s+[Dd]e\s+", descripcion)
            if len(descripcionResiduo)>0:
                if descripcionResiduo[0].lower().startswith("kilo"):
                    return True, "kilo"
                if descripcionResiduo[0].lower().startswith("metro"):
                    return True, "metro"
            return False, ""

        def safe_to_float(value):
            if value is None:
                return 0.0
            try:
                if r"/" in value:
                    return Fraction(value)
                return float(value)
            except (ValueError, TypeError):
                return 0.0
            
        def obtenDescripcionNumeroUnidadInv(descripcion, unidadTruper, costoTruper, sugeridoTruper):
            unidad_inv=""
            numero_unidades=""
            descripcion = descripcion.strip()
            descripcion = quitaParteFinal(descripcion)
            descripcionNueva = descripcion[:]
            #print(descripcionNueva, descripcion)
            # Bolsa Caja Blister Paquete Pack Carrete Juego Estuche Rollo Kit Bote
            costo_paquete = 0
            sugerido_paquete = 0
            numero_kgs=None

            esKiloMetro, unidad_inv = comienzaConKiloMetro(descripcionNueva)
            #print("unidad_inv", unidad_inv)
            #if unidad_inv=="":
            #print(pattern)
            for pindex in range(len(patterns)):
                p = patterns[pindex]
                #print(p)
                match = re.search(p, descripcionNueva)
                if match:
                    #print("groups", match.groups())
                    #print("len groups",len(match.groups()))
                    candena_encontrada = match.group(0)
                    #print("cadena", candena_encontrada)
                    if not esKiloMetro:
                        if unidad_inv=="":
                            if len(match.groups())>1 and match.group(2):
                                unidad_inv = match.group(2).lower()
                                #print("group(2)", f"*{unidad_inv}*")
                                unidad_inv=mapa_unidades_rev.get(unidad_inv,"")
                                #print(f"***{unidad_inv}***")
                                #if unidad_inv=="g": and rollo de entonces solo pon la unidad en metros y no pongas nada del paquete
                    if numero_unidades=="":
                        int_numero = safe_to_float(match.group(1))
                        # if r"/" in match.group(1):
                        #     int_numero = Fraction(match.group(1))
                        # else:
                        #     int_numero =  int( match.group(1))
                        #print("group(1)", numero)
                        if (p.startswith("^") and int_numero>1) or (unidad_inv=='litro'):
                            numero_unidades= match.group(1)
                        elif int_numero!=1:
                            numero_unidades= match.group(1)
                            if not descripcionNueva.startswith(candena_encontrada) \
                                and (unidadTruper=="pieza" or esKiloMetro) and unidad_inv!='litro':
                                if costo_paquete==0:
                                    costo_paquete = round(int_numero * safe_to_float(costoTruper),2)
                                if sugerido_paquete ==0:
                                    sugerido_paquete = round(int_numero * safe_to_float(sugeridoTruper),2)
                        # elif int_numero>0 and int_numero<1:
                        #     if descripcionNueva.startswith(candena_encontrada):
                    if p.startswith("^"):
                        descripcionNueva=descripcionNueva[len(candena_encontrada):].strip(" ,")
                    else:
                        descripcionNueva=descripcionNueva.replace(candena_encontrada,"").strip(" ,")
                    descripcionNueva = descripcionNueva[:1].upper() + descripcionNueva[1:]
                    #if numero_unidades=="1":
                    #    numero_unidades=None
            if (unidad_inv=="gramo"):
                if numero_unidades:
                    numero_unidades=str(round(safe_to_float(numero_unidades)*1.00/1000,3))
                    unidad_inv = "kilo"
                    # AGREGADO PARA IGNORAR GRAMOS  ****** ULTIMO CAMBIO
                    unidad_inv="pieza"
                    numero_unidades="1"
                    numero_kgs=""
            if (unidad_inv=="kilo"):
                #print(descripcionNueva, unidad_inv, numero_unidades)
                if numero_unidades:
                    numero_kgs=numero_unidades[:]
                else:
                    numero_kgs="1"
                numero_unidades="111" #str(math.ceil(111*safe_to_float(contenido_kg)))
            if unidad_inv=="":
                unidad_inv="pieza"
            if numero_unidades!="":
                if costo_paquete==0:
                    costo_paquete=costoTruper
                if sugerido_paquete==0:
                    sugerido_paquete = sugeridoTruper
            else:
                costo_paquete=""
                sugerido_paquete=""
            #print(descripcionNueva, "unidades:", numero, "unidad:", unidad_inv, "costo paquete:",costo_paquete, "costo paquete sugerido:", sugerido_paquete)
            return descripcionNueva, numero_kgs, unidad_inv, numero_unidades, costo_paquete, sugerido_paquete

        dfKgUnidades = df.read_tsv(truperKgUnidades)
        dictKgUnidades = {d["codigo"]: [d["numeroUnidades"], d["unidadInv"]] for d in dfKgUnidades.rows}

        #for i in range(0, df.tail(1).index.item()+1):
        for i, row in df.iterrows():
            descripcion = row["descripcion"]
            #descripcion = quitaParteFinal(descripcion)
            descripcion, numero_kgs, unidad_inv, numero_unidades, costo_paquete, sugerido_paquete = \
            obtenDescripcionNumeroUnidadInv(descripcion, row["unidad"].lower(), \
                row["precioDistribuidorConIva"], row["precioPublicoConIva"])
            if row["codigo"] in dictKgUnidades:
                numero_unidades = dictKgUnidades[row["codigo"]][0]
                unidad_inv = dictKgUnidades[row["codigo"]][1]
                if unidad_inv in ["metro", "litro"]:
                    numero_kgs=""
            row["numeroUnidades"]=numero_unidades
            row["unidadInv"]=unidad_inv
            row["descripcionInv"]=descripcion
            row["costoPaquete"]=costo_paquete
            row["sugeridoPaquete"]=sugerido_paquete
            row["numeroKgs"]=numero_kgs
            #progress(len(df)+i)
            # numero_unidades = row["numeroUnidades"]
            # numero_kgs = row["numeroKgs"]
            # if not numero_unidades:
            #     costo_unidad= float(row["precioDistribuidorConIva"])
            #     sugerido_unidad = row["precioPublicoConIva"]
            # else:
            #     costo_paquete = row["costoPaquete"]
            #     sugerido_paquete = row["sugeridoPaquete"]
            # CALCULO COSTO Y SUGERIOD UNIDAD
            if numero_unidades and costo_paquete:
                if r"/" in numero_unidades:
                    print(f"R in {i}, {df[i]["codigo"]}", {numero_unidades})
                    numero_unidades = Fraction(numero_unidades)
                numero_unidades = float(numero_unidades)
                row["costoUnidad"]=round(float(costo_paquete)/numero_unidades,3)
                if sugerido_paquete!="*":
                    row["sugeridoUnidad"]=round(float(sugerido_paquete)/numero_unidades,3)
            elif not numero_kgs:
                costo_unidad= float(row["precioDistribuidorConIva"])
                sugerido_unidad = row["precioPublicoConIva"]
                row["costoUnidad"]=costo_unidad
                if sugerido_unidad and sugerido_unidad!="*":
                    sugerido_unidad = float(sugerido_unidad)
                    row["sugeridoUnidad"]=round(sugerido_unidad,2)
            # CALCULO COSTO Y SUGERIOD KILOGRAMO
            if numero_kgs is not None and numero_kgs!="" and costo_paquete!="":
                if r"/" in numero_kgs:
                    numero_kgs = Fraction(numero_kgs)
                numero_kgs = float(numero_kgs)
                row["costoKg"]=round(float(costo_paquete)/numero_kgs,3)
                if sugerido_paquete!="*":
                    row["sugeridoKg"]=round(float(sugerido_paquete)/numero_kgs,3)
            progress(len(df)+i)




        # for i, row in df.iterrows():
        #     #try:
        #     numero_unidades = row["numeroUnidades"]
        #     numero_kgs = row["numeroKgs"]
        #     if not numero_unidades:
        #         costo_unidad= float(row["precioDistribuidorConIva"])
        #         sugerido_unidad = row["precioPublicoConIva"]
        #     else:
        #         costo_paquete = row["costoPaquete"]
        #         sugerido_paquete = row["sugeridoPaquete"]
        #     # CALCULO COSTO Y SUGERIOD UNIDAD
        #     if numero_unidades and costo_paquete:
        #         if r"/" in numero_unidades:
        #             print(f"R in {i}, {df[i]["codigo"]}", {numero_unidades})
        #             numero_unidades = Fraction(numero_unidades)
        #         numero_unidades = float(numero_unidades)
        #         row["costoUnidad"]=round(float(costo_paquete)/numero_unidades,3)
        #         if sugerido_paquete!="*":
        #             row["sugeridoUnidad"]=round(float(sugerido_paquete)/numero_unidades,3)
        #     else:
        #         row["costoUnidad"]=costo_unidad
        #         if sugerido_unidad and sugerido_unidad!="*":
        #             sugerido_unidad = float(sugerido_unidad)
        #             row["sugeridoUnidad"]=round(sugerido_unidad,2)
        #     # CALCULO COSTO Y SUGERIOD KILOGRAMO
        #     if numero_kgs is not None and numero_kgs!="" and costo_paquete!="":
        #         if r"/" in numero_kgs:
        #             numero_kgs = Fraction(numero_kgs)
        #         numero_kgs = float(numero_kgs)
        #         row["costoKg"]=round(float(costo_paquete)/numero_kgs,3)
        #         if sugerido_paquete!="*":
        #             row["sugeridoKg"]=round(float(sugerido_paquete)/numero_kgs,3)
        #     progress(len(df)*2+i)
               

        res = df.rows

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
    procesaBarras = params.get("procesaBarras")
    procesaImagenes = params.get("procesaImagenes")

    log(f"params {params}")

    res = []
    res = codigoPrograma(temp_files, procesaImagenes, procesaBarras)
    # /********* CODIGO DEL PROGRAMA *************/ 
    print(res)
    result(res) 

if __name__ == "__main__":
    main()