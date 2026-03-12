-- CODIGO PARA MIGRAR INVENTARIO A NUEVO FORMATO

select activo, count(*) from catalogo_truper ct group by activo

select codigo, codigoBarras, descripcion from catalogo_truper ct where activo and numeroUnidades =111

SELECT * FROM inventario_wip iw WHERE codigoNumericoNuevo =45043


SELECT * FROM productos

select * from catalogo_truper ct where codigo=57001


-- catalogo truper no ha cambiado
SELECT a.codigo, a.descripcion, .precioDistribuidorConIva, b.precioDistribuidorConIva , a.precioPublicoConIva , b.precioPublicoConIva 
from catalogo_truper a
join catalogo_truper b
on a.codigo =b.codigo 
where a.activo and b.activo =0
and ((a.precioDistribuidorConIva != b.precioDistribuidorConIva) or (a.precioPublicoConIva != b.precioPublicoConIva) )


select count(*) from inventario_wip 

-- TODOS 4859
-- ACTIVOS 4812

-- 54 TIENEN 2 RECORDS - UNO PAUQTE Y UNO UNIDAD - 108 EN TTOAL
-- 4758 TIENEN UN RECORD

-- 943 SIN PRECIOES, COSTOES
-- 3385 UNIDAD UNIDAD
-- 390 PAQUETE PAQUETE
-- 6 PAQUETE UNIDAD
-- 34 UNIDAD PAQUETE


select * from inventario_wip iw where CodigoBarras ='7501206672525';

update inventario_wip set activo=0 where CodigoBarras ='7501206672525';
update inventario_wip set descripcionLimpia='Grapas 0.6mm 1/2' where CodigoBarras ='17968';

select  proveedor , UnidadInv, count(*) from inventario_wip iw  group by UnidadInv, proveedor


select count(*) from inventario_wip where activo



select * from inventario_wip where codigoBarrasNuevo not in (select codigoBarras from productos_wip) and activo
-- arena

insert into productos_wip (
codigoBarras, 
codigoNumerico, 
claves, 
proveedorId, 
descripcion, 
preferenciaVenta, 
seCompraPor, 
numeroUnidades, 
numeroKgs, 
unidadInv, 
costoSinIvaUnidad, 
precioUnidad, 
costoSinIvaPaquete, 
precioPaquete, 
costoSinIvaKg, 
precioKg, 
muestraUnidad, 
muestraPaquete, 
muestraKg, 
existenciaUnidades, 
existenciaPaquetes, 
existenciaKgs, 
minimoUnidades, 
minimoPaquetes, 
minimoKgs, 
ultimaVenta, 
activo, 
created_date, 
modified_date
)
-- limpia los departamentos
--create view merge_inventario as 
with inv_source as (
	-- TODOS LOS PRODUCTOS 
	select proveedor, coalesce(nullif(CodigoBarrasNuevo, ""), CodigoBarras) as CodigoBarrasNuevo , codigoNumerico, codigoNumericoNuevo,
	Descripcion, DescripcionLimpia, DescripcionTruper, departamento, CodigosBuscar, CodigosBuscarNuevo, inventario, minimo,
	costo, precio, numeroUnidades, coalesce(nullif(UnidadInv,''),'pieza') as UnidadInv, numeroKgs, 
	--coalesce(nullif(PrecioEs,''), 'unidad') as 
	CostoEs,
	PrecioEs, 
	--coalesce(nullif(CostoEs,''), 'unidad') as 
	 CostoUnidadTruper, sugeridoUnidadTruper, CostoPaqueteTruper, sugeridoPaqueteTruper, costoKgTruper, sugeridoKgTruper
	from inventario_wip where activo=1
)
--select count(*) from inv_source
-- 4853
,
count_records as (
	select *, count(*) over (partition by CodigoBarrasNuevo) as num_records
	from inv_source
	--SELECT CodigoBarrasNuevo, COUNT(*) AS num_records from inv_source GROUP BY CodigoBarrasNuevo
)
--SELECT num_records, COUNT(*) FROM count_records GROUP BY 1

--select num_records, CostoEs, PrecioEs, cast(not numeroUnidades is null as int) as hasNumeroUnidades, cast(not numeroKgs is null as int) as hasNumeroKgs, 
--count(*) as cnt 
--from count_records
--group by 1,2,3	,4,5
--order by 1,2 desc,3 desc	,4 asc,5 asc


	--select distinct CONCAT(
	--        UPPER(SUBSTRING(trim(departamento," .-"), 1, 1)),
	--        LOWER(SUBSTRING(trim(departamento," .-"), 2, LENGTH(trim(departamento," .-"))))
	--    ) AS departamento
	--    from count_records order by 1


-- inento primero de empezar a ver los departamentos de los productos que estan duplicados
--	select PrecioEs, CostoEs, 
--	CONCAT(
--	        UPPER(SUBSTRING(trim(departamento), 1, 1)),
--	        LOWER(SUBSTRING(trim(departamento), 2, LENGTH(trim(departamento))))
--	    ) AS departamento
--	, * from count_records where num_records>1 ORDER BY CodigoBarrasNuevo, PrecioEs, CostoEs  
--52

, one_record_only as (

	/**** NO DUPLICADOS *****/
	
	-- TRUPER SE TENIA COSTO Y PRECIO DE LA UNIDAD Y VIENEN EN UNIDAD SIN DUPLICAR, SE VENDE POR UNIDAD - SON PIEZAS - no tienen numeroUnidades ni numeroKgs
	select *
	, 'unidad' as SeCompraPor, 'unidad' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	MAX(CostoUnidadTruper, Costo) as CostoUnidad, round(MAX(CostoUnidadTruper, Costo)*1.00/1.16,3) as CostoSinIvaUnidad,
	null as CostoPaquete, null as costoSinIvaPaquete, 
	null as CostoKg, null as costoSinIvaKg, 
	Precio as PrecioUnidad, Null as PrecioPaquete, null as precioKg,
	1 muestraUnidad, 0 muestraPaquete, 0 muestraKg
	from count_records where num_records=1 and CostoEs='unidad' and PrecioEs='unidad' and numeroUnidades is null and numeroKgs is null
--	 				3064, son piezas so most products - RESOLVED	
	UNION
	select *
	, 'unidad' as SeCompraPor, 'unidad' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	MAX(CostoUnidadTruper, Costo) as CostoUnidad, round(MAX(CostoUnidadTruper, Costo)*1.00/1.16,3) as CostoSinIvaUnidad,
	MAX(CostoPaqueteTruper, Costo*numeroUnidades) as CostoPaquete, round(MAX(CostoPaqueteTruper, Costo*numeroUnidades)*1.00/1.16,3) as costoSinIvaPaquete, 
	MAX(CostoKgTruper, Costo*numeroUnidades/numeroKgs) as CostoKg, 	round(MAX(CostoKgTruper, Costo*numeroUnidades/numeroKgs)*1.00/1.16, 2) as costoSinIvaKg, 
	Precio as PrecioUnidad, Precio*numeroUnidades as PrecioPaquete, Precio*numeroUnidades/numeroKgs as precioKg,
	0 muestraUnidad, 1 muestraPaquete, 1 muestraKg	
	from count_records where num_records=1 and CostoEs='unidad' and PrecioEs='unidad' and numeroUnidades is null and numeroKgs is NOT null
--	zero - RESOLVED	
	UNION -- TRUPER SE TENIA COSTO Y PRECIO DE LA UNIDAD PERO VENIAN EN PAQUETE, SE VENDE Y PREFIERE POR UNIDAD - Son paquetes que se venden por pieza
	select *,
	'paquete' as SeCompraPor, 'unidad' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	MAX(CostoUnidadTruper, Costo) as CostoUnidad, round(MAX(CostoUnidadTruper, Costo)*1.00/1.16,3) as CostoSinIvaUnidad,
	MAX(CostoPaqueteTruper, Costo*numeroUnidades) as CostoPaquete, 	round(MAX(CostoPaqueteTruper, Costo*numeroUnidades)*1.00/1.16, 2) as costoSinIvaPaquete, 
	null as CostoKg, null as costoSinIvaKg,
	Precio as PrecioUnidad, Precio*numeroUnidades as PrecioPaquete, null as precioKg,
	1 muestraUnidad, 1 muestraPaquete, 0 muestraKg
	from count_records where num_records=1 and CostoEs='unidad' and PrecioEs='unidad' and numeroUnidades is NOT null and numeroKgs is null
--	306, paquetes que se venden por unidad
	UNION
	select *
	, 'paquete' as SeCompraPor, 'unidad' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	MAX(CostoUnidadTruper, Costo) as CostoUnidad, round(MAX(CostoUnidadTruper, Costo)*1.00/1.16,3) as CostoSinIvaUnidad,
	MAX(CostoPaqueteTruper, Costo*numeroUnidades) as CostoPaquete, 	round(MAX(CostoPaqueteTruper, Costo*numeroUnidades)*1.00/1.16, 2) as costoSinIvaPaquete, 
	MAX(CostoKgTruper, Costo*numeroUnidades/numeroKgs)  as CostoKg, 	round(MAX(CostoKgTruper, Costo*numeroUnidades/numeroKgs)*1.00/1.16, 2) as costoSinIvaKg, 
	Precio as PrecioUnidad, Precio*numeroUnidades as PrecioPaquete, Precio*numeroUnidades/numeroKgs as precioKg,
	1 muestraUnidad, 1 muestraPaquete, 1 muestraKg
	from count_records where num_records=1 and CostoEs='unidad' and PrecioEs='unidad' and numeroUnidades is NOT null and numeroKgs is NOT null
--	15, Paquetes comprados en kilo que tambien se pueden vender por pieza
	UNION -- TRUPER SE TENIA COSTO Y PRECIO DEL PAQUETE PERO NADA DEL COSTO O PRECIO POR UNIDAD, SE VENDE POR AMBOS Y SE PREFIERE POR UNIDAD
	select *
	, 'paquete' as SeCompraPor, 'Ambos' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	round(Costo*1.00/numeroUnidades,3) as CostoUnidad, round((Costo*1.00/numeroUnidades)/1.16,3) as CostoSinIvaUnidad,
	Costo as CostoPaquete, round(Costo*1.00/1.16,3) as costoSinIvaPaquete, 
	null as CostoKg, null as costoSinIvaKg,
	round(Precio*1.00/numeroUnidades,3) as PrecioUnidad, Precio as PrecioPaquete, null as precioKg,
 	0 muestraUnidad, 0 muestraPaquete, 0 muestraKg
	from count_records where num_records=1  and CostoEs='paquete' and PrecioEs='paquete' and numeroUnidades is null and numeroKgs is null
	-- zero, Paquetes que no tienen piezas ni kilogramos
	UNION
	select *
	, 'paquete' as SeCompraPor, 'Ambos' as SeVendePor, 'kilo' as PreferenciaVentaDesc, -3 PreferenciaVenta,
	null as CostoUnidad, null as CostoSinIvaUnidad,
	MAX(CostoPaqueteTruper, Costo) as CostoPaquete, round(MAX(CostoPaqueteTruper, Costo)*1.00/1.16,3) as costoSinIvaPaquete, 
	MAX(CostoKgTruper, Costo/numeroKgs)  as CostoKg, 	round(MAX(CostoKgTruper, Costo/numeroKgs)*1.00/1.16, 2) as costoSinIvaKg, 
	null as PrecioUnidad, Precio as PrecioPaquete, round(Precio*1.00/numeroKgs,3) as precioKg,
 	0 muestraUnidad, 1 muestraPaquete, 1 muestraKg
	from count_records where num_records=1 and CostoEs='paquete' and PrecioEs='paquete' and numeroUnidades is null and numeroKgs is NOT null
	-- ESTOPA REVISAR PORQUE NO SE VENDE POR KILO Y SE PIERDE EL COSTO Y EL PRECIO
	-- 1, ESTOPA **** Paquetes que  se venden por kilo 
	UNION
	select *
	, 'paquete' as SeCompraPor, 'Ambos' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	round(MAX(CostoUnidadTruper,Costo*1.00/numeroUnidades),3) as CostoUnidad, round(MAX(CostoUnidadTruper,Costo*1.00/numeroUnidades)/1.16,3) as CostoSinIvaUnidad,
	MAX(CostoPaqueteTruper, Costo) as CostoPaquete, round(MAX(CostoPaqueteTruper, Costo)*1.00/1.16,3) as costoSinIvaPaquete, 
	null as CostoKg, null as costoSinIvaKg, 
	round(Precio*1.00/numeroUnidades,3) as PrecioUnidad, Precio as PrecioPaquete,  null as precioKg,
 	1 muestraUnidad, 1 muestraPaquete, 0 muestraKg
	from count_records where num_records=1  and CostoEs='paquete' and PrecioEs='paquete' and numeroUnidades is NOT null and numeroKgs is null
	-- 363, Paquetes que se venden por unidad
	UNION
	select *
	, 'paquete' as SeCompraPor, 'Ambos' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	round(MAX(CostoUnidadTruper, Costo*1.00/numeroUnidades),3) as CostoUnidad, round(MAX(CostoUnidadTruper, Costo*1.00/numeroUnidades)/1.16,3) as CostoSinIvaUnidad,
	MAX(CostoPaqueteTruper, Costo) as CostoPaquete, round(MAX(CostoPaqueteTruper, Costo)*1.00/1.16,3) as costoSinIvaPaquete, 
	round(MAX(CostoKgTruper, Costo/numeroKgs),3) as CostoKg, round(MAX(CostoKgTruper, Costo/numeroKgs)/1.16,3) as costoSinIvaKg,
	round(Precio*1.00/numeroUnidades,3) as PrecioUnidad, Precio as PrecioPaquete, round(Precio*1.00/numeroKgs,3) as PrecioKg,
	1 muestraUnidad, 1 muestraPaquete, 1 muestraKg
	from count_records where num_records=1 and CostoEs='paquete' and PrecioEs='paquete' and numeroUnidades is NOT null and numeroKgs is NOT null
	-- 27, Paquetes comprados en kilo que tambien se pueden vender por pieza - 111
	UNION -- TRUPER SE TENIA COSTO DE UNIDAD Y PRECIO DE PAQUETE, REVISAR PORQUE ALGUNOS NO TIENEN SENTIDO
	select *
	, 'paquete' as SeCompraPor, 'Ambos' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	MAX(CostoUnidadTruper, Costo) as CostoUnidad, round(MAX(CostoUnidadTruper, Costo)*1.00/1.16,3) as CostoSinIvaUnidad, 
	round(MAX(CostoPaqueteTruper,Costo*1.00*numeroUnidades),3) as CostoPaquete, round(MAX(CostoPaqueteTruper,Costo*1.00*numeroUnidades)/1.16,3) as costoSinIvaPaquete,
	null as costoKg, null as costoSinIvaKg,
	round(Precio*1.00/numeroUnidades,3) as PrecioUnidad, Precio as PrecioPaquete, null as precioKg,
	1 muestraUnidad, 0 muestraPaquete, 0 muestraKg
	from count_records where num_records=1 and CostoEs='unidad'  and PrecioEs='paquete' and numeroUnidades is null and numeroKgs is null
	-- 0 RECORDS -	Piezas cuyo precio viene como si fuera de paquete - NO debe haber
	UNION
	select *
	, 'paquete' as SeCompraPor, 'Ambos' as SeVendePor, 'kilo' as PreferenciaVentaDesc, -3 PreferenciaVenta,
	MAX(CostoUnidadTruper, Costo) as CostoUnidad, round(MAX(CostoUnidadTruper, Costo)*1.00/1.16,3) as CostoSinIvaUnidad, 
	round(MAX(CostoPaqueteTruper,Costo*1.00*numeroUnidades),3) as CostoPaquete, round(MAX(CostoPaqueteTruper,Costo*1.00*numeroUnidades)/1.16,3) as costoSinIvaPaquete,
	round(MAX(CostoKgTruper,Costo*1.00*numeroUnidades/numeroKgs),3) as CostoKg, round(MAX(CostoKgTruper,Costo*1.00*numeroUnidades/numeroKgs)/1.16,3) as costoSinIvaKg,
	round(Precio*1.00/numeroUnidades,3) as PrecioUnidad, Precio as PrecioPaquete, round(Precio*1.00/numeroKgs,3) as PrecioKg, 
	0 muestraUnidad, 1 muestraPaquete, 1 muestraKg
	from count_records where num_records=1 and CostoEs='unidad' and PrecioEs='paquete' and numeroUnidades is null and numeroKgs is NOT null
	-- 0 records, Costo es de unidad cuando el paquete tiene kilos y no unidades
	UNION
	select *
	, 'paquete' as SeCompraPor, 'Ambos' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	MAX(CostoUnidadTruper, Costo) as CostoUnidad, round(MAX(CostoUnidadTruper, Costo)*1.00/1.16,3) as CostoSinIvaUnidad, 
	round(MAX(CostoPaqueteTruper,Costo*1.00*numeroUnidades),3) as CostoPaquete, round(MAX(CostoPaqueteTruper,Costo*1.00*numeroUnidades)/1.16,3) as costoSinIvaPaquete,
	round(MAX(CostoKgTruper,Costo*1.00*numeroUnidades/numeroKgs),3) as CostoKg, round(MAX(CostoKgTruper,Costo*1.00*numeroUnidades/numeroKgs)/1.16,3) as costoSinIvaKg,
	round(Precio*1.00/numeroUnidades,3) as PrecioUnidad, Precio as PrecioPaquete, round(Precio*1.00/numeroKgs,3) as PrecioKg, 
	1 muestraUnidad, 1 muestraPaquete, 0 muestraKg
	from count_records where num_records=1 and CostoEs='unidad' and PrecioEs='paquete' and numeroUnidades is NOT null and numeroKgs is null
--	6 RESUELTO
	UNION
	select *
	, 'paquete' as SeCompraPor, 'Ambos' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	MAX(CostoUnidadTruper, Costo) as CostoUnidad, round(MAX(CostoUnidadTruper, Costo)*1.00/1.16,3) as CostoSinIvaUnidad, 
	round(MAX(CostoPaqueteTruper,Costo*1.00*numeroUnidades),3) as CostoPaquete, round(MAX(CostoPaqueteTruper,Costo*1.00*numeroUnidades)/1.16,3) as costoSinIvaPaquete,
	round(MAX(CostoKgTruper,Costo*1.00*numeroUnidades/numeroKgs),3) as CostoKg, round(MAX(CostoKgTruper,Costo*1.00*numeroUnidades/numeroKgs)/1.16,3) as costoSinIvaKg,
	round(Precio*1.00/numeroUnidades,3) as PrecioUnidad, Precio as PrecioPaquete, round(Precio*1.00/numeroKgs,3) as PrecioKg, 
	1 muestraUnidad, 1 muestraPaquete, 1 muestraKg
	from count_records where num_records=1 and CostoEs='unidad' and PrecioEs='paquete' and numeroUnidades is NOT null and numeroKgs is NOT null
--	0 records
	UNION -- TRUPER SE TENIA EL COSTO DEL PAQUETE, PERO EL PRECIO ERA POR UNIDAD, YA SE CALCULAN LOS DOS, SE VENDE POR UNIDAD
	select *
	, 'paquete' as SeCompraPor, 'unidad' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	null as CostoUnidad, null as CostoSinIvaUnidad,
	MAX(CostoPaqueteTruper, Costo) as CostoPaquete, round(MAX(CostoPaqueteTruper, Costo)*1.00/1.16,3) as costoSinIvaPaquete, 
	null as CostoKg, null as costoSinIvaKg, 
	Precio as PrecioUnidad, round(Precio*numeroUnidades,2) as PrecioPaquete, NULL AS precioKg,
	1 muestraUnidad, 0 muestraPaquete, 0 muestraKg
	from count_records where num_records=1 and CostoEs='paquete' and PrecioEs='unidad' and numeroUnidades is null and numeroKgs is null
	-- 0 RECORDS - RESUELTO
	UNION	-- LOS QUE NO SON TRUPER Y NO ESTAN DUPLICADOS - HAY QUE REVISARLOS
	select *
	, 'paquete' as SeCompraPor, 'unidad' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	null as CostoUnidad, null as CostoSinIvaUnidad,
	MAX(CostoPaqueteTruper, Costo) as CostoPaquete, round(MAX(CostoPaqueteTruper, Costo)*1.00/1.16,3) as costoSinIvaPaquete, 
	round(MAX(CostoKgTruper, Costo/numeroKgs),3) as CostoKg, round(MAX(CostoKgTruper, Costo/numeroKgs)*1.00/1.16,3) as costoSinIvaKg, 
	Precio as PrecioUnidad, round(Precio*numeroUnidades,2) as PrecioPaquete, round(Precio*numeroUnidades/numeroKgs,2) AS precioKg,
	0 muestraUnidad, 1 muestraPaquete, 1 muestraKg
	from count_records where num_records=1 and CostoEs='paquete' and PrecioEs='unidad' and numeroUnidades is null and numeroKgs is NOT null
--	0 records
	UNION
	select *
	, 'paquete' as SeCompraPor, 'unidad' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	MAX(CostoUnidadTruper, Costo/numeroUnidades) as CostoUnidad, round(MAX(CostoUnidadTruper, Costo/numeroUnidades)*1.00/1.16,3) as CostoSinIvaUnidad, 
	MAX(CostoPaqueteTruper, Costo) as CostoPaquete, round(MAX(CostoPaqueteTruper, Costo)*1.00/1.16,3) as costoSinIvaPaquete, 
	null as CostoKg, null as costoSinIvaKg, 
	Precio as PrecioUnidad, round(Precio*numeroUnidades,2) as PrecioPaquete, null AS precioKgSinIva,
	1 muestraUnidad, 1 muestraPaquete, 0 muestraKg
	from count_records where num_records=1 and CostoEs='paquete' and PrecioEs='unidad' and numeroUnidades is NOT null and numeroKgs is null
--	29 records
	UNION
	select *
	, 'paquete' as SeCompraPor, 'unidad' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	MAX(CostoUnidadTruper, Costo/numeroUnidades) as CostoUnidad, round(MAX(CostoUnidadTruper, Costo/numeroUnidades)*1.00/1.16,3) as CostoSinIvaUnidad, 
	MAX(CostoPaqueteTruper, Costo) as CostoPaquete, round(MAX(CostoPaqueteTruper, Costo)*1.00/1.16,3) as costoSinIvaPaquete, 
	round(MAX(CostoKgTruper, Costo/numeroKgs),3) as CostoKg, round(MAX(CostoKgTruper, Costo/numeroKgs)*1.00/1.16,3) as costoSinIvaKg, 
	Precio as PrecioUnidad, round(Precio*numeroUnidades,2) as PrecioPaquete, round(Precio*numeroUnidades/numeroKgs,2) AS precioKg,
	1 muestraUnidad, 1 muestraPaquete, 1 muestraKg
	from count_records where num_records=1 and CostoEs='paquete' and PrecioEs='unidad' and numeroUnidades is NOT null and numeroKgs is NOT null
--	5 records
	UNION
	select *
	, 'unidad' as SeCompraPor, 'unidad' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	Costo as CostoUnidad, round(Costo*1.00/1.16,3) as CostoSinIvaUnidad, 
	null as CostoPaquete, null as costoSinIvaPaquete, 
	null as CostoKg, null as costoSinIvaKg, 
	Precio as PrecioUnidad, null as PrecioPaquete, null AS precioKg,
	1 muestraUnidad, 0 muestraPaquete, 0 muestraKg
	from count_records where num_records=1 and CostoEs='' and PrecioEs='' and numeroUnidades is null and numeroKgs is null
)
--select * from one_record_only
	/**** DUPLICADOS *****/

--	select *
--	, 'unidad' as SeCompraPor, 'unidad' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
--	Costo as CostoUnidad, round(Costo*1.00/1.16,3) as CostoSinIvaUnidad, 
--	null as CostoPaquete, null as costoSinIvaPaquete, 
--	null as CostoKg, null as costoSinIvaKg, 
--	Precio as PrecioUnidad, null as PrecioPaquete, null AS precioKg,
--	1 muestraUnidad, 0 muestraPaquete, 0 muestraKg
--	from count_records where num_records=2 --and CostoEs='' and PrecioEs='' and numeroUnidades is null and numeroKgs is null
--	order by codigoBarrasNuevo, precio

--select * from inventario_wip iw where codigoBarrasNuevo in (
--	select codigoBarrasNuevo  from 	count_records where num_records=2
--) order by codigoBarrasNuevo, costoEs , precioEs 


--select * from count_records where num_records=2  order by codigoBarrasNuevo, costoEs, precioEs, costo, precio



, dups as (
	-- TODOS LOS PRODUCTOS 
	select uni.proveedor, uni.CodigoBarrasNuevo , uni.codigoNumerico, uni.codigoNumericoNuevo,
	case when uni.diffDescripcionInv>paq.diffDescripcionInv then uni.Descripcion else paq.Descripcion end as descripcion, 
	case when uni.diffDescripcionInv>paq.diffDescripcionInv then uni.DescripcionLimpia else paq.DescripcionLimpia end as DescripcionLimpia, 
	--case when uni.diffDescripcionInv>paq.diffDescripcionInv then uni.DescripcionLimpia else paq.DescripcionLimpia end as DescripcionLimpia, 
	uni.DescripcionTruper, uni.departamento, uni.CodigosBuscar, uni.CodigosBuscarNuevo, uni.inventario+paq.inventario as inventario, 
	max(uni.minimo,paq.minimo) as minimo,
	null as costo, null as precio, 
	uni.numeroUnidades, uni.UnidadInv, uni.numeroKgs, 
	--coalesce(nullif(PrecioEs,''), 'unidad') as 
	null as CostoEs,
	null as PrecioEs, 
	--coalesce(nullif(CostoEs,''), 'unidad') as 
	 uni.CostoUnidadTruper, uni.sugeridoUnidadTruper, uni.CostoPaqueteTruper, uni.sugeridoPaqueteTruper, uni.costoKgTruper, uni.sugeridoKgTruper,
	 -- calculados
	 1 as num_records,
	 'paquete' as SeCompraPor, 'unidad' as SeVendePor, 'unidad' as PreferenciaVentaDesc, -1 PreferenciaVenta,
	MAX(uni.Costo, paq.Costo/uni.numeroUnidades) as CostoUnidad, round(MAX(uni.Costo, paq.Costo/uni.numeroUnidades)*1.00/1.16,3) as CostoSinIvaUnidad, 
	MAX(uni.Costo*uni.numeroUnidades, paq.costo) as CostoPaquete,  round(MAX(uni.Costo*uni.numeroUnidades, paq.costo)*1.00/1.16,3) as costoSinIvaPaquete, 
	case when paq.numeroKgs is not null then MAX(uni.Costo*uni.numeroUnidades, paq.costo)/paq.numeroKgs else null end  as CostoKg,
	case when paq.numeroKgs is not null then round(MAX(uni.Costo*uni.numeroUnidades, paq.costo)/paq.numeroKgs/1.16,3) else null end  as costoSinIvaKg,
	uni.Precio as PrecioUnidad, paq.precio as PrecioPaquete, case when paq.numeroKgs is not null then round(paq.precio/paq.numeroKgs) else null end  as precioKg,
	1 muestraUnidad, 1 muestraPaquete, case when paq.numeroKgs is not null then 1 else 0 end as  muestraKg
	 from inventario_wip uni
	 join inventario_wip paq
	 on uni.codigoBarrasNuevo =paq.codigoBarrasNuevo 
	 where uni.CodigoBarrasNuevo in (
		 select codigoBarrasNuevo  from count_records where num_records=2  
	 ) and uni.costoEs ='unidad' and uni.precioEs ='unidad'
	 and paq.CodigoBarrasNuevo in (
		 select codigoBarrasNuevo  from count_records where num_records=2  
	 ) and paq.costoEs ='paquete' and paq.precioEs ='paquete'
),
res as (
SELECT * FROM one_record_only
union
SELECT * FROM dups
),
exist_min as (
select
-- existencia
case when numeroUnidades is not null then 
		case when inventario>numeroUnidades then inventario
			when inventario<10 then inventario*numeroUnidades 
			else inventario  end 
else inventario end as existenciaUnidades,
case when numeroUnidades is not null then 
	case when inventario>numeroUnidades then round(inventario*1.00/numeroUnidades,2)
		when inventario<10 then inventario
		else round(inventario*1.00/numeroUnidades,2)   end 
else null end as existenciaPaquetes,
case when numeroKgs is not null and numeroUnidades is not null then 
		case when inventario>numeroUnidades then round(inventario*1.00*numeroKgs/numeroUnidades,2)
			when inventario<10 then inventario*numeroKgs
			else round(inventario*1.00*numeroKgs/numeroUnidades,2)   end 
else null end as existenciaKgs,
-- minimo
case when numeroUnidades is not null then 
		case when minimo>numeroUnidades then minimo
			when minimo<10 then minimo*numeroUnidades 
			else minimo  end 
else minimo end as minimoUnidades,
case when numeroUnidades is not null then 
	case when minimo>numeroUnidades then round(minimo*1.00/numeroUnidades,2)
		when minimo<10 then minimo
		else round(minimo*1.00/numeroUnidades,2)   end 
else null end as minimoPaquetes,
case when numeroKgs is not null and numeroUnidades is not null then 
		case when minimo>numeroUnidades then round(minimo*1.00*numeroKgs/numeroUnidades,2)
			when minimo<10 then minimo*numeroKgs
			else round(minimo*1.00*numeroKgs/numeroUnidades,2)   end 
else null end as minimoKgs,
 *
from res
)
--
--select seCompraPor, unidadInv, numeroUnidades, numeroKgs, inventario, existenciaUnidades, existenciaPaquetes, existenciaKgs, minimo,
--minimoUnidades, minimoPaquetes, minimoKgs
--from exist_min
--order by 1,2,3,4
select 
CodigoBarrasNuevo as codigoBarras, 
codigoNumericoNuevo as codigoNumerico, 
CodigosBuscarNuevo as claves, 
case proveedor when 'Truper' then 1 else 5 end as proveedorId, 
DescripcionLimpia as descripcion, 
preferenciaVenta, 
seCompraPor, 
numeroUnidades, 
numeroKgs, 
case unidadInv when 'kilo' then '' else unidadInv end as unidadInv, 
costoSinIvaUnidad, 
precioUnidad, 
costoSinIvaPaquete, 
precioPaquete, 
costoSinIvaKg, 
precioKg, 
muestraUnidad, 
muestraPaquete, 
muestraKg, 
existenciaUnidades, 
existenciaPaquetes, 
existenciaKgs, 
minimoUnidades, 
minimoPaquetes, 
minimoKgs, 
datetime('now', 'localtime') as ultimaVenta, 
1 activo, 
datetime('now', 'localtime') as created_date, 
datetime('now', 'localtime') as modified_date
from exist_min;

-- YA EN PRODUCTOS
UPDATE PRODUCTOS SET codigoNumerico=substr(codigoNumerico, 1, INSTR(codigoNumerico,',')-1) ,
claves = substr(codigoNumerico, INSTR(codigoNumerico,',')+1) where codigoNumerico LIKE '%,%';
UPDATE PRODUCTOS SET unidadInv='pieza' where numeroUnidades=111 and unidadInv='';
update PRODUCTOS set muestraPaquete =0 where numeroKgs =1 and numeroUnidades is not null;
--select * from PRODUCTOS where DESCRIPCION LIKE '%BOLSA%';
--select * FROM PRODUCTOS_wip WHERE codigoNumerico LIKE '%,%';
--select * from PRODUCTOS where DESCRIPCION LIKE '%metro%';
--select * from PRODUCTOS where DESCRIPCION LIKE '%estuche%';
--select * from PRODUCTOS where DESCRIPCION LIKE '%rollo%';

-- CAL
-- CEMENTO
-- YESO
-- ESTUCO
-- 

--select distinct CodigoBarrasNuevo from res
--select codigoNumericoNuevo, CostoUnidad, CostoPaquete, CostoKg, CostoPaquete/CostoUnidad as calcNumUnidades, numeroUnidades, precioUnidad, precioPaquete, precioPaquete/precioUnidad as calcPreNUmeroUnidades,
--	precioUnidad-costoUnidad>0 as precioUnidadMayor, precioPaquete-costoPaquete>0 as precioPaqueteMayor
--	from dups


--select * from productos_wip




