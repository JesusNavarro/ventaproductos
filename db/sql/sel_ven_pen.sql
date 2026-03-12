
with base_query as (
	
    select
	a.dispositivoId,
	a.fechaVenta,
	a.productoId,
	a.tipoVentaId,
	a.sinInventario,
	a.cancelada,
	case a.tipoVentaId when -5 then a.extraInfo else b.codigoBarras end as codigoBarras,
	b.codigoNumerico,
	b.claves,
	case a.tipoVentaId when -4 then a.extraInfo else b.descripcion end as descripcion,
	case a.tipoVentaId 
		when -4 then 'comun'
		when -5 then 'sin inventario'
		when -1 then b.unidadInv
		when -2 then 'paquete' || 
			case when b.numeroUnidades is not null then ' ' || b.numeroUnidades || ' ' || b.unidadInv || 's' else '' end || 
			case when b.numeroKgs is not null then ' ' || b.numeroKgs || ' kgs' else '' end
		when -3 then 'kg'
	end as ventaPor,
	case a.tipoVentaId 
	when -1 then b.costoSinIvaUnidad
	when -2 then b.costoSinIvaPaquete
	when -3 then b.costoSinIvaKg
	else 0 end * (select coalesce(1+(valor/100.00),1) from ajustes where variable='IVA' and desde <= a.fechaVenta ORDER BY desde DESC LIMIT 1 ) as costo,
	a.precio,
	a.precioVenta,
	a.cantidad,
	replace(
	case a.tipoVentaId 
		when -4 then a.cantidad || ' articulo'
		when -1 then a.cantidad || ' ' || b.unidadInv || iif(a.cantidad>1,'s','')
		when -2 then a.cantidad || ' paquete' || iif(a.cantidad>1,'s','') || ' (' || trim(
				case when b.numeroUnidades is not null then (a.cantidad * b.numeroUnidades) || ' ' || b.unidadInv || iif(a.cantidad*b.numeroUnidades>1,'s','') else '' end || 
				case when b.numeroKgs is not null then ' ' || (a.cantidad * b.numeroKgs) || ' kg' || iif(a.cantidad * b.numeroKgs>1,'s','') else '' end) || ')'
		when -3 then a.cantidad || ' kgs' 
	end
	, '.0 ', ' ') as descCantidad,
	a.subtotal,
	a.extraInfo,
	b.numeroUnidades,
	b.numeroKgs,
	case a.tipoVentaId 
    when -1 then a.cantidad
	when -4 then a.cantidad
	when -2 then case when b.numeroUnidades is not null then a.cantidad * b.numeroUnidades end
	when -3 then case when b.numeroUnidades is not null and b.numeroKgs is not null then (a.cantidad / b.numeroKgs)* b.numeroUnidades end
	end as cantidadUnidades,
	case a.tipoVentaId 
	when -1 then case when b.numeroUnidades is not null then a.cantidad / b.numeroUnidades end
	when -4 then case when b.numeroUnidades is not null then a.cantidad / b.numeroUnidades end
	when -2 then a.cantidad
	when -3 then case when b.numeroKgs is not null then a.cantidad / b.numeroKgs end
	end as cantidadPaquetes,
	case a.tipoVentaId 
	when -1 then case when b.numeroUnidades is not null and b.numeroKgs is not null then (a.cantidad / b.numeroUnidades)* b.numeroKgs end
	when -4 then case when b.numeroUnidades is not null and b.numeroKgs is not null then (a.cantidad / b.numeroUnidades)* b.numeroKgs end
	when -2 then case when b.numeroKgs is not null then a.cantidad * b.numeroKgs end
	when -3 then a.cantidad
	end as cantidadKgs,
	b.unidadInv,
	c.fechaInventario,
	b.minimoUnidades,
	b.minimoPaquetes,
	b.minimoKgs
from
	ventas_esclavos a
    left join productos b
    on a.productoId = b.productoId 
	left join ventas c
	on a.dispositivoId=c.dispositivoId
	and a.fechaVenta=c.fechaVenta
	and a.productoId=c.productoId
	where 1=1
	{and_where}
),
cantidadesAccum as (
select a.*,
	sum(iif(fechaInventario is null and not coalesce(cancelada,0),  cantidadUnidades)) over (PARTITION BY productoId ORDER BY fechaVenta, abs(tipoVentaId)) as cantidadUnidadesAccum,
	sum(iif(fechaInventario is null and not coalesce(cancelada,0),  cantidadPaquetes)) over (PARTITION BY productoId ORDER BY fechaVenta, abs(tipoVentaId)) as cantidadPaquetesAccum,
	sum(iif(fechaInventario is null and not coalesce(cancelada,0),  cantidadKgs)) over (PARTITION BY productoId ORDER BY fechaVenta, abs(tipoVentaId)) as cantidadKgsAccum
from base_query a
),
inv_nuevo as (
select a.*,
	b.existenciaUnidades,
	b.existenciaPaquetes,
	b.existenciaKgs,
	b.existenciaUnidades-a.cantidadUnidadesAccum as existenciaNuevaUnidades,
	b.existenciaPaquetes-a.cantidadPaquetesAccum as existenciaNuevaPaquetes,
	b.existenciaKgs-a.cantidadKgsAccum as existenciaNuevaKgs,
	case when fechaInventario is not null then 'Ya en inventario' else 
		replace(trim(
		case when a.cantidadPaquetesAccum is null and a.cantidadKgsAccum is null 
			then ROUND(a.cantidadUnidadesAccum, 2) || ' ' || a.unidadInv || iif(a.cantidadUnidadesAccum>1,'s','') else '' end ||
		case when a.cantidadPaquetesAccum is not null 
			then ROUND(a.cantidadPaquetesAccum, 2) || ' paquete' || iif(a.cantidadPaquetesAccum>1,'s','') || ' (' ||
				trim(case when a.cantidadUnidadesAccum is not null then ROUND(a.cantidadUnidadesAccum, 2) || ' ' || a.unidadInv || iif(a.cantidadUnidadesAccum>1,'s','') else '' end || 
				case when a.cantidadKgsAccum is not null then ' ' || ROUND(a.cantidadKgsAccum, 2) || ' kg' || iif(a.cantidadKgsAccum>1,'s','') else '' end )
			|| ')' else '' end ||
		case when a.cantidadUnidadesAccum is null and a.cantidadPaquetesAccum is null 
			then ROUND(a.cantidadKgsAccum, 2) || ' kg' || iif(a.cantidadKgsAccum>1,'s','') else '' end 
		), '.0 ', ' ') 
	end as descCantidadAccum
from cantidadesAccum a
    left join productos b
    on a.productoId = b.productoId
)
select a.*,
	case when fechaInventario is not null then 'Ya en inventario' else 
		replace(trim(
		case when a.existenciaNuevaPaquetes is null and a.existenciaNuevaKgs is null 
			then ROUND(a.existenciaNuevaUnidades, 2) || ' ' || a.unidadInv || iif(abs(a.existenciaNuevaUnidades)>1,'s','') else '' end ||
		case when a.existenciaNuevaPaquetes is not null 
			then ROUND(a.existenciaNuevaPaquetes, 2) || ' paquete' || iif(abs(a.existenciaNuevaPaquetes)>1,'s','') || ' (' ||
				trim(case when a.existenciaNuevaUnidades is not null then ROUND(a.existenciaNuevaUnidades, 2) || ' ' || a.unidadInv || iif(abs(a.existenciaNuevaUnidades)>1,'s','') else '' end || 
				case when a.existenciaNuevaKgs is not null then ' ' || ROUND(a.existenciaNuevaKgs, 2) || ' kg' || iif(abs(a.existenciaNuevaKgs)>1,'s','') else '' end )
			|| ')' else '' end ||
		case when a.existenciaNuevaUnidades is null and a.existenciaNuevaPaquetes is null 
			then ROUND(a.existenciaNuevaKgs, 2) || ' kg' || iif(abs(a.existenciaNuevaKgs)>1,'s','') else '' end 
		), '.0 ', ' ') 
	end 
	as descExistenciaNueva
from inv_nuevo a
order by fechaVenta asc, descripcion, tipoVentaId