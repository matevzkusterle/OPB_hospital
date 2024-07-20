-- Active: 1708602439218@@baza.fmf.uni-lj.si@5432@sem2024_matevzku@public

CREATE TABLE specializacije (
    id INTEGER PRIMARY KEY,
    opis TEXT NOT NULL
);

CREATE TABLE pacient (
    id INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    szz BIGINT NOT NULL --CHECK (szz >= 1000000000 AND szz <= 9999999999) --szz = 10-mestna stevilka zdravstvenega zavarovanja
);

CREATE TABLE diagnoze (
    koda TEXT PRIMARY KEY,
    detajli TEXT NOT NULL,
    aktivnost BOOLEAN NOT NULL,
    pacient INTEGER NOT NULL REFERENCES pacient(id)
);


CREATE TABLE zdravnik (
    id INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    specializacija INTEGER REFERENCES specializacije(id)
);


CREATE TABLE bridge (
    id_pacient INTEGER,
    id_zdravnik INTEGER,
    povezava BOOLEAN NOT NULL,
    PRIMARY KEY (id_pacient, id_zdravnik)
);


CREATE TABLE uporabnik (
    username TEXT PRIMARY KEY,
    id INTEGER NOT NULL,
    role TEXT NOT NULL,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    last_login TIMESTAMP NOT NULL
);



