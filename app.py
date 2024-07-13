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


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')



@get('/')
@cookie_required
def index():
    """
    Začetna stran.
    """
    return template_user('dobrodosli.html', napaka=None)

@get('/prijava')
def prijava():
    return template("prijava.html", napaka=None)

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
    
    if not auth.obstaja_uporabnik(username):
        return template("prijava_next.html", napaka="Uporabnik s tem imenom ne obstaja")
    
    if not auth.preveri_geslo(username, password):
        return template("prijava_next.html", napaka="Napačno geslo")

    prijava = auth.prijavi_uporabnika(username, password)
    
    
    if prijava:
        response.set_cookie("uporabnik", username)
        response.set_cookie("rola", prijava.role)
        
        if prijava.role == 'admin':
            return redirect(url('admin'))
        if prijava.role=='Zdravnik':
            return redirect(url('pogled_zdravnik')) ### neki kar je html od zravnika, popravi!
        if prijava.role=='Pacient':
            return redirect(url('pogled_pacient')) ### neki kar je html od pacienta, popravi!

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


@get('/registracija_zdravnik')
def registracija_zdravnik():

    return template('registracija_zdravnik.html', uporabnik=None, rola='zdravnik', napaka=None)



@post('/registracija_zdravnik')
def registracija_zdravnik():
    """
    Processes the registration of a doctor.
    """
    ime = request.forms.get('ime')
    priimek = request.forms.get('priimek')
    uporabnisko_ime = request.forms.get('username')
    geslo = request.forms.get('password')
    potrditev_gesla = request.forms.get('password2')

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
    
    try:
        if (ime, priimek) in existing_doctors:
            # Dodamo uporabnika in zdravnika v bazo
            
            auth.dodaj_uporabnika(uporabnisko_ime, 'Zdravnik',ime, priimek, geslo=geslo)

            return template('registracija_uspesna.html', napaka = None)

    except BaseException as error:
        return template('registracija_zdravnik.html', napaka="Napaka pri registraciji: {}".format(error))




@get('/registracija_pacient')
def registracija_pacient():

    return template('registracija_pacient.html', uporabnik=None, rola=None, napaka=None)

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
    existing_pacients = [(pacient.ime, pacient.priimek) for pacient in pacienti]
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
        if (ime, priimek) in existing_pacients:
            # Dodamo uporabnika in zdravnika v bazo
            
            auth.dodaj_uporabnika(uporabnisko_ime, 'Pacient',ime, priimek, geslo=geslo)

            return template('registracija_uspesna.html', napaka =None, ime=ime, priimek=priimek)
        else:
            return template('registracija_pacient.html', napaka="Napaka pri registraciji.")

    except Exception as e:
        return template('registracija_pacient.html', napaka="Napaka pri registraciji.")



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

@get('/dodaj_pacienta')
def dodaj_pacienta():
    """
    Dodajanje pacienta.
    """
    rola = request.get_cookie("rola")  # Define the variable "rola" by getting it from the cookie
    if rola != 'Zdravnik':
        # Redirect or show an error page if user doesn't have permission
        return template('error.html', napaka="Nimate dovoljenja za ogled te strani!")

    return template('dodaj_pacienta.html', napaka = None, pacient=None)

@post('/dodaj_pacienta')
def dodaj_pacienta_post():
    """
    Processes the form submission to add a patient.
    """
    rola = request.get_cookie("rola")
    if rola != 'Zdravnik':
        return template('error.html', napaka="Nimaš dovoljenja za ogled te strani!")
    ime = request.forms.get('ime')
    priimek = request.forms.get('priimek')
    szz = request.forms.get('szz')
    if not ime or not priimek or not szz:
        return template('dodaj_pacienta.html', pacient=None, napaka="Prosim, izpolnite vsa polja.")
    try:
        pacientt = pacient(ime=ime, priimek=priimek, szz=szz)
        repo.dodaj_gen(pacientt)
        return template('dodaj_pacienta.html', pacient=None, napaka="Pacient uspešno dodan.")
    except Exception as e:
        return template('dodaj_pacienta.html', pacient=None, napaka="Napaka pri dodajanju pacienta: {}".format(str(e)))

#diagnozo se lahko postavi le pacientu, ki je v bazi, torej v tabeli pacient
#Torej, ko zdravnik dobi novega pacienta, ga najprej doda v bazo pacientov, \
# nato pa mu lahko postavi diagnozo
@get('/dodaj_diagnozo')
def dodaj_diagnozo():
    """
    Dodajanje diagnoze pacientu.
    """
    rola = request.get_cookie("rola")
    if rola != 'Zdravnik':
        return template('error.html', napaka="Nimate dovoljenja za ogled te strani!")

    pacienti = repo.pacient()
    return template_user('dodaj_diagnozo.html', pacienti=pacienti, napaka=None)

@post('/dodaj_diagnozo')
def dodaj_diagnozo_post():
    """
    Processes the form submission to add a diagnosis to a patient.
    """
    rola = request.get_cookie("rola")
    if rola != 'Zdravnik':
        return template('error.html', napaka="Nimate dovoljenja za ogled te strani!")

    pacient_id = request.forms.get('pacient_id')
    detajl = request.forms.get('diagnoza')
    koda = request.forms.get('koda')
    aktivnost = True

    if not pacient_id or not detajl or not koda:
        pacienti = repo.pacient()
        return template_user('dodaj_diagnozo.html', pacienti=pacienti, napaka="Prosim, izpolnite vsa polja.")

    try:
        pacientt = repo.dobi_gen_id(pacient, pacient_id)
        if pacientt:
            diagnozaa = diagnoza(pacient=pacient_id, detajl=detajl, koda=koda, aktivnost=aktivnost)
            repo.dodaj_gen(diagnozaa)
            return template_user('dodaj_diagnozo.html', napaka="Diagnoza uspešno dodana.")
        else:
            return template_user('dodaj_diagnozo.html', napaka="Pacient, kateremu želite dodeliti diagnozo, ne obstaja.")
    except Exception as e:
        return template_user('dodaj_diagnozo.html', napaka="Napaka pri dodajanju diagnoze: {}".format(str(e)))

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
