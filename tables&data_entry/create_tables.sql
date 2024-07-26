-- Active: 1708602439218@@baza.fmf.uni-lj.si@5432@sem2024_matevzku@public

CREATE TABLE specializacije (
    id SERIAL PRIMARY KEY,
    opis TEXT NOT NULL
);

CREATE TABLE pacient (
    id SERIAL PRIMARY KEY,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    szz BIGINT NOT NULL --CHECK (szz >= 1000000000 AND szz <= 9999999999) --szz = 10-mestna stevilka zdravstvenega zavarovanja
);

CREATE TABLE diagnoza (
    id SERIAL PRIMARY KEY,
    koda TEXT NOT NULL,
    detajli TEXT NOT NULL,
    aktivnost BOOLEAN NOT NULL,
    id_pacient INTEGER NOT NULL REFERENCES pacient (id)
);

CREATE TABLE zdravnik (
    id SERIAL PRIMARY KEY,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    specializacija INTEGER REFERENCES specializacije (id)
);

CREATE TABLE bridge (
    id_pacient INTEGER,
    id_zdravnik INTEGER,
    PRIMARY KEY (id_pacient, id_zdravnik)
);

CREATE TABLE uporabnik (
    username TEXT PRIMARY KEY,
    id_zdravnik INTEGER REFERENCES zdravnik (id),
    id_pacient INTEGER REFERENCES pacient (id),
    role TEXT NOT NULL,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    last_login TIMESTAMP NOT NULL
);