INSERT INTO specializacije (id, opis) VALUES (-1, 'nefrologija');

INSERT INTO specializacije (id, opis) VALUES (-2, 'pulmologija');

INSERT INTO specializacije (id, opis) VALUES (-3, 'dermatologija');

INSERT INTO specializacije (id, opis) VALUES (-4, 'nevrologija');

INSERT INTO specializacije (id, opis) VALUES (-5, 'psihiatrija');

INSERT INTO
    specializacije (id, opis)
VALUES (-6, 'družinski zdravnik');

INSERT INTO
    zdravnik (
        id,
        ime,
        priimek,
        specializacija
    )
VALUES (1, 'Ana', 'Novak', -1);

INSERT INTO
    zdravnik (
        id,
        ime,
        priimek,
        specializacija
    )
VALUES (2, 'Luka', 'Horvat', -2);

INSERT INTO
    zdravnik (
        id,
        ime,
        priimek,
        specializacija
    )
VALUES (3, 'Nina', 'Kovac', -3);

INSERT INTO
    zdravnik (
        id,
        ime,
        priimek,
        specializacija
    )
VALUES (4, 'Matej', 'Zupan', -4);

INSERT INTO
    zdravnik (
        id,
        ime,
        priimek,
        specializacija
    )
VALUES (5, 'Sara', 'Vidmar', -5);

INSERT INTO
    zdravnik (
        id,
        ime,
        priimek,
        specializacija
    )
VALUES (6, 'Sergej', 'Maze', -6);

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1001,
        'Tina',
        'Pogorelc',
        3981276450
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1002,
        'Miha',
        'Petek',
        7164930285
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1003,
        'Eva',
        'Jereb',
        2548613790
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1004,
        'Alen',
        'Hribar',
        5376924180
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1005,
        'Katja',
        'Rupnik',
        8246731950
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1006,
        'Tina',
        'Pogorelc',
        1904728356
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1007,
        'Andrej',
        'Potocnik',
        3560891247
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1008,
        'Klemen',
        'Bizjak',
        6072958314
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1009,
        'Maja',
        'Kos',
        4783920165
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1010,
        'Gregor',
        'Kralj',
        9230481675
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1011,
        'Jana',
        'Petric',
        1357924680
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1012,
        'Bojan',
        'Strukelj',
        8064519273
    );

INSERT INTO
    pacient (id, ime, priimek, szz)
VALUES (
        1013,
        'Irena',
        'Zore',
        9143827506
    );

-- Diagnoze za pacienta 1001
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '10-ABCD',
        'Prehlad',
        TRUE,
        1001,
        3
    );

INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '45-EFGH',
        'Zvit glezenj',
        FALSE,
        1001,
        1
    );

-- Diagnoze za pacienta 1002
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '27-IJKL',
        'Gripa',
        TRUE,
        1002,
        4
    );

INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '88-MNOP',
        'Povisan krvni tlak',
        FALSE,
        1002,
        2
    );

-- Diagnoze za pacienta 1003
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '62-QRST',
        'Motnje spanja',
        TRUE,
        1003,
        5
    );

-- Diagnoze za pacienta 1004
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '53-UVWX',
        'Prebavne tezave',
        TRUE,
        1004,
        1
    );

INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '71-YZAB',
        'Migrena',
        FALSE,
        1004,
        6
    );

INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '94-CDEF',
        'Sladkorna bolezen',
        TRUE,
        1004,
        3
    );

-- Diagnoze za pacienta 1005
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '09-GHIJ',
        'Hrupno dihanje',
        TRUE,
        1005,
        2
    );

INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '36-KLMN',
        'Bolecine v hrbtu',
        FALSE,
        1005,
        4
    );

-- Diagnoze za pacienta 1006
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '82-OPQR',
        'Anksioznost',
        FALSE,
        1006,
        5
    );

-- Diagnoze za pacienta 1007
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '17-STUV',
        'Astma',
        TRUE,
        1007,
        6
    );

-- Diagnoze za pacienta 1008
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '49-WXYZ',
        'Okuzba secil',
        FALSE,
        1008,
        1
    );

-- Diagnoze za pacienta 1009
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '76-1234',
        'Bolecine v trebuhu',
        TRUE,
        1009,
        4
    );

-- Diagnoze za pacienta 1010
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '28-5678',
        'Tezave s scitnico',
        FALSE,
        1010,
        3
    );

INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '51-90AB',
        'Tezave s spanjem',
        TRUE,
        1010,
        2
    );

-- Diagnoze za pacienta 1011
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '64-CDEF',
        'Depresija',
        TRUE,
        1011,
        5
    );

-- Diagnoze za pacienta 1012
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '93-GHIJ',
        'Glavobol',
        FALSE,
        1012,
        4
    );

INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '12-KLMN',
        'Tezave s sluhom',
        TRUE,
        1012,
        6
    );

-- Diagnoze za pacienta 1013
INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '39-OPQR',
        'Bolecine v sklepih',
        FALSE,
        1013,
        3
    );

INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '85-STUV',
        'Povisana telesna temperatura',
        TRUE,
        1013,
        1
    );

INSERT INTO
    diagnoza (
        koda,
        detajli,
        aktivnost,
        id_pacient,
        id_zdravnik
    )
VALUES (
        '56-WXYZ',
        'Tezave z vidom',
        TRUE,
        1013,
        2
    );

-- Vnosi v tabelo bridge

INSERT INTO
    bridge (id_pacient, id_zdravnik)
VALUES (1001, 1),
    (1001, 4),
    (1002, 3),
    (1002, 6),
    (1003, 1),
    (1003, 4),
    (1004, 3),
    (1004, 6),
    (1005, 1),
    (1005, 6),
    (1006, 4),
    (1006, 6),
    (1007, 1),
    (1007, 3),
    (1008, 1),
    (1008, 4),
    (1009, 3),
    (1009, 6),
    (1010, 1),
    (1010, 4),
    (1011, 3),
    (1011, 6),
    (1012, 1),
    (1012, 4),
    (1013, 1),
    (1013, 6);

-- INSERT INTO uporabnik VALUES
--     ('admin', 'admin', 'admin', '2016-06-22 19:10:25-07');

--naslednja dva ukaza naredimo da imamo admina v bazi
--sicer admina najprej registriramo kot zdravnika, nato pa mu spremenimo role v admin
INSERT INTO zdravnik VALUES (666, 'admin', 'admin', -1);

UPDATE uporabnik SET role = 'admin' WHERE username = 'admin';

--izbriši vse uporabnike iz tabele uporabnik
DELETE FROM uporabnik;

delete from uporabnik WHERE username = 'kati';