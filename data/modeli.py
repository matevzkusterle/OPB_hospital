from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

# Predlagam uporabo (vsaj) dataclass-ov

# Nahitro dataclass doda nekaj bližnjic za delo z razredi in omogoča 
# tudi nekaj bolj naprednih funkcij,
# ki jih načeloma najdemo v bolj tipiziranih jezik kot so C#, Java, C++,..

# Knjižnjica dataclasses_json je nadgradnja za delo z dataclasses
# in omogoča predvsem
# preprosto serializacijo in deseralizacijo objektov.
# Poleg tega vsebuje tudi uporabno funkcijo
# to_dict() in from_dict(), ki dataclas pretvori v/iz slovarja.

@dataclass_json
@dataclass
class uporabnik:
    username: str = field(default="")
    id_zdravnik: int = field(default="")
    id_pacient: int = field(default="")
    role: str = field(default="")
    ime: str = field(default="")
    priimek: str = field(default="")
    password_hash: str = field(default="")
    last_login: str = field(default="")

@dataclass
class uporabnikDto:
    username: str = field(default="")
    role: str = field(default="")



@dataclass_json
@dataclass
class zdravnik:
    id: int = field(default="")
    ime: str = field(default="")
    priimek: str = field(default="")
    specializacija: str = field(default="")



@dataclass_json
@dataclass
class pacient:
    id: int = field(default="")
    ime: str = field(default="")
    priimek: str = field(default="")
    szz: str = field(default="")
    


@dataclass
class pacientDiag:  #pacient skupaj z njegovo diagnozo
    id_diagnoza: int = field(default="")
    id_pacient: int = field(default="")
    ime: str = field(default="")
    priimek: str = field(default="")
    szz: str = field(default="")
    koda: str = field(default="")
    detajli: str = field(default="")
    aktivnost: str = field(default="")

@dataclass_json
@dataclass
class diagnoza:
    id: int = field(default="")
    koda: str = field(default="")
    detajli: str = field(default="")
    aktivnost: str = field(default="")
    id_pacient: int = field(default="")
    id_zdravnik: int = field(default="")

@dataclass
class diagnoza_pacient:
    koda: str = field(default="")
    detajli: str = field(default="")
    aktivnost: str = field(default="")
    ime: str = field(default="")
    priimek: str = field(default="")

@dataclass_json
@dataclass
class specializacije:
    id: int = field(default="")
    opis: str = field(default="")

@dataclass_json
@dataclass
class spec_zdravnik:
    ime: str = field(default="")
    priimek: str = field(default="")
    opis: str = field(default="")

@dataclass_json
@dataclass
class bridge:
    id_zdravnik: int = field(default="")
    id_pacient: int = field(default="")