CREATE TABLE ajustes (
    variable varchar(20) NOT NULL,
    valor varchar(255) NOT NULL,
    desde DATE NOT NULL,
    PRIMARY KEY (variable, desde)
);