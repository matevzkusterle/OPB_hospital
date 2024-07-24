
from data.database import Repo
from data.modeli import *
from typing import Dict
from re import sub
import dataclasses
import bcrypt
from typing import Type
from datetime import date
from datetime import datetime

class AuthService:

    repo : Repo
    def __init__(self, repo : Repo):
        
        self.repo = repo

    def obstaja_uporabnik(self, uporabnikk: str) -> bool:
        try:
            user = self.repo.dobi_gen_id(uporabnik, 
                                         uporabnikk, id_col="username")
            return True
        except:
            return False
    
    def preveri_geslo(self, uporabnikk:str, geslo:str):
        user = self.repo.dobi_gen_id(uporabnik, uporabnikk, id_col="username")
        geslo_bytes = geslo.encode('utf-8')
        
     
        return bcrypt.checkpw(geslo_bytes, user.password_hash.encode('utf-8'))
        


    def prijavi_uporabnika(self, 
                           uporabnikk : str,
                           geslo: str) -> uporabnikDto | bool :

        # Najprej dobimo uporabnika iz baze
        user = self.repo.dobi_gen_id(uporabnik, uporabnikk, id_col="username")
        geslo_bytes = geslo.encode('utf-8')
        # Ustvarimo hash iz gesla, ki ga je vnesel uporabnik
        succ = bcrypt.checkpw(geslo_bytes, user.password_hash.encode('utf-8'))
        

        # if uporabnikk == 'admin' and succ:
        #     print('jaa')
        #     print(datetime.now().strftime("%Y-%m-%d %H:%M"))
        #     user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M") 
        #     self.repo.posodobi_gen(user, id_col="username")
        #     return uporabnikDto(
        #         username='admin',
        #         role='admin'
        #     )
        
        if succ:
            # popravimo last login time
            user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M") 
            self.repo.posodobi_gen(user, id_col="username")
            return uporabnikDto(username=user.username, role=user.role)
        
        return False
    

    def dodaj_uporabnika(self,
                         uporabnikk: str,
                         id_zdravnik: int,
                         id_pacient: int,
                         rola: str,
                         ime: str,
                         priimek: str,
                         geslo: str) -> uporabnik:

        # zgradimo hash za geslo od uporabnika

        # Najprej geslo zakodiramo kot seznam bajtov
        bytes = geslo.encode('utf-8')
  
        # Nato ustvarimo salt
        salt = bcrypt.gensalt()
        
        # In na koncu ustvarimo hash gesla
        password_hash = bcrypt.hashpw(bytes, salt)

        # Sedaj ustvarimo objekt uporabnik in ga zapišemo bazo

        uporabnikk = uporabnik(
            username=uporabnikk,
            id_zdravnik=id_zdravnik,
            id_pacient=id_pacient,
            role=rola,
            ime=ime,
            priimek=priimek,
            password_hash=password_hash.decode(),
            last_login= datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        self.repo.dodaj_gen(uporabnikk, serial_col=None)

        return uporabnik(username=uporabnikk,
                         id_zdravnik=id_zdravnik,
                         id_pacient= id_pacient,
                         role=rola, ime=ime, priimek=priimek)