#!//bin/bash

SOURCE="/Users/delfigre/Desktop/GDrive/Tlapaleria/ventaproductos"
DEST="/Users/delfigre/syncFolder/ventaproductos"

copy_item() {
  local name="$1"
  local src="$SOURCE/$name"
  local dst="$DEST/$name"

  # Check if source exists
  if [ ! -e "$src" ]; then
    echo "❌ ERROR: '$src' does not exist."
    return 1
  fi

  # If it's a directory
  if [ -d "$src" ]; then
    echo "📁 $name"
    mkdir -p "$dst"
    if [ $? -ne 0 ]; then
      echo "❌ ERROR: Failed to create directory: $dst"
      return 2
    fi
    #echo "✅ Directory created successfully: $dst"
  
  # If it's a file
  elif [ -f "$src" ]; then
    echo "     📄 $name"
    cp "$src" "$dst"
    if [ $? -ne 0 ]; then
      echo "❌ ERROR: Failed to copy file: $src → $dst"
      return 3
    fi
    #echo "✅ File copied successfully: $dst"

  else
    echo "⚠️  WARNING: '$src' is not a regular file or directory (maybe a symlink or special file)."
    return 4
  fi
}

copy_item "db"
copy_item "db/ajustesDAO.py"
copy_item "db/baseDatosDAO.py"
copy_item "db/catalogoTruperDAO.py"
copy_item "db/dbMapper.py"
copy_item "db/dispositivosDAO.py"
copy_item "db/pedidosDAO.py"
copy_item "db/productosDAO.py"
copy_item "db/ventasDAO.py"

copy_item "db/models"

copy_item "db/sql"
copy_item "db/sql/create_ajustes.sql"
copy_item "db/sql/create_catalogo_truper.sql"
copy_item "db/sql/create_proveedores.sql"
copy_item "db/sql/create_productos.sql"
copy_item "db/sql/create_registros.sql"
copy_item "db/sql/find_producto.sql"
copy_item "db/sql/create_inventario_wip.sql"
copy_item "db/sql/sel_ven_pen.sql"
copy_item "db/sql/truper_kg_unidades.sql"
copy_item "db/sql/codigoMigrar.sql"
copy_item "db/sql/inventario_ajustes.sql"
copy_item "db/sql/create_ventas.sql"

copy_item "procesos"
copy_item "procesos/jobManager.py"
copy_item "procesos/jobs"
copy_item "procesos/logs"
copy_item "procesos/tmp"
copy_item "procesos/jobs/process_file.py"
copy_item "procesos/jobs/pandasReader.py"
copy_item "procesos/jobs/procesaInventario.py"
copy_item "procesos/jobs/procesaTruper.py"


copy_item "services"
copy_item "services/businessLogic.py"

#copy_item "inventario"
#copy_item "inventario/inventario.txt"

copy_item "logs"

copy_item "static"
copy_item "static/favicon.ico"

copy_item "static/css"
copy_item "static/css/bootstrap.min.css"
copy_item "static/css/buscadorProducto.css"
copy_item "static/css/workspace.css"
copy_item "static/css/helpers.css"

copy_item "static/imagenes"
copy_item "static/imagenes/borrar_icon.png"
copy_item "static/imagenes/cancela_venta.png"
copy_item "static/imagenes/cancelar.png"
copy_item "static/imagenes/down_icon.jpg"
copy_item "static/imagenes/favicon.ico"
copy_item "static/imagenes/info.png"
copy_item "static/imagenes/kg.png"
copy_item "static/imagenes/litro.png"
copy_item "static/imagenes/metro.png"
copy_item "static/imagenes/minus_icon.jpg"
copy_item "static/imagenes/paquete_icon.jpg"
copy_item "static/imagenes/paquete.png"
copy_item "static/imagenes/pieza_icon.jpg"
copy_item "static/imagenes/pieza.png"
copy_item "static/imagenes/plus_icon.jpg"
copy_item "static/imagenes/up_icon.jpg"
copy_item "static/imagenes/ver_icon.jpg"

copy_item "static/js"
copy_item "static/js/buscadorProducto.js"
copy_item "static/js/html5-qrcode.min.js"
copy_item "static/js/jobs.js"
copy_item "static/js/mac_scanner.js"
copy_item "static/js/main.js"
copy_item "static/js/tablet_scanner.js"
copy_item "static/js/zxing.min.js"

copy_item "static/js/helpers.js"
copy_item "static/js/producTabla.js"
copy_item "static/js/vender.js"
copy_item "static/js/ventaProductoViewer.js"
copy_item "static/js/workspace.js"


copy_item "templates"
copy_item "templates/home.html"
copy_item "templates/entregas.html"
copy_item "templates/index.html"
copy_item "templates/vender.html"
copy_item "templates/ventas_viewer.html"
copy_item "templates/redirect.html"
copy_item "templates/ajustes.html"
copy_item "templates/producto.html"
copy_item "templates/resumen.html"
copy_item "templates/workspace.html"
copy_item "templates/pendientes.html"
copy_item "templates/truper.html"

copy_item "ventas"

copy_item "app.py"
#copy_item "config.py"
copy_item "kill_port.sh"
copy_item "Venta_Productos.sh"
#copy_item "restartflask.bat"
#copy_item "killport.bat"

copy_item "Truper"
copy_item "Truper/procesa_catalogo"
copy_item "Truper/procesa_catalogo/ProcesaImagenesBarras.ipynb"
copy_item "Truper/catalogo_truper.json"
copy_item "Truper/catalogo.html"
copy_item "Truper/jquery-3.7.1.min.js"
copy_item "Truper/up_image.png"

sleep 10
exit 0


