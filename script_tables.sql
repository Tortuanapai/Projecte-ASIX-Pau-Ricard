BEGIN;

CREATE TABLE usuaris (
id SERIAL PRIMARY KEY,
usuario VARCHAR(50) UNIQUE NOT NULL,
password_hash TEXT NOT NULL,
nom_rol VARCHAR(50) NOT NULL CHECK (nom_rol IN ('Administrador', 'Metge', 'Infermer', 'Personal Vari')),
id_treballador INTEGER UNIQUE
);

CREATE TABLE usuaris_pendents (
id SERIAL PRIMARY KEY,
usuario VARCHAR(50) UNIQUE NOT NULL,
password_hash TEXT NOT NULL,
nom_rol VARCHAR(50) NOT NULL CHECK (nom_rol IN ('Administrador', 'Metge', 'Infermer', 'Personal Vari')),
data_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE planta (
id_planta SERIAL PRIMARY KEY,
nom_planta VARCHAR(50) NOT NULL UNIQUE CHECK (nom_planta IN ('Primera', 'Segona', 'Tercera', 'Quarta')),
ubicacio VARCHAR(100) NOT NULL,
estat_actual VARCHAR(50) NOT NULL
);

CREATE TABLE habitacio (
id_habitacio SERIAL PRIMARY KEY,
tamany VARCHAR(20) NOT NULL CHECK (tamany IN ('Individual', 'Doble', 'Suite')),
ubicacio VARCHAR(50) NOT NULL,
estat VARCHAR(50) NOT NULL CHECK (estat IN ('Lliure', 'Ocupada', 'Neteja', 'Manteniment')),
id_planta INTEGER NOT NULL,
CONSTRAINT fk_planta FOREIGN KEY (id_planta) REFERENCES planta(id_planta)
);

CREATE TABLE quirofan (
id_quirofan SERIAL PRIMARY KEY,
codi_quirofan VARCHAR(10) NOT NULL,
id_planta INTEGER NOT NULL,
CONSTRAINT fk_planta_quirofan FOREIGN KEY (id_planta) REFERENCES planta(id_planta)
);

CREATE TABLE aparell (
id_aparell SERIAL PRIMARY KEY,
nom_aparell VARCHAR(100) NOT NULL,
marca VARCHAR(50) NOT NULL,
model VARCHAR(50) NOT NULL,
descripcio TEXT
);

CREATE TABLE quirofan_aparell (
id_quirofan INTEGER,
id_aparell INTEGER,
quantitat INTEGER NOT NULL CHECK (quantitat > 0),
CONSTRAINT pk_quirofan_aparell PRIMARY KEY (id_quirofan, id_aparell),
CONSTRAINT fk_quirofan FOREIGN KEY (id_quirofan) REFERENCES quirofan(id_quirofan),
CONSTRAINT fk_aparell FOREIGN KEY (id_aparell) REFERENCES aparell(id_aparell)
);

CREATE TABLE treballador (
id_treballador SERIAL PRIMARY KEY,
nif VARCHAR(20) UNIQUE NOT NULL,
nom VARCHAR(50) NOT NULL CHECK (nom = INITCAP(nom)),
primer_cognom VARCHAR(50) NOT NULL CHECK (LEFT(primer_cognom, 1) = UPPER(LEFT(primer_cognom, 1))),
segon_cognom VARCHAR(50) NOT NULL CHECK (LEFT(segon_cognom, 1) = UPPER(LEFT(segon_cognom, 1))),
adreça VARCHAR(100),
telefon NUMERIC(15) NOT NULL,
observacions TEXT
);

CREATE TABLE metge (
id_treballador INTEGER PRIMARY KEY,
especialitat VARCHAR(100) NOT NULL,
torn VARCHAR(20) NOT NULL CHECK (torn IN ('Matí', 'Tarda', 'Nit')),
estudis TEXT NOT NULL,
curriculum TEXT NOT NULL,
CONSTRAINT fk_treballador_metge FOREIGN KEY (id_treballador) REFERENCES treballador(id_treballador)
);

CREATE TABLE infermeria (
id_treballador INTEGER PRIMARY KEY,
torn VARCHAR(20) NOT NULL CHECK (torn IN ('Matí', 'Tarda', 'Nit')),
estudis TEXT NOT NULL,
curriculum TEXT NOT NULL,
id_metge INTEGER,
id_planta INTEGER,
CONSTRAINT fk_treballador_infermeria FOREIGN KEY (id_treballador) REFERENCES treballador(id_treballador),
CONSTRAINT fk_metge_assignat FOREIGN KEY (id_metge) REFERENCES metge(id_treballador),
CONSTRAINT fk_planta_assignada FOREIGN KEY (id_planta) REFERENCES planta(id_planta)
);

CREATE TABLE personal_vari (
id_treballador INTEGER PRIMARY KEY,
tipus_feina VARCHAR(50) NOT NULL,
descripcio TEXT,
CONSTRAINT fk_treballador_vari FOREIGN KEY (id_treballador) REFERENCES treballador(id_treballador)
);

CREATE TABLE pacient (
id_pacient SERIAL PRIMARY KEY,
nom VARCHAR(100) NOT NULL CHECK (nom = INITCAP(nom)),
nss VARCHAR(15) UNIQUE NOT NULL,
adreça VARCHAR(100),
descripcio TEXT
);

CREATE TABLE medicament (
id_medicament SERIAL PRIMARY KEY,
nom_comercial VARCHAR(100) NOT NULL UNIQUE,
principi_actiu VARCHAR(100) NOT NULL
);

CREATE TABLE diagnostic (
id_diagnostic SERIAL PRIMARY KEY,
nom_malaltia VARCHAR(100) NOT NULL UNIQUE,
descripcio TEXT,
observacions TEXT
);

CREATE TABLE visita (
id_visita SERIAL PRIMARY KEY,
dia_visita DATE NOT NULL DEFAULT CURRENT_DATE,
hora_visita TIME NOT NULL,
observacions TEXT,
id_metge INTEGER NOT NULL,
id_pacient INTEGER NOT NULL,
CONSTRAINT fk_metge_visita FOREIGN KEY (id_metge) REFERENCES metge(id_treballador),
CONSTRAINT fk_pacient_visita FOREIGN KEY (id_pacient) REFERENCES pacient(id_pacient)
);

CREATE TABLE visita_medicament (
id_visita INTEGER,
id_medicament INTEGER,
dosis VARCHAR(50) NOT NULL,
pauta TEXT NOT NULL,
CONSTRAINT pk_visita_med PRIMARY KEY (id_visita, id_medicament),
CONSTRAINT fk_visita FOREIGN KEY (id_visita) REFERENCES visita(id_visita),
CONSTRAINT fk_medicament FOREIGN KEY (id_medicament) REFERENCES medicament(id_medicament)
);

CREATE TABLE visita_diagnostic (
id_visita INTEGER,
id_diagnostic INTEGER,
CONSTRAINT pk_visita_diag PRIMARY KEY (id_visita, id_diagnostic),
CONSTRAINT fk_visita_diag FOREIGN KEY (id_visita) REFERENCES visita(id_visita),
CONSTRAINT fk_diagnostic FOREIGN KEY (id_diagnostic) REFERENCES diagnostic(id_diagnostic)
);

CREATE TABLE reserva_habitacio (
id_reserva SERIAL PRIMARY KEY,
data_ingres_previst DATE NOT NULL,
data_sortida_prevista DATE,
id_pacient INTEGER NOT NULL,
id_habitacio INTEGER NOT NULL,
CONSTRAINT fk_pacient_reserva FOREIGN KEY (id_pacient) REFERENCES pacient(id_pacient),
CONSTRAINT fk_habitacio_reserva FOREIGN KEY (id_habitacio) REFERENCES habitacio(id_habitacio)
);

CREATE TABLE operacio (
id_operacio SERIAL PRIMARY KEY,
dia_operacio DATE NOT NULL,
hora_operacio TIME NOT NULL,
id_metge INTEGER NOT NULL,
id_pacient INTEGER NOT NULL,
id_quirofan INTEGER NOT NULL,
CONSTRAINT fk_metge_op FOREIGN KEY (id_metge) REFERENCES metge(id_treballador),
CONSTRAINT fk_pacient_op FOREIGN KEY (id_pacient) REFERENCES pacient(id_pacient),
CONSTRAINT fk_quirofan_op FOREIGN KEY (id_quirofan) REFERENCES quirofan(id_quirofan)
);

CREATE TABLE assistencia_operacio (
id_operacio INTEGER,
id_infermer INTEGER,
CONSTRAINT pk_assistencia PRIMARY KEY (id_operacio, id_infermer),
CONSTRAINT fk_operacio FOREIGN KEY (id_operacio) REFERENCES operacio(id_operacio),
CONSTRAINT fk_infermer FOREIGN KEY (id_infermer) REFERENCES infermeria(id_treballador)
);

COMMIT;