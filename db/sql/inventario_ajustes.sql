
-- AJUSTES INVENTARIO ********



--	delete from inventario_wip

--SELECT * FROM PROVEEDORES

-- AJUSTES DESPUES DE CARAGAR INVENTARIO

--delete from inventario_wip
--select count(*) from inventario_wip

--select * from  inventario_wip where descripcion like '%Niple Galvanizado%'	
--delete from inventario_wip where codigoBarras='7506240627203' and inventario=0;	-- VERIFIED
--select * from  inventario_wip where codigoBarras='7506240627203'


-- inventario_ajustes
--select * from inventario_wip iw  where CodigoBarrasNuevo is null or CodigoBarrasNuevo='';
update inventario_wip set CodigoBarrasNuevo =CodigoBarras where CodigoBarrasNuevo is null or CodigoBarrasNuevo='';	-- VERIFIED

-- select CodigoBarras, activo, CodigoBarrasNuevo, CodigosBuscar, CodigosBuscarNuevo,  Descripcion, DescripcionTruper, Unidad, UnidadInv, NumeroUnidades, Costo, CostoUnidadTruper, CostoPaqueteTruper, CostoComparacion, CostoEs, Precio, PrecioComparacion, PrecioEs
-- from inventario_wip where CodigoBarrasNuevo in (
-- select distinct CodigoBarrasNuevo  from inventario_wip where CodigoBarrasNuevo !=""
-- group by CodigoBarrasNuevo 
-- having count(*)>1
-- --order by 2 desc
-- )
-- order by 3, 7

-- AJUSTES;
-- ART 1;
-- select * from inventario_wip iw where CodigoBarras='ELECTRODO60133/32';
update inventario_wip set activo=0 where CodigoBarras ='ELECTRODO60133/32';		-- VERIFIED

-- ART 2;	-- VERIFIED			-- VERIFICAR ESTE
-- select * from inventario_wip iw where CodigoBarrasNuevo='7501206622735';
update inventario_wip set UnidadInv='metro', NumeroUnidades=9, CostoPaqueteTruper=CostoUnidadTruper, sugeridoPaqueteTruper=sugeridoUnidadTruper
where CodigoBarrasNuevo='7501206622735'; 	-- https://www.elferretero.com.mx/Carrito/Producto.aspx?NumeroProducto=14365 ;
update inventario_wip set CostoUnidadTruper=CostoPaqueteTruper/NumeroUnidades, sugeridoUnidadTruper=sugeridoPaqueteTruper/NumeroUnidades
where CodigoBarrasNuevo='7501206622735';
update inventario_wip set PrecioComparacion=Precio-sugeridoUnidadTruper,  CostoComparacion=Costo-CostoUnidadTruper where CodigoBarras='7501206622735 1';
update inventario_wip set CostoEs='paquete', PrecioEs='paquete' where CodigoBarras='7501206622735';
update inventario_wip set descripcionLimpia ='Soldadura Centicore Nucleo De Resina 50/50' where CodigoBarrasNuevo='7501206622735';

-- ART 3;	-- VERIFIED
-- codigo barras nuevo - 7501206623251 - tiene dos precios 2 y 3;
-- ********* -- select * FROM inventario_wip where CodigoBarrasNuevo='7501206623251';
-- select * from inventario_wip iw where CodigoBarrasNuevo='7501206623251';
update inventario_wip set DescripcionLimpia=Descripcion where CodigoBarrasNuevo ='7501206623251';
update inventario_wip set activo=0 where CodigoBarrasNuevo ='7501206623251' and CodigoBarras='PIJAA 1/4 PO 2';
update inventario_wip set proveedor='Otro', codigoNumericoNuevo=null where CodigoBarrasNuevo ='7501206623251';


-- ART 4;
-- CONFIRMAR REGISTRO INACTIVO YA NO SIRVE ;
-- select * FROM inventario_wip where CodigoBarrasNuevo='7501206630501';
-- select * FROM catalogo_truper ct  where codigo=17155;
update inventario_wip set activo=0 where CodigoBarras ='17155';	-- VERIFIED

-- ART 5;
-- CONFIRMAR REGISTRO INACTIVO YA NO SIRVE - tiene dos precios 48 Y 60;
-- select * FROM catalogo_truper ct  where codigo=11218;
-- select * FROM inventario_wip where CodigoBarrasNuevo='7501206634523';
-- select * FROM inventario_wip where CodigoBarras='11218';
update inventario_wip set activo=0 where CodigoBarras ='11218';		-- VERIFIED
update inventario_wip set inventario=3 where CodigoBarras ='7501206634523';	

-- ART 6;
-- CONFIRMAR REGISTRO INACTIVO YA NO SIRVE - tiene dos precios 90 Y 80;
-- select * FROM catalogo_truper ct  where codigo=11218;
-- select * FROM inventario_wip where CodigoBarrasNuevo='7501206634578';
-- select * FROM inventario_wip where CodigoBarras='7501206634578';
update inventario_wip set activo=0 where CodigoBarras ='7501206634578';	-- VERIFIED

-- ART 7;
-- CONFIRMAR REGISTRO INACTIVO YA NO SIRVE - tiene dos precios 40 Y 43;
-- select * FROM catalogo_truper ct  where codigo=11218;
-- select * FROM inventario_wip where CodigoBarrasNuevo='7501206648254';
-- select * FROM inventario_wip where CodigoBarras='7501206648254';
update inventario_wip set activo=0 where CodigoBarras ='7501206648254';
update inventario_wip set descripcionLimpia=descripcionTruperInv where CodigoBarrasNuevo ='7501206648254'; 	-- VERIFIED

-- ART 8;
-- CONFIRMAR REGISTRO INACTIVO YA NO SIRVE - tiene dos precios 45 Y 50;
-- select * FROM catalogo_truper ct  where codigo=15140;
-- select * FROM inventario_wip where CodigoBarrasNuevo='7501206648308';
update inventario_wip set activo=0 where CodigoBarras ='15140';
update inventario_wip set inventario=5 where CodigoBarras ='7501206648308';		-- VERIFIED

-- ART 9;
-- CONFIRMAR REGISTRO INACTIVO YA NO SIRVE - tiene dos precios 60 Y 65;
-- select * FROM catalogo_truper ct  where codigo=15142;
-- select * FROM inventario_wip where CodigoBarrasNuevo='7501206648315';	-- VERIFIED
-- select * FROM inventario_wip where CodigoBarras='15142';
update inventario_wip set activo=0 where CodigoBarras ='15142';
update inventario_wip set inventario=1 where CodigoBarras ='7501206648315';	

-- ART 10;
-- CONFIRMAR REGISTRO INACTIVO YA NO SIRVE - MAL EL PRECIO DE UNO;
-- select * FROM catalogo_truper ct  where codigo=18397;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7501206652343';
-- select * FROM inventario_wip where CodigoBarras='18397';
update inventario_wip set activo=0 where CodigoBarras ='7501206652343' AND codigoNumerico ="";

-- ART 11;		MISMO QUE ARTICULO 10
-- CONFIRMAR REGISTRO INACTIVO YA NO SIRVE - MAL EL PRECIO DE UNO;
--select * FROM catalogo_truper ct  where codigo=18397;			-- VERIFIED
--select * FROM inventario_wip where CodigoBarrasNuevo='7501206652343';
--select * FROM inventario_wip where CodigoBarras='18397';
update inventario_wip set activo=0 where CodigoBarras ='7501206652343' AND CodigoNumerico ="";

-- art 12 - costo mal;
-- select * FROM catalogo_truper ct  where codigo=17968;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7501206672525';
-- select * FROM inventario_wip where CodigoBarras='17968';
update inventario_wip set activo=0 where CodigoBarras ='7501206672525';
update inventario_wip set descripcionLimpia='Grapas 0.6mm 1/2' where CodigoBarras ='17968';

-- ART 13 - DUPLICADO CON COSTO MAL;
-- select * FROM catalogo_truper ct  where codigo=44414;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7501206686805';
-- select * FROM inventario_wip where CodigoBarras='44414';
update inventario_wip set activo=0 where CodigoBarras ='7501206686805';

-- art 14 - duplicado con precio mal;
-- select * FROM catalogo_truper ct  where codigo=19860;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7501206697672';
-- select * FROM inventario_wip where CodigoBarras='17501206697679';
update inventario_wip set activo=0 where CodigoBarras ='17501206697679';

-- ART 15 ---------- PREGUNTAR - DUPLCIADO CON COSTO POR PIEZA DIFERENTE	**************************	ES TUERCA Y TORNILLO;
-- ********* -- select * FROM inventario_wip where CodigoBarrasNuevo='7506240600985'	;
-- EL TORNILLO NO SABEMOS CUAL ES - 
-- select * FROM catalogo_truper ct  where codigo=44698;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo like '%7506240600985%';
-- select * FROM inventario_wip where CodigoBarras='7506240600985';
update inventario_wip set CodigoBarrasNuevo=CodigoBarrasNuevo||'-X', CodigoNumericoNuevo='' where CodigoBarras ='7506240600985';
update inventario_wip set costoEs = 'paquete' where CodigoBarrasNuevo='7506240600985';


-- ART 16 ---------- PREGUNTAR - DUPLCIADO CON COSTO POR PIEZA DIFERENTE	**************************;
-- ********* -- select * FROM inventario_wip where CodigoBarrasNuevo='7506240601371';
-- select * FROM catalogo_truper ct  where codigo=44557;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240601371';
-- select * FROM inventario_wip where CodigoBarras='7506240601371';
update inventario_wip set activo=0 where CodigoBarras ='7506240601371';
update inventario_wip set inventario=217 where CodigoBarras ='TORNILLOMAQ1/4';

-- ART 17 -- DUPLICATE;
-- select * FROM catalogo_truper ct  where codigo=44558;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240601388';
-- select * FROM inventario_wip where CodigoBarras='7506240601388';
update inventario_wip set activo=0 where CodigoBarras ='7506240601388';

-- art 18 - duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=49659;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240619444';
-- select * FROM inventario_wip where CodigoBarras='7506240619444';
update inventario_wip set activo=0 where CodigoBarras ='7506240619444';
update inventario_wip set descripcionLimpia='Tuerca union cobre a rosca externa 1/2' where CodigoBarrasNuevo ='7506240619444';


-- ART 19 - ONE IS UNIT ONE IS PACKAGE BUT HAS NO NUMBER OF UNITS;
-- select * FROM catalogo_truper ct  where codigo=45032;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240619994';
-- select * FROM inventario_wip where CodigoBarras='7506240619994';
update inventario_wip set descripcionLimpia ='Rafia blanca calibre 2.2 g/m' where CodigoBarrasNuevo='7506240619994';


-- art 20 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=44959;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240624172';
-- select * FROM inventario_wip where CodigoBarras='7506240624172';
-- select * FROM inventario_wip where codigoNumericoNuevo =44959;
-- select * FROM inventario_wip WHERE descripcion LIKE '%MALLA%'
--update inventario_wip set activo=0 where CodigoBarras ='7506240624172';
update inventario_wip set descripcionLimpia ='Malla Mosquitera Gris Plastica 0.9' where CodigoBarrasNuevo='7506240624172';

-- otras mallas mosquiteras-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='710631915344';

-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='MAYAGALLINA';

-- select * FROM catalogo_truper ct  where codigo=44960;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240624189';

-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240624103';
update inventario_wip set descripcionLimpia ='Malla Mosquitera Verde Plastica 0.9m' where CodigoBarrasNuevo='7506240624103';

-- select * FROM catalogo_truper ct  where codigo=44656;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240606086';
-- select * FROM inventario_wip where CodigoBarras='7506240606086';
-- select * FROM inventario_wip where codigoNumericoNuevo =44656;

-- select * FROM catalogo_truper ct  where codigo=44954;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240624127';
-- select * FROM inventario_wip where CodigoBarras='7506240624127';
-- select * FROM inventario_wip where codigoNumericoNuevo =44954;

-- select * FROM catalogo_truper ct  where codigo=103141;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506610203105';
-- select * FROM inventario_wip where CodigoBarras='7506610203105';
-- select * FROM inventario_wip where codigoNumericoNuevo =103141;


-- art 21 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=45102;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240627944';
-- select * FROM inventario_wip where CodigoBarras='7506240627944';
-- select * FROM inventario_wip where codigoNumericoNuevo =45102;
update inventario_wip set activo=0 where CodigoBarras ='7506240627944';



-- art 22 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=45108;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240628002';
-- select * FROM inventario_wip where CodigoBarras='45108';
-- select * FROM inventario_wip where codigoNumericoNuevo =45108;
update inventario_wip set activo=0 where CodigoBarras ='45108';

-- art 23 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=47433;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240629962';
-- select * FROM inventario_wip where CodigoBarras='47433';
-- select * FROM inventario_wip where codigoNumericoNuevo =47433;
update inventario_wip set activo=0 where CodigoBarras ='47433';



-- ART 24 - ONE IS UNIT ONE IS PACKAGE BUT HAS NO NUMBER OF UNITS;
-- select * FROM catalogo_truper ct  where codigo=45043;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240646570';
-- select * FROM inventario_wip where CodigoBarras='45043';
-- select * FROM inventario_wip where codigoNumericoNuevo =45043;
update inventario_wip set UnidadInv='metro', NumeroUnidades=3, CostoPaqueteTruper=CostoUnidadTruper, sugeridoPaqueteTruper=sugeridoUnidadTruper
where CodigoBarrasNuevo='7506240646570';
update inventario_wip set descripcionLimpia ='Tubo CPVC 3/4 Café' where CodigoBarrasNuevo='7506240646570';
update inventario_wip set CostoUnidadTruper=CostoPaqueteTruper/NumeroUnidades, sugeridoUnidadTruper=sugeridoPaqueteTruper/NumeroUnidades
where CodigoBarrasNuevo='7506240646570';
update inventario_wip set PrecioComparacion=Precio-sugeridoUnidadTruper,  CostoComparacion=Costo-CostoUnidadTruper where CodigoBarras='TUBOCPVA3/4CAFE';
update inventario_wip set CostoEs='paquete', PrecioEs='paquete' where CodigoBarras='TUBOCPVC3/43MTS.';

-- ART 25 - ONE IS UNIT ONE IS PACKAGE BUT HAS NO NUMBER OF UNITS;
-- select * FROM catalogo_truper ct  where codigo=43038;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240648789';
-- select * FROM inventario_wip where CodigoBarras='43038';
-- select * FROM inventario_wip where codigoNumericoNuevo =43038;
update inventario_wip set UnidadInv='metro', NumeroUnidades=3, CostoPaqueteTruper=CostoUnidadTruper, sugeridoPaqueteTruper=sugeridoUnidadTruper
where CodigoBarrasNuevo='7506240648789';
update inventario_wip set descripcionLimpia ='Tubo PVC Hidra 1/2 Blanco' where CodigoBarrasNuevo='7506240648789';
update inventario_wip set CostoUnidadTruper=CostoPaqueteTruper/NumeroUnidades, sugeridoUnidadTruper=sugeridoPaqueteTruper/NumeroUnidades
where CodigoBarrasNuevo='7506240648789';
update inventario_wip set PrecioComparacion=Precio-sugeridoUnidadTruper,  CostoComparacion=Costo-CostoUnidadTruper where CodigoBarras='TUBOHIDRA1/2';
update inventario_wip set CostoEs='paquete', PrecioEs='paquete' where CodigoBarras='TUBOPVCHIDRA1/2';

-- ART 26 - ONE IS UNIT ONE IS PACKAGE BUT HAS NO NUMBER OF UNITS;
-- select * FROM catalogo_truper ct  where codigo=43040;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240648802';
-- select * FROM inventario_wip where CodigoBarras='43040';
-- select * FROM inventario_wip where codigoNumericoNuevo =43040;
update inventario_wip set UnidadInv='metro', NumeroUnidades=3, CostoPaqueteTruper=CostoUnidadTruper, sugeridoPaqueteTruper=sugeridoUnidadTruper
where CodigoBarrasNuevo='7506240648802';
update inventario_wip set descripcionLimpia ='Tubo PVC Hidra 1'' Ced 40 Blanco' where CodigoBarrasNuevo='7506240648802';
update inventario_wip set CostoUnidadTruper=CostoPaqueteTruper/NumeroUnidades, sugeridoUnidadTruper=sugeridoPaqueteTruper/NumeroUnidades
where CodigoBarrasNuevo='7506240648802';
update inventario_wip set PrecioComparacion=Precio-sugeridoUnidadTruper,  CostoComparacion=Costo-CostoUnidadTruper where CodigoBarras='TUBOPVC1PULHIDRA';
update inventario_wip set CostoEs='paquete', PrecioEs='paquete' where CodigoBarras='TUBOPVC1PUL';

-- ART 27 - ONE IS UNIT ONE IS PACKAGE BUT HAS NO NUMBER OF UNITS;
-- select * FROM catalogo_truper ct  where codigo=41271;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240652014';
-- select * FROM inventario_wip where CodigoBarras='41271';
-- select * FROM inventario_wip where codigoNumericoNuevo =41271;
update inventario_wip set UnidadInv='metro', NumeroUnidades=3, CostoPaqueteTruper=CostoUnidadTruper, sugeridoPaqueteTruper=sugeridoUnidadTruper where CodigoBarrasNuevo='7506240652014';
update inventario_wip set descripcionLimpia ='Tubo Cobre Tipo L, 1/2'' (gas)' where CodigoBarrasNuevo='7506240652014';
update inventario_wip set CostoUnidadTruper=CostoPaqueteTruper/NumeroUnidades, sugeridoUnidadTruper=sugeridoPaqueteTruper/NumeroUnidades where CodigoBarrasNuevo='7506240652014';
update inventario_wip set PrecioComparacion=Precio-sugeridoUnidadTruper,  CostoComparacion=Costo-CostoUnidadTruper where CodigoBarras='TUBO COBRE GAS 1/2';
update inventario_wip set CostoEs='paquete', PrecioEs='paquete' where CodigoBarras='TUBOGAS1/2RIGIDO';

-- ART 28 - ONE IS UNIT ONE IS PACKAGE BUT HAS NO NUMBER OF UNITS ******* revisar precio por metro que esta muy bajo *********;
-- select * FROM catalogo_truper ct  where codigo=41274;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240652069';
-- select * FROM inventario_wip where CodigoBarras='41274';
-- select * FROM inventario_wip where codigoNumericoNuevo =41274;
update inventario_wip set UnidadInv='metro', NumeroUnidades=3, CostoPaqueteTruper=CostoUnidadTruper, sugeridoPaqueteTruper=sugeridoUnidadTruper where CodigoBarrasNuevo='7506240652069';
update inventario_wip set descripcionLimpia ='Tubo Cobre Tipo M, 1/2' where CodigoBarrasNuevo='7506240652069';
update inventario_wip set CostoUnidadTruper=CostoPaqueteTruper/NumeroUnidades, sugeridoUnidadTruper=sugeridoPaqueteTruper/NumeroUnidades where CodigoBarrasNuevo='7506240652069';
update inventario_wip set PrecioComparacion=Precio-sugeridoUnidadTruper,  CostoComparacion=Costo-CostoUnidadTruper where CodigoBarras='TUBO COBRE1/2M';
update inventario_wip set CostoEs='paquete', PrecioEs='paquete' where CodigoBarras='9022345250';

-- ART 29 - ONE IS UNIT ONE IS PACKAGE BUT HAS NO NUMBER OF UNITS ;
-- select * FROM catalogo_truper ct  where codigo=41275;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240652076';
-- select * FROM inventario_wip where CodigoBarras='41275';
-- select * FROM inventario_wip where codigoNumericoNuevo =41275;
update inventario_wip set UnidadInv='metro', NumeroUnidades=3, CostoPaqueteTruper=CostoUnidadTruper, sugeridoPaqueteTruper=sugeridoUnidadTruper where CodigoBarrasNuevo='7506240652076';
update inventario_wip set descripcionLimpia ='Tubo Cobre Tipo M, 3/4' where CodigoBarrasNuevo='7506240652076';
update inventario_wip set CostoUnidadTruper=CostoPaqueteTruper/NumeroUnidades, sugeridoUnidadTruper=sugeridoPaqueteTruper/NumeroUnidades where CodigoBarrasNuevo='7506240652076';
update inventario_wip set PrecioComparacion=Precio-sugeridoUnidadTruper,  CostoComparacion=Costo-CostoUnidadTruper where CodigoBarras='TUBOCOBRE3/4M';
update inventario_wip set CostoEs='paquete', PrecioEs='paquete' where CodigoBarras='TUBOCOBRE3/4TIPOM';

-- ART 30 - BARCODES ARE WRONG, IT'S NOT THE SAME PRODUCT;

-- select * FROM catalogo_truper ct  where codigo=41983;			-- VERIFIED	Esfera	59	93	7506240654544
-- select * FROM catalogo_truper ct  where codigo=41980;			-- VERIFIED	Globo 115 179	7506240654513

-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240654544';
-- select * FROM inventario_wip where CodigoBarras='41275';
-- select * FROM inventario_wip where codigoNumericoNuevo =41275;

-- select * FROM inventario_wip where CodigoBarrasNuevo in ('7506240654544','7506240654513')

UPDATE inventario_wip SET CodigoBarras='7506240654513', CodigoBarrasNuevo='7506240654513', CodigoNumericoNuevo=41980 where CodigoBarras ='7506240654544';
update inventario_wip set costoUnidadTruper=115, sugeridoUnidadTruper=179 where codigoBarrasNuevo ='7506240654513';

-- ART 31 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=45539;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240656753';
-- select * FROM inventario_wip where CodigoBarras='45539';
-- select * FROM inventario_wip where codigoNumericoNuevo =45539;
update inventario_wip set activo=0 where CodigoBarras ='45539';
update inventario_wip set inventario =7 where CodigoBarras ='7506240656753';


-- ART 32 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=45540;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240656760';
-- select * FROM inventario_wip where CodigoBarras='45540';
-- select * FROM inventario_wip where codigoNumericoNuevo =45540;
update inventario_wip set activo=0 where CodigoBarras ='45540';

-- ART 33 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=45541;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240656777';
-- select * FROM inventario_wip where CodigoBarras='45541';
-- select * FROM inventario_wip where codigoNumericoNuevo =45541;
update inventario_wip set activo=0 where CodigoBarras ='45541';
update inventario_wip set inventario =28 where CodigoBarras ='7506240656777';


-- ART 33 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48721;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240663676';
-- select * FROM inventario_wip where CodigoBarras='48721';
-- select * FROM inventario_wip where codigoNumericoNuevo =48721;
update inventario_wip set activo=0 where CodigoBarras ='7506240663676';
update inventario_wip set inventario =120 where CodigoBarras ='PIJALAMINA6X1';

-- ART 34 - - ONE IS UNIT ONE IS PACKAGE BUT HAS NO NUMBER OF UNITS ******* revisar precio por metro que esta muy bajo *********;
-- select * FROM catalogo_truper ct  where codigo=48151;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240665960';
-- select * FROM inventario_wip where CodigoBarras='48151';
-- select * FROM inventario_wip where codigoNumericoNuevo =48151;
update inventario_wip set UnidadInv='metro', NumeroUnidades=3, CostoPaqueteTruper=CostoUnidadTruper, sugeridoPaqueteTruper=sugeridoUnidadTruper where CodigoBarrasNuevo='7506240665960';
update inventario_wip set descripcionLimpia ='Tubo Cobre Tipo N, 1/2' where CodigoBarrasNuevo='7506240665960';
update inventario_wip set CostoUnidadTruper=CostoPaqueteTruper/NumeroUnidades, sugeridoUnidadTruper=sugeridoPaqueteTruper/NumeroUnidades where CodigoBarrasNuevo='7506240665960';
update inventario_wip set PrecioComparacion=Precio-sugeridoUnidadTruper,  CostoComparacion=Costo-CostoUnidadTruper where CodigoBarras='TUBO48151';
update inventario_wip set CostoEs='paquete', PrecioEs='paquete' where CodigoBarras='48151';

-- ART 35 - ONE IS UNIT ONE IS PACKAGE BUT HAS NO NUMBER OF UNITS ;
-- select * FROM catalogo_truper ct  where codigo=48152;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240665977';
-- select * FROM inventario_wip where CodigoBarras='48152';
-- select * FROM inventario_wip where codigoNumericoNuevo =48152;
update inventario_wip set UnidadInv='metro', NumeroUnidades=3, CostoPaqueteTruper=CostoUnidadTruper, sugeridoPaqueteTruper=sugeridoUnidadTruper where CodigoBarrasNuevo='7506240665977';
update inventario_wip set descripcionLimpia ='Tubo Cobre Tipo N, 3/4' where CodigoBarrasNuevo='7506240665977';
update inventario_wip set CostoUnidadTruper=CostoPaqueteTruper/NumeroUnidades, sugeridoUnidadTruper=sugeridoPaqueteTruper/NumeroUnidades where CodigoBarrasNuevo='7506240665977';
update inventario_wip set PrecioComparacion=Precio-sugeridoUnidadTruper,  CostoComparacion=Costo-CostoUnidadTruper where CodigoBarras='TUBOCOMBREM3/4';
update inventario_wip set CostoEs='paquete', PrecioEs='paquete' where CodigoBarras='TUBOCOBRE3/4TIPON';

-- ART 36 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48584;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668206';
-- select * FROM inventario_wip where CodigoBarras='48584';
-- select * FROM inventario_wip where codigoNumericoNuevo =48584;
update inventario_wip set activo=0 where CodigoBarras ='48584';

-- ART 37 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48580;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668244';
-- select * FROM inventario_wip where CodigoBarras='48580';
-- select * FROM inventario_wip where codigoNumericoNuevo =48580;
update inventario_wip set activo=0 where CodigoBarras ='48580';

-- ART 38 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48577;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668275';
-- select * FROM inventario_wip where CodigoBarras='48577';
-- select * FROM inventario_wip where codigoNumericoNuevo =48577;
update inventario_wip set activo=0 where CodigoBarras ='48577';

-- ART 39 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48576;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668282';
-- select * FROM inventario_wip where CodigoBarras='48576';
-- select * FROM inventario_wip where codigoNumericoNuevo =48576;
update inventario_wip set activo=0 where CodigoBarras ='48576';

-- ART 40 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48574;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668305';
-- select * FROM inventario_wip where CodigoBarras='48574';
-- select * FROM inventario_wip where codigoNumericoNuevo =48574;
update inventario_wip set activo=0 where CodigoBarras ='48574';
update inventario_wip set inventario =5 where CodigoBarras ='7506240668305';

-- ART 41 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48573;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668312';
-- select * FROM inventario_wip where CodigoBarras='48573';
-- select * FROM inventario_wip where codigoNumericoNuevo =48573;
update inventario_wip set activo=0 where CodigoBarras ='48573';

-- ART 42 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48572;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668329';
-- select * FROM inventario_wip where CodigoBarras='48572';
-- select * FROM inventario_wip where codigoNumericoNuevo =48572;
update inventario_wip set activo=0 where CodigoBarras ='48572';

-- ART 43 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48570;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668343';
-- select * FROM inventario_wip where CodigoBarras='48570';
-- select * FROM inventario_wip where codigoNumericoNuevo =48570;
update inventario_wip set activo=0 where CodigoBarras ='48570';

-- ART 44 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48569;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668350';
-- select * FROM inventario_wip where CodigoBarras='48569';
-- select * FROM inventario_wip where codigoNumericoNuevo =48569;
update inventario_wip set activo=0 where CodigoBarras ='7506240668350';
update inventario_wip set inventario = 8 where CodigoBarras ='48569';


-- ART 45 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48568;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668367';
-- select * FROM inventario_wip where CodigoBarras='48568';
-- select * FROM inventario_wip where codigoNumericoNuevo =48568;
update inventario_wip set activo=0 where CodigoBarras ='48568';

-- ART 46 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48567;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668374';
-- select * FROM inventario_wip where CodigoBarras='48567';
-- select * FROM inventario_wip where codigoNumericoNuevo =48567;
update inventario_wip set activo=0 where CodigoBarras ='7506240668374';
update inventario_wip set inventario = 8 where CodigoBarras ='48567';


-- ART 47 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48563;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668411';
-- select * FROM inventario_wip where CodigoBarras='48563';
-- select * FROM inventario_wip where codigoNumericoNuevo =48563;
update inventario_wip set activo=0 where CodigoBarras ='48563';
update inventario_wip set inventario =16 where CodigoBarras ='7506240668411';


-- ART 48 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48562;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668428';
-- select * FROM inventario_wip where CodigoBarras='48562';
-- select * FROM inventario_wip where codigoNumericoNuevo =48562;
update inventario_wip set activo=0 where CodigoBarras ='48562';

-- ART 49 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48561;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668435';
-- select * FROM inventario_wip where CodigoBarras='48561';
-- select * FROM inventario_wip where codigoNumericoNuevo =48561;
update inventario_wip set activo=0 where CodigoBarras ='48561';

-- ART 50 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=48558;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668466';
-- select * FROM inventario_wip where CodigoBarras='48558';
-- select * FROM inventario_wip where codigoNumericoNuevo =48558;
update inventario_wip set activo=0 where CodigoBarras ='7506240668466';
update inventario_wip set inventario =8 where CodigoBarras ='48558';


-- ART 51 -- duplicate with wrong price;
-- select * FROM catalogo_truper ct  where codigo=47232;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240668862';
-- select * FROM inventario_wip where CodigoBarras='47232';
-- select * FROM inventario_wip where codigoNumericoNuevo =47232;
update inventario_wip set activo=0 where CodigoBarras ='47232';


-- ART 52 ---------- PREGUNTAR - COSTO METRO ES MENOR QUE COSTO 3 MTS	**************************;
-- select * FROM catalogo_truper ct  where codigo=40094;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240678564';
-- select * FROM inventario_wip where CodigoBarras='40094';
-- select * FROM inventario_wip where codigoNumericoNuevo =40094;
-- ********* -- select * FROM inventario_wip where CodigoBarrasNuevo='7506240678564';
update inventario_wip set descripcionLimpia ='Cuerda De Polipropileno Amarilla No. 8' where codigoBarrasNuevo='7506240678564';

-- ART 53 ---------- PREGUNTAR - COSTO PARECE DE DOS O DE UNIDAD	**************************;
-- select * FROM catalogo_truper ct  where codigo=27241;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506610205611';
-- select * FROM inventario_wip where CodigoBarras='27241';
-- select * FROM inventario_wip where codigoNumericoNuevo =27241;
-- ********* -- select * FROM inventario_wip where CodigoBarrasNuevo='7506610205611';
update inventario_wip set activo=0 where CodigoBarras='7506610205611';
update inventario_wip set descripcionLimpia ='Rodilleras Antiderrapantes Doble Capsula' where CodigoBarrasNuevo='7506610205611';


-- with cod_bars as (
-- 	select CodigoBarras from inventario_wip where activo=1
-- ),
-- cod_bars_in_another as (
-- 	select a.CodigoBarras from cod_bars a, cod_bars b
-- 	where a.CodigoBarras!=b.CodigoBarras and length(a.CodigoBarras)>4 and length(b.CodigoBarras)>4
-- 	and charindex(lower(a.CodigoBarras), lower(b.CodigoBarras) )>0
-- 	UNION 
-- 	select b.CodigoBarras from cod_bars a, cod_bars b
-- 	where a.CodigoBarras!=b.CodigoBarras and length(a.CodigoBarras)>4 and length(b.CodigoBarras)>4
-- 	and charindex(lower(a.CodigoBarras), lower(b.CodigoBarras) )>0
-- 	UNION 
-- 	select a.CodigoBarras from cod_bars a, cod_bars b
-- 	where a.CodigoBarras!=b.CodigoBarras and length(a.CodigoBarras)>4 and length(b.CodigoBarras)>4
-- 	and charindex(lower(b.CodigoBarras), lower(a.CodigoBarras) )>0
-- 	UNION
-- 	select b.CodigoBarras from cod_bars a, cod_bars b
-- 	where a.CodigoBarras!=b.CodigoBarras and length(a.CodigoBarras)>4 and length(b.CodigoBarras)>4
-- 	and charindex(lower(b.CodigoBarras), lower(a.CodigoBarras) )>0
-- )
-- select CodigoBarras, activo, CodigoBarrasNuevo, CodigosBuscar, CodigosBuscarNuevo, Costo, Precio,  Descripcion, DescripcionLimpia, 	DescripcionTruper, Unidad, UnidadInv, PesoKg, 
-- NumeroUnidades, Costo, CostoUnidadTruper, CostoPaqueteTruper, CostoComparacion, CostoEs, Precio, sugeridoUnidadTruper, sugeridoPaqueteTruper,  PrecioComparacion, PrecioEs
-- from inventario_wip where CodigoBarras in (
-- 	select distinct CodigoBarras from cod_bars_in_another
-- --order by 2 desc
-- ) and (CodigoBarras not in ('44560','7501206644560')
-- 	 and CodigoBarrasNuevo not in ('7501206622735')
-- 	)
-- and CodigoBarras like '%7501206647523%'
-- order by 3, 1, 7
-- --LIMIT 2
-- select distinct UnidadInv from inventario_wip iw 

-- ART 1;
-- select * FROM catalogo_truper ct  where codigo=13420;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo like '%7501206647523%';
-- select * FROM inventario_wip where CodigoBarras='BB 7501206647523';
-- select * FROM inventario_wip where codigoNumericoNuevo =13420;
update inventario_wip set activo=0 where CodigoBarras ='BB 7501206647523';

-- ART 2;
-- select * FROM catalogo_truper ct  where codigo=13420;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7502242342205';
-- select * FROM inventario_wip where CodigoBarras like '%7502242342205%';
-- select * FROM inventario_wip where codigoNumericoNuevo =13420;
UPDATE inventario_wip SET costoes='unidad', precioes='unidad' WHERE CodigoBarras IN ('7502242342205MOSCA');
UPDATE inventario_wip SET costoes='paquete', precioes='paquete' WHERE CodigoBarras IN ('7502242342205');
UPDATE inventario_wip SET CodigoBarras='7502242342205', CodigoBarrasNuevo='7502242342205', UnidadInv='pieza', NumeroUnidades=4 WHERE CodigoBarras IN ('7502242342205MOSCA', '7502242342205');
update inventario_wip set descripcionLimpia ='Atrapa Moscas Fly Kill' where CodigoBarras IN ('7502242342205MOSCA', '7502242342205');
-- ********* -- select * from inventario_wip where CodigoBarras='7502242342205';

-- ART 3;
			-- VERIFIED
--select * from inventario_wip where CodigoBarras like '%ESCOBA%';
update inventario_wip set activo=0 where CodigoBarras ='PALOESCOBAMADERA';

-- ART 4 ---- PREGUNTAR POR METRO Y ROLLO;	-- dejar los dos ********************************************************************************
-- select * FROM catalogo_truper ct  where codigo=44884;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240637295';
-- select * FROM inventario_wip where CodigoBarras='7506240637295';
-- select * FROM inventario_wip where codigoNumericoNuevo =44884;
-- ********* -- select * FROM inventario_wip where CodigoBarras IN ('ALAMBREPUAS','ALAMBREPUASPOROLLO');

-- ART 5 ---- PREGUNTAR POR bulto y kilo;

-- ********* -- select * FROM inventario_wip where CodigoBarras IN ('ARENA','ARENASUELTA');   ***********************************************
update inventario_wip set codigoBarrasNuevo='ARENA' where  CodigoBarras IN ('ARENA','ARENASUELTA');


-- art 6 - AGREGUE CODIGO CORRECT PARA REPROCESAR Niple Galvanizado 1/2 Por 3 - 7506240627203;
-- select * FROM catalogo_truper ct  where codigo=47517;			-- VERIFIED
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240627203';
-- select * FROM inventario_wip where CodigoBarras='7506240627203';
-- select * FROM inventario_wip where codigoNumericoNuevo =47517;
--select * FROM inventario_wip where Descripcion='Niple Galvanizado 1/2 Por 3';
--select * FROM inventario_wip where CodigoBarras='NIPLEGALVANIZADO1/2';
update inventario_wip set activo=0 where CodigoBarras ='NIPLEGALVANIZADO1/2';

-- art 7 fixed and also para reprocesar;
-- select * FROM inventario_wip where CodigoBarras like '%TUBOCPVC1/2%';
-- select * FROM inventario_wip where CodigoBarrasNuevo='7506240646563';	-- VERIFIED

UPDATE inventario_wip SET costoes='unidad', precioes='unidad' WHERE CodigoBarras IN ('TUBOCPVC1/2PORMETRO');
UPDATE inventario_wip SET costoes='paquete', precioes='paquete', CodigosBuscarNuevo='45042'  WHERE CodigoBarras IN ('TUBOCPVC1/2');
UPDATE inventario_wip SET CodigoBarras='7506240646563', CodigoBarrasNuevo='7506240646563', UnidadInv='metro', NumeroUnidades='3' WHERE CodigoBarras IN ('TUBOCPVC1/2PORMETRO', 'TUBOCPVC1/2');
update inventario_wip  set descripcionLimpia ='Tubo CPVC 1/2 Café' where CodigoBarrasNuevo='7506240646563';
update inventario_wip set proveedor='Truper', codigoNumerico=45042, codigoNumericoNuevo=45042,  codigosBuscarNuevo=''  where codigoBarrasNuevo ='7506240646563' and codigosBuscarNuevo='45042';
-- ********* -- select * from inventario_wip where CodigoBarras='7506240646563';

-- ART 8 PREGYUNTAR CEMENTOS EN EXCEL CUAL ES DE QUE BULTO Y CUANTOS KILOS TIENE EL BULTO;			************************************************
-- select * from inventario_wip where codigoBarras like '%cemen%' and proveedor='' order by descripcion   


--select * from inventario_wip where codigoBarrasNuevo ='7506240668459'


update inventario_wip set activo=0 where codigoBarras='7506240668459';
update inventario_wip set descripcionLimpia=descripcionTruperInv  where codigoBarrasNuevo='7506240668459';

--------------------------------------------- HASTA AQUI YA WSTA TODO ACTUALIZADO --------- ********************************************************

-- DESPUES DE ANALISIS


-- --------------------------------
-- UPDATE inventario_wip SET Costo=65, Precio=105, Inventario=200, PrecioEs='paquete', CostoEs='paquete', SeCompraPor='paquete', 
-- CostoPaquete=65,  CostoPaqueteSinIva=round(65/1.16,2), 
-- CostoUnidad=round(65*1.00/NumeroUnidades,2), CostoUnidadSinIva = round((65/1.16)/NumeroUnidades,2),
-- PrecioPaquete=105, PrecioUnidad=round(105*1.0/NumeroUnidades,2) 										where CodigoBarrasNuevo ='7506240603122';

-- UPDATE inventario_wip SET Costo=25, PrecioEs='paquete', CostoEs='paquete', SeCompraPor='paquete', 
-- CostoPaquete=25, CostoPaqueteSinIva=round(25/1.16,2), 
-- CostoUnidad=round(25*1.00/NumeroUnidades,2), CostoUnidadSinIva = round((25/1.16)/NumeroUnidades,2),
-- PrecioPaquete=Precio, PrecioUnidad=round(Precio*1.0/NumeroUnidades,2) 										where CodigoBarrasNuevo ='7501206618059';
	
-- UPDATE inventario_wip SET Costo=25, Precio=42, PrecioEs='paquete', CostoEs='paquete', SeCompraPor='paquete', 
-- CostoPaquete=25, CostoPaqueteSinIva=round(25/1.16,2), 
-- CostoUnidad=round(25*1.00/NumeroUnidades,2), CostoUnidadSinIva = round((25/1.16)/NumeroUnidades,2),
-- PrecioPaquete=42, PrecioUnidad=round(42*1.0/NumeroUnidades,2) 										where CodigoBarrasNuevo ='7501206662694';

-- UPDATE inventario_wip SET Costo=22, Precio=32, PrecioEs='paquete', CostoEs='paquete', SeCompraPor='paquete', 
-- CostoPaquete=22, CostoPaqueteSinIva=round(22/1.16,2), 
-- CostoUnidad=round(22*1.00/NumeroUnidades,2), CostoUnidadSinIva = round((22/1.16)/NumeroUnidades,2),
-- PrecioPaquete=32, PrecioUnidad=round(32*1.0/NumeroUnidades,2) 										where CodigoBarrasNuevo ='7506240602989';

-- UPDATE inventario_wip SET Costo=18, Precio=28, PrecioEs='paquete', CostoEs='paquete', SeCompraPor='paquete', 
-- CostoPaquete=18, CostoPaqueteSinIva=round(18/1.16,2), 
-- CostoUnidad=round(18*1.00/NumeroUnidades,2), CostoUnidadSinIva = round((18/1.16)/NumeroUnidades,2),
-- PrecioPaquete=28, PrecioUnidad=round(28*1.0/NumeroUnidades,2) 										where CodigoBarrasNuevo ='7506240609445';

-- UPDATE inventario_wip SET Costo=19, PrecioEs='paquete', CostoEs='paquete', SeCompraPor='paquete', 
-- CostoPaquete=19, CostoPaqueteSinIva=round(19/1.16,2), 
-- CostoUnidad=round(19*1.00/NumeroUnidades,2), CostoUnidadSinIva = round((19/1.16)/NumeroUnidades,2),
-- PrecioPaquete=Precio, PrecioUnidad=round(Precio*1.0/NumeroUnidades,2) 										where CodigoBarrasNuevo ='7506240663584';


-- UPDATE inventario_wip SET Costo=27, Precio=42, PrecioEs='paquete', CostoEs='paquete', SeCompraPor='paquete', SeVendePor='paquete', PreferenciaVenta='paquete',
-- CostoPaquete=27, CostoPaqueteSinIva=round(27/1.16,2), 
-- CostoUnidad=round(27*1.00/NumeroUnidades,2), CostoUnidadSinIva = round((27/1.16)/NumeroUnidades,2),
-- PrecioPaquete=42, PrecioUnidad=round(42*1.0/NumeroUnidades,2) 										where CodigoBarrasNuevo ='7506240667957';
