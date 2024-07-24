# uvozimo bottle.py
from bottleext import get, post, run, request, template, redirect, static_file, url, response, template_user
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
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("uporabnik")
        if cookie:
            return f(*args, **kwargs)
        return template("prijava.html",uporabnik=None, rola=None, napaka="Potrebna je prijava!")   
    return decorated


def zdravnik_required(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie_rola = request.get_cookie("rola")
        if cookie_rola is not None and cookie_rola == 'Zdravnik':
            return f(*args, **kwargs)
        return template("prijava.html",uporabnik=None, rola=None, napaka="Potrebna je prijava!")
    return decorated

def pacient_required(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie_rola = request.get_cookie("rola")
        if cookie_rola is not None and cookie_rola == 'Pacient':
            return f(*args, **kwargs)
        return template("prijava.html",uporabnik=None, rola=None, napaka="Potrebna je prijava!")
    return decorated

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')



@get('/')
def index():
    """
    Začetna stran.
    """
    return template_user('dobrodosli.html', napaka=None)

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
    existing_doctors = [(zdravnik.ime, zdravnik.priimek) for zdravnik in zdravniki]
    uporabniki = repo.uporabnik()
    existing_usernames = [uporabnik.username for uporabnik in uporabniki]
    
    
    
    if uporabnisko_ime in existing_usernames:
        return template('registracija_zdravnik.html', napaka="Uporabnik s tem uporabnškim imenom že obstaja.")
    
    if not all([ime, priimek, uporabnisko_ime, geslo, potrditev_gesla]):
        return template('registracija_zdravnik.html', napaka="Prosim, izpolnite vsa polja.")

    if geslo != potrditev_gesla:
        return template('registracija_zdravnik.html', napaka="Gesli se ne ujemata.")
    
    if (ime, priimek) in existing_doctors:
        nas_zdravnik = repo.dobi_gen_dvoje(zdravnik, ime, priimek, prvi="ime", drugi="priimek")
        # Dodamo uporabnika in zdravnika v bazo
        
        auth.dodaj_uporabnika(uporabnisko_ime, nas_zdravnik.id, None, 'Zdravnik',ime, priimek, geslo=geslo)
        return template('registracija_uspesna.html', napaka = None)
    else:
        return template('registracija_zdravnik.html', napaka=f"Napaka pri registraciji: Imena {ime} {priimek} ni v bazi. Za registracijo "
                                                             "zdravnika morate biti vnešeni v bazo.")




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
        return template('registracija_zdravnik.html', napaka="Uporabnik s tem uporabnškim imenom že obstaja.")
    # če ne izpolni vseh polj
    if not ime or not priimek or not szz or not geslo or not uporabnisko_ime or not potrditev_gesla:
        return template('registracija_pacient.html', napaka="Prosim, izpolnite vsa polja.")

    if geslo != potrditev_gesla:
        return template('registracija_pacient.html', napaka="Gesli se ne ujemata.")

    
    try:
        if int(szz) in existing_pacients: 
            # Dodamo uporabnika in zdravnika v bazo
            nas_pacient = repo.dobi_gen_id(pacient, szz, id_col="szz")
            auth.dodaj_uporabnika(uporabnisko_ime, None, nas_pacient.id, 'Pacient', ime, priimek, geslo=geslo)

            return template('registracija_uspesna.html', napaka=None, ime=ime, priimek=priimek)
        else:
            return template('registracija_pacient.html', napaka="Napaka pri registracijiii.")

    except Exception as e:
        return template('registracija_pacient.html', napaka="Napaka pri registraciji.")

@get('/prijava_next')
def prijava_next():
    return template("prijava_next.html", napaka=None)

@post('/prijava_next')
def prijava_next():
    """
    Prijavi uporabnika v aplikacijo. Če je prijava uspešna, ustvari piškotke o uporabniku in njegovi roli.
    Drugače sporoči, da je prijava neuspešna.
    """
    username = request.forms.get('username')
    password = request.forms.get('password')

    if username == 'admin' and password == 'admin':
        if not auth.obstaja_uporabnik('admin'):
            auth.dodaj_uporabnika('admin', None, None, 'admin', username, 'admin', geslo=password)

    if not all([username, password]):
        return template('prijava_next.html', napaka="Prosim, izpolnite vsa polja.")
    
    if not auth.obstaja_uporabnik(username):
        return template("prijava_next.html", napaka="Uporabnik s tem imenom ne obstaja")
    
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
        return template('prijava_next.html', uporabnik=username, rola=prijava.role, napaka = 'Neuspešna prijava. Napačno geslo ali uporabniško ime.')
        
    else:
        return template("prijava_next.html", uporabnik=None, rola=None, napaka="Neuspešna prijava. Napačno geslo ali uporabniško ime.")


@get('/odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi roli.
    """
    
    response.delete_cookie("uporabnik")
    response.delete_cookie("rola")
    
    return template('prijava.html', uporabnik=None, rola=None, napaka=None)





##----------------FUNCTIONS FOR ADMIN-----------------##
@get('/admin')
def admin():
    return template('admin.html', napaka = None)

@get('/admin/prikazi_zdravnike')
def prikazi_zdravnike():

    zdravniki = repo.zdravnik()

    return template_user('prikazi_zdravnike.html', zdravniki = zdravniki)



@get('/admin/prikazi_paciente')
def prikazi_paciente():

    pacienti = repo.pacientDiag()

    return template_user('prikazi_paciente.html', pacienti = pacienti)

@get('/admin/prikazi_uporabnike')
def prikazi_uporabnike():

    uporabniki = repo.uporabnik()

    return template_user('prikazi_uporabnike.html', uporabniki = uporabniki)

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
    
    return template_user('prikazi_moje_paciente.html', pacienti_diag=pacienti_diag)

@get('/pogled_zdravnik/dodaj_pacienta')
@zdravnik_required
def dodaj_pacienta():
    """
    Dodajanje pacienta.
    """
    rola = request.get_cookie("rola") 
    if rola not in ['admin', 'Zdravnik']:
        # Redirect or show an error page if user doesn't have permission
        return template('error.html', napaka="Nimate dovoljenja za ogled te strani!")

    return template('dodaj_pacienta.html', rola=rola, napaka = None)

@post('/pogled_zdravnik/dodaj_pacienta')
@zdravnik_required
def dodaj_pacienta_post():
    """
    Processes the form submission to add a patient.
    """
    rola = request.get_cookie("rola")
    # if rola not in ['admin', 'Zdravnik']:
    #     return template('error.html', napaka="Nimaš dovoljenja za ogled te strani!")
    ime = request.forms.get('ime')
    priimek = request.forms.get('priimek')
    szz = request.forms.get('szz')
    if not ime or not priimek or not szz:
        return template('dodaj_pacienta.html', rola=rola, napaka="Prosim, izpolnite vsa polja.")
    existing_pacients = [pacient.szz for pacient in repo.pacient()]
    if int(szz) in existing_pacients:
        return template('dodaj_pacienta.html', rola=rola, napaka="Pacient s tem številom zdravstvenega zavarovanja že obstaja.")
    try:
        pacientt = pacient(ime=ime, priimek=priimek, szz=szz)
        repo.dodaj_gen(pacientt)
        return template('dodajanje_uspesno.html', napaka="Pacient uspešno dodan.")
    except Exception as e:
        return template('dodaj_pacienta.html', rola=rola, napaka="Napaka pri dodajanju pacienta: {}".format(str(e)))

#diagnozo se lahko postavi le pacientu, ki je v bazi, torej v tabeli pacient
#Torej, ko zdravnik dobi novega pacienta, ga najprej doda v bazo pacientov, \
# nato pa mu lahko postavi diagnozo
@get('/pogled_zdravnik/dodaj_diagnozo')
@zdravnik_required
def dodaj_diagnozo():
    """
    Dodajanje diagnoze pacientu.
    """
    # rola = request.get_cookie("rola")
    # if rola != 'Zdravnik':
    #     return template('error.html', napaka="Nimate dovoljenja za ogled te strani!")

    pacienti = repo.pacient()
    return template_user('dodaj_diagnozo.html', pacienti=pacienti, napaka=None)

@post('/pogled_zdravnik/dodaj_diagnozo')
@zdravnik_required
def dodaj_diagnozo_post():
    """
    Processes the form submission to add a diagnosis to a patient.
    """
    rola = request.get_cookie("rola")
    # if rola != 'Zdravnik':
    #     return template('error.html', napaka="Nimate dovoljenja za ogled te strani!")

    szz = request.forms.get('szz')
    detajl = request.forms.get('diagnoza')
    koda = request.forms.get('koda')
       

    pacienti = repo.pacient()
    if not szz or not detajl or not koda:
        
        return template_user('dodaj_diagnozo.html', rola =rola, pacienti=pacienti, napaka="Prosim, izpolnite vsa polja.")
    
    try:
        pacientt = repo.dobi_gen_id(pacient, szz, id_col="szz")
        if pacientt:
            diagnozaa = diagnoza(pacient=pacientt.id, detajl=detajl, koda=koda, aktivnost=True)
            repo.dodaj_gen(diagnozaa)
            return template_user('dodajanje_uspesno.html', napaka="Diagnoza uspešno dodana.")
        else:
            return template_user('dodaj_diagnozo.html', rola=rola, napaka="Pacient, kateremu želite dodeliti diagnozo, ne obstaja.")
    except Exception as e:
        return template_user('dodaj_diagnozo.html', rola=rola, napaka="Napaka pri dodajanju diagnoze: {}".format(str(e)))

@get('/pogled_zdravnik/moja_specializacija')
@zdravnik_required
def moja_specializacija():
    """
    Prikaz specializacije zdravnika.
    """
    # rola = request.get_cookie("rola")
    # if rola != 'Zdravnik':
    #     return template('error.html', napaka="Nimate dovoljenja za ogled te strani!")
    uporabnikk = request.get_cookie("uporabnik")
    zdravnik = repo.dobi_gen_id(uporabnik, uporabnikk, id_col="username")
    spec = repo.specializacija_zdravnik(zdravnik.ime, zdravnik.priimek)

    return template_user('moja_specializacija.html', specializacija = spec, napaka=None)

##----------------FUNCTIONS FOR PACIENT-----------------##
@get('/moje_diagnoze')
def moje_diagnoze():
    return template_user('moje_diagnoze.html', pacient =None )

@post('/moje_diagnoze')
def moje_diagnoze():
    uporabnik = request.get_cookie("uporabnik")
    a = repo.uporabnik()
    print(a)
    if uporabnik:
        diagnoze = repo.dobi_diagnoze_pacienta(uporabnik)
        return template_user('moje_diagnoze.html', pacient=uporabnik, diagnoze=diagnoze)
    else:
        return template_user('moje_diagnoze.html', pacient=None)
# Glavni program


# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
