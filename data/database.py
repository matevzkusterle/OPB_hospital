# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os
from typing import List, TypeVar, Type, Callable, Any
from data.modeli import (
    pacient, pacientDiag, zdravnik, uporabnikDto, uporabnik, diagnoza,
    diagnoza_pacient, specializacije, bridge, spec_zdravnik
)
from pandas import DataFrame
from re import sub
import auth_private as auth
from datetime import date
from dataclasses_json import dataclass_json

import dataclasses
# Ustvarimo generično TypeVar spremenljivko. Dovolimo le naše entitene, ki jih imamo tudi v bazi
# kot njene vrednosti. Ko dodamo novo entiteno, jo moramo dodati tudi v to spremenljivko.


DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

T = TypeVar(
    "T",
    pacient,
    pacientDiag,
    zdravnik,    
    uporabnik,
    diagnoza,
    diagnoza_pacient,
    specializacije,
    bridge

    )

class Repo:

    def __init__(self):
        
        # priklopimo se na bazo
        self.conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


    def dobi_gen(self, typ: Type[T], take=10, skip=0) -> List[T]:
        """ 
        Generična metoda, ki za podan vhodni dataclass vrne seznam teh objektov iz baze.
        Predpostavljamo, da je tabeli ime natanko tako kot je ime posameznemu dataclassu.
        """


        # ustvarimo sql select stavek, kjer je ime tabele typ.__name__ oz. ime razreda
        tbl_name = typ.__name__
        
        sql_cmd = f'''SELECT * FROM {tbl_name} LIMIT {take} OFFSET {skip};'''
        self.cur.execute(sql_cmd)
        return [typ.from_dict(d) for d in self.cur.fetchall()]
    
    def dobi_gen_id(self, typ: Type[T], id: int | str, id_col = "id") -> T:
        """
        Generična metoda, ki vrne dataclass objekt pridobljen iz baze na podlagi njegovega idja.
        """
        tbl_name = typ.__name__
        sql_cmd = f'SELECT * FROM {tbl_name} WHERE {id_col} = %s';
        self.cur.execute(sql_cmd, (id,))

        d = self.cur.fetchone()

        if d is None:
            raise Exception(f'Vrstica z id-jem {id} ne obstaja v {tbl_name}');
    
        return typ.from_dict(d)
    
    def dobi_gen_dvoje(self, typ: Type[T], ime: str, priimek: str, prvi = "id", drugi = "id") -> T:
        """
        Generična metoda, ki vrne dataclass objekt pridobljen iz baze na podlagi dveh podatkov.
        """
        tbl_name = typ.__name__
        sql_cmd = f'SELECT * FROM {tbl_name} WHERE {prvi} = %s AND {drugi} = %s';
        self.cur.execute(sql_cmd, (ime, priimek))

        d = self.cur.fetchone()

        if d is None:
            raise Exception(f'Vrstica z imenom {ime} in priimkom {priimek} ne obstaja v {tbl_name}');
    
        return typ.from_dict(d)
    
    def izberi_paciente_zdravnika(self, ime: str, priimek: str) -> List[pacient]:
        """
        Vrne paciente danega zdravnika v seznamu.
        """
        
        self.cur.execute(
            """
            SELECT pacient.* FROM bridge
            JOIN zdravnik ON bridge.id_zdravnik = zdravnik.id
            JOIN pacient ON bridge.id_pacient = pacient.id
            WHERE zdravnik.ime = %s AND zdravnik.priimek = %s
            """,
            (ime, priimek)
            )
        

        pacienti = self.cur.fetchall()

        if pacienti is None:
            raise Exception(f'Vrstica z imenom {ime} in priimkom {priimek} ne obstaja v tabeli pacient');
    
        # return [pacient.from_dict(d) for d in pacienti]
        return [pacient(id, ime, priimek, szz) for (id, ime, priimek, szz) in pacienti]
    
    def izbrisi_gen(self,  typ: Type[T], id: int | str, id_col = "id"):
        """
        Generična metoda, ki vrne dataclass objekt pridobljen iz baze na podlagi njegovega idja.
        """
        tbl_name = typ.__name__
        sql_cmd = f'Delete  FROM {tbl_name} WHERE {id_col} = %s';
        self.cur.execute(sql_cmd, (id,))
        self.conn.commit()

       

    
    def dodaj_gen(self, typ: T, serial_col="id", auto_commit=True):
        """
        Generična metoda, ki v bazo doda entiteto/objekt. V kolikor imamo definiram serial
        stolpec, objektu to vrednost tudi nastavimo. Imena stolpev v bazi morajo biti enaka
        imenom atributov objekta v modeli.py.
        """

        tbl_name = type(typ).__name__
    
        cols =[c.name for c in dataclasses.fields(typ) if c.name != serial_col]
        
        sql_cmd = f'''
        INSERT INTO {tbl_name} ({", ".join(cols)})
        VALUES
        ({self.cur.mogrify(",".join(['%s']*len(cols)), [getattr(typ, c) for c in cols]).decode('utf-8')})
        '''

        if serial_col != None:
            sql_cmd += f'RETURNING {serial_col}'

        self.cur.execute(sql_cmd)

        if serial_col != None:
            serial_val = self.cur.fetchone()[0]

            # Nastavimo vrednost serial stolpca
            setattr(typ, serial_col, serial_val)

        if auto_commit: self.conn.commit()

        # Dobro se je zavedati, da tukaj sam dataclass dejansko
        # "mutiramo" in ne ustvarimo nove reference. Return tukaj ni niti potreben.
      
    def dodaj_gen_list(self, typs: List[T], serial_col="id"):
        """
        Generična metoda, ki v bazo zapiše seznam objekton/entitet. Uporabi funkcijo
        dodaj_gen, le da ustvari samo en commit na koncu.
        """

        if len(typs) == 0: return # nič za narest

        # drugače dobimo tip iz prve vrstice
        typ = typs[0]

        tbl_name = type(typ).__name__

        cols =[c.name for c in dataclasses.fields(typ) if c.name != serial_col]
        sql_cmd = f'''
            INSERT INTO {tbl_name} ({", ".join(cols)})
            VALUES
            {','.join(
                self.cur.mogrify(f'({",".join(["%s"]*len(cols))})', i.to_dict()).decode('utf-8')
                for i in typs
                )}
        '''

        if serial_col != None:
            sql_cmd += f' RETURNING {serial_col};'

        self.cur.execute(sql_cmd)

        if serial_col != None:
            res = self.cur.fetchall()

            for i, d in enumerate(res):
                setattr(typs[i], serial_col, d[0])

        self.conn.commit()



    def posodobi_gen(self, typ: T, id_col = "id", auto_commit=True):
        """
        Generična metoda, ki posodobi objekt v bazi. Predpostavljamo, da je ime pripadajoče tabele
        enako imenu objekta, ter da so atributi objekta direktno vezani na ime stolpcev v tabeli.
        """

        tbl_name = type(typ).__name__
        
        id = getattr(typ, id_col)
        # dobimo vse atribute objekta razen id stolpca
        fields = [c.name for c in dataclasses.fields(typ) if c.name != id_col]

        sql_cmd = f'UPDATE {tbl_name} SET \n ' + \
                    ", \n".join([f'{field} = %s' for field in fields]) +\
                    f'WHERE {id_col} = %s'
        
        # iz objekta naredimo slovar (deluje samo za dataclasses_json)
        d = typ.to_dict()

        # sestavimo seznam parametrov, ki jih potem vsatvimo v sql ukaz
        parameters = [d[field] for field in fields]
        parameters.append(id)

        # izvedemo sql
        self.cur.execute(sql_cmd, parameters)
        if auto_commit: self.conn.commit()
        

    def posodobi_list_gen(self, typs : List[T], id_col = "id"):
        """
        Generična metoda, ki  posodobi seznam entitet(objektov). Uporabimo isti princip
        kot pri posodobi_gen funkciji, le da spremembe commitamo samo enkrat na koncu.
        """
        
        # Posodobimo vsak element seznama, pri čemer sprememb ne comitamo takoj na bazi
        for typ in typs:
            self.posodobi_gen(typ, id_col=id_col, auto_commit=False)

        # Na koncu commitamo vse skupaj
        self.conn.commit()


    def camel_case(self, s):
        """
        Pomožna funkcija, ki podan niz spremeni v camel case zapis.
        """
        
        s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
        return ''.join(s)     

    def col_to_sql(self, col: str, col_type: str, use_camel_case=True, is_key=False):
        """
        Funkcija ustvari del sql stavka za create table na podlagi njegovega imena
        in (python) tipa. Dodatno ga lahko opremimo še z primary key omejitvijo
        ali s serial lastnostjo. Z dodatnimi parametri, bi lahko dodali še dodatne lastnosti.
        """

        # ali stolpce pretvorimo v camel case zapis?
        if use_camel_case:
            col = self.camel_case(col)
        
        match col_type:

            case "int":
                return f'"{col}" BIGINT{" PRIMARY KEY" if  is_key else ""}'
            case "int32":
                return f'"{col}" BIGINT{" PRIMARY KEY" if  is_key else ""}'
         
            case "int64":
                return f'"{col}" BIGINT{" PRIMARY KEY" if  is_key else ""}'
            case "float":
                return f'"{col}" FLOAT'
            case "float32":
                return f'"{col}" FLOAT'
            case "float64":
                return f'"{col}" FLOAT'
        
        # če ni ujemanj stolpec naredimo kar kot text
        return f'"{col}" TEXT{" PRIMARY KEY" if  is_key else ""}'
    
    def df_to_sql_create(self, df: DataFrame, name: str, add_serial=False, use_camel_case=True) -> str:
        """
        Funkcija ustvari in izvede sql stavek za create table na podlagi podanega pandas DataFrame-a. 
        df: DataFrame za katerega zgradimo sql stavek
        name: ime nastale tabele v bazi
        add_serial: opcijski parameter, ki nam pove ali želimo dodat serial primary key stolpec
        """

        # dobimo slovar stolpcev in njihovih tipov
        cols = dict(df.dtypes)

        cols_sql = ""

        # dodamo serial primary key
        if add_serial: cols_sql += 'Id SERIAL PRIMARY KEY,\n'
        
        # dodamo ostale stolpce
        # tukaj bi stolpce lahko še dodatno filtrirali, preimenovali, itd.
        cols_sql += ",\n".join([self.col_to_sql(col, str(typ), use_camel_case=use_camel_case) for col, typ in cols.items()])


        # zgradimo končen sql stavek
        sql = f'''CREATE TABLE IF NOT EXISTS {name}(
            {cols_sql}
        )'''


        self.cur.execute(sql)
        self.conn.commit()
        

    def df_to_sql_insert(self, df:DataFrame, name:str, use_camel_case=True):
        """
        Vnese DataFrame v postgresql bazo. Paziti je treba pri velikosti dataframa,
        saj je sql stavek omejen glede na dolžino. Če je dataframe prevelik, ga je potrebno naložit
        po delih (recimo po 100 vrstic naenkrat), ali pa uporabit bulk_insert.
        df: DataFrame, ki ga želimo prenesti v bazo
        name: Ime tabele kamor želimo shranit podatke
        use_camel_case: ali pretovrimo stolpce v camel case zapis
        """

        cols = list(df.columns)

        # po potrebi pretvorimo imena stolpcev
        if use_camel_case: cols = [self.camel_case(c) for c in cols]

        # ustvarimo sql stavek, ki vnese več vrstic naenkrat
        sql_cmd = f'''INSERT INTO {name} ({", ".join([f'"{c}"' for c in cols])})
            VALUES 
            {','.join(
                self.cur.mogrify(f'({",".join(["%s"]*len(cols))})', i).decode('utf-8')
                for i in df.itertuples(index=False)
                )}
        '''

        # izvedemo ukaz
        self.cur.execute(sql_cmd)
        self.conn.commit()
 


    def zdravnik(self) -> List[zdravnik]:
        self.cur.execute(
            """
            SELECT i.id, i.ime, i.priimek, k.opis FROM "zdravnik" i
            left join specializacije k on i.specializacija = k.id
            """)
        
        zdravnikk = self.cur.fetchall()

        if zdravnikk is None:
            return []
        
        return [zdravnik(id, ime, priimek, opis) for \
                (id, ime, priimek, opis) in zdravnikk]

    def pacientDiag(self) -> List[pacientDiag]: 

        self.cur.execute(
            """
            SELECT i.id, i.ime, i.priimek, i.szz, k.koda, k.detajli, k.aktivnost FROM pacient i
            left join diagnoza k on i.id = k.id_pacient
            """)
        
        pacientt = self.cur.fetchall()
        
        if pacientt is None:
            return []

        return [pacientDiag(id, ime, priimek, szz, koda, detajli, aktivnost) for \
                (id, ime, priimek, szz, koda, detajli, aktivnost) in pacientt]
    
    
    def pacient_to_pacientDiag(self, pacients: List[pacient]) -> List[pacientDiag]:
        pacient_ids = [p.id for p in pacients]
        pacient_ids_str = ', '.join(str(id) for id in pacient_ids)

        self.cur.execute(
            f"""
            SELECT i.id, i.ime, i.priimek, i.szz, k.koda, k.detajli, k.aktivnost FROM pacient i
            LEFT JOIN diagnoza k ON i.id = k.id_pacient
            WHERE i.id IN ({pacient_ids_str})
            """
        )

        pacientDiags = self.cur.fetchall()

        if pacientDiags is None:
            return []

        return [pacientDiag(id, ime, priimek, szz, koda, detajli, aktivnost) for \
                (id, ime, priimek, szz, koda, detajli, aktivnost) in pacientDiags]
    
    def pacient(self) -> List[pacient]:

        self.cur.execute(
            """
            SELECT i.id, i.ime, i.priimek, i.szz FROM pacient i
            """
        )

        pacientt = self.cur.fetchall()

        if pacientt is None:
            return []
        return [pacient(id, ime, priimek, szz) for (id, ime, priimek, szz) in pacientt]
    
    def pacient_dobi_info(self, id: int) -> List[pacient]:
        self.cur.execute(
            """
            SELECT i.id, i.szz, i.ime, i.priimek  FROM pacient i
            WHERE i.id = %s
            """
            , (id,))
        
        pacientt = self.cur.fetchall()

        if pacientt is None:
            return []
        return [pacient(id, ime, priimek, szz) for (id, ime, priimek, szz) in pacientt]

    
    def uporabnik(self) -> List[uporabnik]:
        self.cur.execute(
            """
            SELECT i.username, i.id_zdravnik, i.id_pacient, i.role, i.ime, i.priimek, i.password_hash, i.last_login FROM uporabnik i
            """)
        
        uporabnikk = self.cur.fetchall()

        if uporabnikk is None:
            return []
        return [uporabnik(username, id_zdravnik, id_pacient, role, ime, priimek, password_hash, last_login) for \
                 (username, id_zdravnik, id_pacient, role, ime, priimek, password_hash, last_login) in uporabnikk]
    
    def specializacije(self) -> List[specializacije]:
        self.cur.execute(
            """
            SELECT i.id, i.opis FROM specializacije i
            """)
        
        specializacijee = self.cur.fetchall()

        if specializacijee is None:
            return []
        return [specializacije(id, opis) for \
                 (id, opis) in specializacijee]
    
    def prikazi_diagnoze_pacienta(self, id: int) -> List[diagnoza]:
        self.cur.execute(
            """
            SELECT i.koda, i.detajli, i.aktivnost, k.ime, k.priimek FROM diagnoza i
            LEFT JOIN zdravnik k ON i.id_zdravnik = k.id
            WHERE i.id_pacient = %s
            """
            , (id,))
        
        diagnoze = self.cur.fetchall()

        if diagnoze is None:
            return []
        return [diagnoza_pacient(koda, detajli, aktivnost, ime, priimek) for \
                 (koda, detajli, aktivnost, ime, priimek) in diagnoze]
    
    def specializacija_zdravnik(self, ime: str, priimek: str) -> spec_zdravnik:
        self.cur.execute(
            """
            SELECT i.ime, i.priimek, k.opis FROM zdravnik i
            LEFT JOIN specializacije k ON i.specializacija = k.id
            WHERE i.ime = %s AND i.priimek = %s
            """,
            (ime, priimek)
        )
        
        zdravnik = self.cur.fetchone()

        if zdravnik is None:
            raise ValueError("Zdravnik not found")
        
        return spec_zdravnik(zdravnik[0], zdravnik[1], zdravnik[2])

