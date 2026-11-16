create table ventas_detalles (
dispositivoId varchar(20) not null,
fechaVenta DATETIME not null,
total float not null,
tipoPago varchar(1) not null,
pago float not null,
cambio float null,
extraInfo varchar(255) null,
FOREIGN KEY(dispositivoId, fechaVenta) REFERENCES ventas(dispositivoId, fechaVenta)
);

