-- tipoVentaId meanings:
-- >= -3 : producto en producto
-- -4   : articulo comun → productoReferencia = descripcion
-- -5   : producto pendiente → productoReferencia = codigo de barras
create table ventas (
dispositivoId varchar(20) not null,
productoId INTEGER not null,
tipoVentaId integer,
precio float,
precioVenta float,
cantidad float not null,
subtotal float, 
fechaVenta DATETIME not null,
fechaInventario DATETIME,
extraInfo varchar(255) null,
cancelada boolean,
sinInventario boolean
);
-- CREATE UNIQUE INDEX idx_ventas_natural_key
-- ON ventas (dispositivoId, fechaVenta);