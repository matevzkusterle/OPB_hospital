# uvozimo bottle.py
from bottleext import (
    get, 
    post, 
    run, 
    request, 
    template, 
    redirect, 
    static_file, 
    url, 
    response, 
    template_user
)
import auth_private as auth_data
from data.database import Repo

# uvozimo ustrezne podatke za povezavo

from data.modeli import *

#za cookieje:
from functools import wraps

from data.services import AuthService
import os

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)


# odkomentiraj, če želiš sporočila o napakah
# debug(True)

repo = Repo()
auth = AuthService(repo)


def cookie_required(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika 
    preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("uporabnik")
        if cookie:
            return f(*args, **kwargs)
        return template("prijava.html",uporabnik=None, rola=None, 
                        napaka="Potrebna je prijava!")   
    return decorated


def zdravnik_required(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika 
    preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie_rola = request.get_cookie("rola")
        if cookie_rola is not None and cookie_rola == 'Zdravnik':
            return f(*args, **kwargs)
        return template("prijava.html",uporabnik=None, rola=None, 
                        napaka="Potrebna je prijava!")
    return decorated

def pacient_required(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika 
    preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie_rola = request.get_cookie("rola")
        if cookie_rola is not None and cookie_rola == 'Pacient':
            return f(*args, **kwargs)
        return template("prijava.html",uporabnik=None, rola=None, 
                        napaka="Potrebna je prijava!")
    return decorated

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')



@get('/')
def index():
    """
    Začetna stran.
    """
    return template('dobrodosli.html', napaka=None)

@get('/prijava')
def prijava():
    return template("prijava.html", napaka=None)

@get('/registracija_zdravnik')
def registracija_zdravnik():

    return template('registracija_zdravnik.html', uporabnik=None, napaka=None)



@post('/registracija_zdravnik')
def registracija_zdravnik():
    """
    Processes the registration of a doctor.
    """
    ime = request.forms.getunicode('ime')
    priimek = request.forms.getunicode('priimek')
    uporabnisko_ime = request.forms.getunicode('username')
    geslo = request.forms.getunicode('password')
    potrditev_gesla = request.forms.getunicode('password2')

    # Preverimo, ali je zdravnik že v bazi
    # zdravniki = repo.dobi_gen(Zdravnik) 
    # print(zdravniki)
    zdravniki = repo.zdravnik()  # Pridobimo seznam zdravnikov iz baze
    existing_doctors = [
    (zdravnik.ime, zdravnik.priimek) 
    for zdravnik in zdravniki
    ]
    uporabniki = repo.uporabnik()
    existing_usernames = [uporabnik.username for uporabnik in uporabniki]
    
    
    
    if uporabnisko_ime in existing_usernames:
        return template('registracija_zdravnik.html', 
                        napaka="Uporabnik s tem uporabnškim imenom že obstaja.")
    
    if not all([ime, priimek, uporabnisko_ime, geslo, potrditev_gesla]):
        return template('registracija_zdravnik.html', 
                        napaka="Prosim, izpolnite vsa polja.")

    if geslo != potrditev_gesla:
        return template('registracija_zdravnik.html', 
                        napaka="Gesli se ne ujemata.")
    
    if (ime, priimek) in existing_doctors:
        nas_zdravnik = repo.dobi_gen_dvoje(
            zdravnik, ime, priimek, prvi="ime", drugi="priimek"
            )
        # Dodamo uporabnika in zdravnika v bazo
        
        auth.dodaj_uporabnika(
            uporabnisko_ime, nas_zdravnik.id, None, 'Zdravnik',
            ime, priimek, geslo=geslo)
        return template('registracija_uspesna.html', napaka = None)
    else:
        return template(
            'registracija_zdravnik.html', 
            napaka=(
                f"Napaka pri registraciji: Imena {ime} {priimek} ni v bazi. "
                f"Za registracijo zdravnika morate biti vnešeni v bazo."
            )
        )



@get('/registracija_pacient')
def registracija_pacient():

    return template('registracija_pacient.html', uporabnik=None, napaka=None)

@post('/registracija_pacient')
def registracija_pacient():
    """
    Processes the registration of a doctor.
    """
    ime = request.forms.get('ime')
    priimek = request.forms.get('priimek')
    szz = request.forms.get('szz')
    uporabnisko_ime = request.forms.get('username')
    geslo = request.forms.get('password')
    potrditev_gesla = request.forms.get('password2')

    pacienti = repo.pacient()  # Pridobimo seznam zdravnikov iz baze
    existing_pacients = [pacient.szz for pacient in pacienti]
    # print(existing_pacients)
    # print(szz)
    # print(szz in existing_pacients)
    uporabniki = repo.uporabnik()
    existing_usernames = [uporabnik.username for uporabnik in uporabniki]

    if uporabnisko_ime in existing_usernames:
        return template('registracija_zdravnik.html', 
                        napaka="Uporabnik s tem uporabnškim imenom že obstaja.")
    # če ne izpolni vseh polj
    if not all([ime, priimek, szz, geslo, uporabnisko_ime, potrditev_gesla]):
        return template('registracija_pacient.html', 
                        napaka="Prosim, izpolnite vsa polja.")

    if geslo != potrditev_gesla:
        return template('registracija_pacient.html', 
                        napaka="Gesli se ne ujemata.")

    
    try:
        if int(szz) in existing_pacients: 
            # Dodamo uporabnika in zdravnika v bazo
            nas_pacient = repo.dobi_gen_id(pacient, szz, id_col="szz")
            auth.dodaj_uporabnika(
                uporabnisko_ime, None, nas_pacient.id, 'Pacient', 
                ime, priimek, geslo=geslo)

            return template('registracija_uspesna.html', 
                            napaka=None, ime=ime, priimek=priimek)
        else:
            return template('registracija_pacient.html', 
                            napaka="Napaka pri registracijiii.")

    except Exception as e:
        return template('registracija_pacient.html', 
                        napaka="Napaka pri registraciji.")

@get('/prijava_next')
def prijava_next():
    return template("prijava_next.html", napaka=None)

@post('/prijava_next')
def prijava_next():
    """
    Prijavi uporabnika v aplikacijo. Če je prijava uspešna, ustvari piškotke 
    o uporabniku in njegovi roli. Drugače sporoči, da je prijava neuspešna.
    """
    username = request.forms.get('username')
    password = request.forms.get('password')

    if username == 'admin' and password == 'admin':
        if not auth.obstaja_uporabnik('admin'):
            auth.dodaj_uporabnika('admin', None, None, 'admin', 
                                  username, 'admin', geslo=password)

    if not all([username, password]):
        return template('prijava_next.html', 
                        napaka="Prosim, izpolnite vsa polja.")
    
    if not auth.obstaja_uporabnik(username):
        return template("prijava_next.html", 
                        napaka="Uporabnik s tem imenom ne obstaja")
    
    if not auth.preveri_geslo(username, password):
        return template("prijava_next.html", napaka="Napačno geslo")

    prijava = auth.prijavi_uporabnika(username, password)
    
    
    if prijava:
        response.set_cookie("uporabnik", username)
        response.set_cookie("rola", prijava.role)
        if prijava.role=='admin':
            return redirect(url('admin'))
        if prijava.role=='Zdravnik':
            return redirect(url('pogled_zdravnik'))
        if prijava.role=='Pacient':
            return redirect(url('pogled_pacient'))
        return template(
            'prijava_next.html', 
            uporabnik=username, 
            rola=prijava.role, 
            napaka='Neuspešna prijava. Napačno geslo ali uporabniško ime.'
        )        
    else:
        return template(
            "prijava_next.html", 
            uporabnik=None, 
            rola=None, 
            napaka="Neuspešna prijava. Napačno geslo ali uporabniško ime."
        )

@get('/odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in 
    njegovi roli.
    """
    
    response.delete_cookie("uporabnik")
    response.delete_cookie("rola")
    
    return template('prijava.html', uporabnik=None, rola=None, napaka=None)





##----------------FUNCTIONS FOR ADMIN-----------------##
@get('/admin')
@cookie_required
def admin():
    rola = request.get_cookie("rola") 
    return template('admin.html', rola = rola, napaka = None)

@get('/admin/prikazi_zdravnike')
@cookie_required
def prikazi_zdravnike():

    zdravniki = repo.zdravnik()

    return template('prikazi_zdravnike.html', zdravniki = zdravniki, 
                    napaka = None)



@get('/admin/prikazi_paciente')
@cookie_required
def prikazi_paciente():

    pacienti = repo.pacientDiag()

    return template('prikazi_paciente.html', pacienti = pacienti, napaka = None)

@get('/admin/dodaj_zdravnika')
@cookie_required
def dodaj_zdravnika():
    """
    Dodajanje zdravnika.
    """
    
    rola = request.get_cookie("rola")
    return template('dodaj_zdravnika.html', rola = rola, napaka = None)

@post('/admin/dodaj_zdravnika')
@cookie_required
def dodaj_zdravnika_post():
    """
    Processes the form submission to add a doctor.
    """
    rola = request.get_cookie("rola") 
    ime = request.forms.get('ime')
    priimek = request.forms.get('priimek')
    specializacija = request.forms.get('spec')

    if not ime or not priimek or not specializacija:
        return template('dodaj_zdravnika.html', rola = rola, 
                        napaka="Prosim, izpolnite vsa polja.")
    existing_doctors = [
    (zdravnik.ime, zdravnik.priimek) 
    for zdravnik in repo.zdravnik()
    ]
    if (ime, priimek) in existing_doctors:
        return template('dodaj_zdravnika.html', rola = rola, 
                        napaka="Zdravnik s tem imenom in priimkom že obstaja.")
    try:
        existing_specializacije = [spec.opis for spec in repo.specializacije()]
        if specializacija not in existing_specializacije:
            repo.dodaj_gen(specializacije(opis=specializacija))
        
        repo.dodaj_gen(zdravnik(ime=ime, priimek=priimek, opis=specializacija))
        return template('dodajanje_uspesno.html', 
                        napaka="Zdravnik uspešno dodan.")
    except Exception as e:
        return template('dodaj_zdravnika.html', 
                        napaka=f"Napaka pri dodajanju zdravnika: {e}")
    
@get('/admin/prikazi_uporabnike')
@cookie_required
def prikazi_uporabnike():

    uporabniki = repo.uporabnik()

    return template('prikazi_uporabnike.html', uporabniki = uporabniki, 
                    napaka = None)

##----------------FUNCTIONS FOR ZDRAVNIK-----------------##
@get('/pogled_zdravnik')
@zdravnik_required
def pogled_zdravnik():
    return template('pogled_zdravnik.html', napaka = None)

@get('/pogled_zdravnik/prikazi_moje_paciente')
@zdravnik_required
def prikazi_moje_paciente():
    uporabnikk = request.get_cookie("uporabnik")

    zdravnik = repo.dobi_gen_id(uporabnik, uporabnikk, id_col="username")

    pacienti = repo.izberi_paciente_zdravnika(zdravnik.ime, zdravnik.priimek)
    pacienti_diag = repo.pacient_to_pacientDiag(pacienti)
    
    return template('prikazi_moje_paciente.html', 
                    pacienti_diag=pacienti_diag, napaka = None)

@get('/pogled_zdravnik/dodaj_pacienta')
@zdravnik_required
def dodaj_pacienta():
    """
    Dodajanje pacienta.
    """
    rola = request.get_cookie("rola") 
    return template('dodaj_pacienta.html', rola=rola, napaka = None)

@post('/pogled_zdravnik/dodaj_pacienta')
@zdravnik_required
def dodaj_pacienta_post():
    """
    Processes the form submission to add a patient.
    """
    rola = request.get_cookie("rola")
    ime = request.forms.get('ime')
    priimek = request.forms.get('priimek')
    szz = request.forms.get('szz')
    if not ime or not priimek or not szz:
        return template('dodaj_pacienta.html', rola=rola, 
                        napaka="Prosim, izpolnite vsa polja.")
    existing_pacients = [pacient.szz for pacient in repo.pacient()]
    if int(szz) in existing_pacients:
        return template(
            'dodaj_pacienta.html', 
            rola=rola, 
            napaka="Pacient s tem številom zdravstvenega zavarovanja že obstaja."
        )
    try:
        pacientt = pacient(ime=ime, priimek=priimek, szz=szz)
        repo.dodaj_gen(pacientt)
        zdravnikk = repo.dobi_gen_id(
            uporabnik, request.get_cookie("uporabnik"), id_col="username"
            )
        bridgee=bridge(
            id_pacient=pacientt.id, id_zdravnik=zdravnikk.id_zdravnik
            )
        repo.dodaj_gen(bridgee, serial_col=None)
        return template('dodajanje_uspesno.html', 
                        napaka="Pacient uspešno dodan.")
    except Exception as e:
        return template('dodaj_pacienta.html', rola=rola, 
                        napaka=f"Napaka pri dodajanju pacienta: {e}")

#diagnozo se lahko postavi le pacientu, ki je v bazi, torej v tabeli pacient
#Torej, ko zdravnik dobi novega pacienta, ga najprej doda v bazo pacientov, \
# nato pa mu lahko postavi diagnozo
@get('/pogled_zdravnik/dodaj_diagnozo')
@zdravnik_required
def dodaj_diagnozo():
    """
    Dodajanje diagnoze pacientu.
    """
    rola = request.get_cookie("rola")
    return template('dodaj_diagnozo.html', rola=rola, napaka=None)

@post('/pogled_zdravnik/dodaj_diagnozo')
@zdravnik_required
def dodaj_diagnozo_post():
    """
    Processes the form submission to add a diagnosis to a patient.
    """
    rola = request.get_cookie("rola")
    szz = request.forms.get('szz')
    detajl = request.forms.get('diagnoza')
    koda = request.forms.get('koda')

    uporabnikk = request.get_cookie("uporabnik")
    zdravnikk = repo.dobi_gen_id(uporabnik, uporabnikk, id_col="username")
    zdravnik_id = zdravnikk.id_zdravnik
   
    if not szz or not detajl or not koda:
        return template('dodaj_diagnozo.html', rola=rola, 
                        napaka="Prosim, izpolnite vsa polja.")
    
    try:
        pacientt = repo.dobi_gen_id(pacient, int(szz), id_col="szz")
        if pacientt:
            diagnozaa = diagnoza(
                id_pacient=pacientt.id, 
                id_zdravnik= zdravnik_id, 
                detajli=detajl, 
                koda=koda, 
                aktivnost=True
                )
            repo.dodaj_gen(diagnozaa)
            return template('dodajanje_diagnoze_uspesno.html', 
                            napaka="Diagnoza uspešno dodana.")
        else:
            return template(
                'dodaj_diagnozo.html', 
                rola=rola, 
                napaka="Pacient, kateremu želite dodeliti diagnozo, ne obstaja."
                )
    except Exception as e:
        return template('dodaj_diagnozo.html', rola=rola, 
                        napaka=f"Napaka pri dodajanju diagnoze: {e}")

@get('/pogled_zdravnik/moja_specializacija')
@zdravnik_required
def moja_specializacija():
    """
    Prikaz specializacije zdravnika.
    """
    uporabnikk = request.get_cookie("uporabnik")
    zdravnik = repo.dobi_gen_id(uporabnik, uporabnikk, id_col="username")
    spec = repo.specializacija_zdravnik(zdravnik.ime, zdravnik.priimek)

    return template('moja_specializacija.html', specializacija = spec, 
                    napaka=None)

##----------------FUNCTIONS FOR PACIENT-----------------##
@get('/pogled_pacient')
@pacient_required
def pogled_pacient():
    return template('pogled_pacient.html', napaka = None)

@get('/pogled_pacient/moje_diagnoze')
@pacient_required
def moje_diagnoze():
    uporabnikk = repo.dobi_gen_id(uporabnik, request.get_cookie("uporabnik"), 
                                  id_col="username")
    diagnoze = repo.prikazi_diagnoze_pacienta(uporabnikk.id_pacient)
    return template('moje_diagnoze.html', diagnoze=diagnoze, napaka=None)

@get('/pogled_pacient/moji_podatki')
@pacient_required
def moji_podatki():
    uporabnikk = repo.dobi_gen_id(uporabnik, request.get_cookie("uporabnik"), 
                                  id_col="username")
    pacientt = repo.pacient_dobi_info(uporabnikk.id_pacient)
    return template('moji_podatki', pacientt = pacientt, napaka = None)



# Glavni program


# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
