select {simple_columns},
case preferenciaVenta
	when -1 then unidadInv
	when -2 then 'paquete ('
		|| case when numeroUnidades is not null then ' ' || numeroUnidades ||' '|| unidadInv||'s' else '' end
		|| case when numeroKgs is not null then ' ' || numeroKgs ||' kgs' else '' end
		|| ')'
	when -3 then 'kilo' end as descVenta,
case preferenciaVenta
	when -1 then precioUnidad
	when -2 then precioPaquete
	when -3 then precioKg end as precio,
case preferenciaVenta
	when -1 then existenciaUnidades || ' '|| unidadInv||'s' 
	when -2 then existenciaPaquetes || ' paquetes'
	when -3 then existenciaKgs || ' kgs' end as descExistencia,
case preferenciaVenta
	when -1 then existenciaUnidades
	when -2 then existenciaPaquetes
	when -3 then existenciaKgs end as existencia,
case preferenciaVenta
	when -1 then minimoUnidades
	when -2 then minimoPaquetes
	when -3 then minimoKgs end as minimo,
case when muestraUnidad then unidadInv end as descVentaUnidad,
case when muestraPaquete then 'paquete (' ||
		case when numeroUnidades is not null then ' ' || numeroUnidades ||' '|| unidadInv||'s' else '' end 
		|| case when numeroKgs is not null then ' ' || numeroKgs ||' kgs' else '' end
	end || ')' as descVentaPaquete,
case when muestraKg then case when numeroKgs is not null then 'kilo' else '' end end as descVentaKg,
b.proveedor
from productos a
left join proveedores b on a.proveedorId=b.proveedorId
where {conditions}
order by {order_by}

