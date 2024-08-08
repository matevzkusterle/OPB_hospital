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
import data.auth_public as auth_data
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

@get('/osnovna_stran')
def osnovna_stran():
    if request.get_cookie("rola") == 'admin':
        return redirect(url('admin'))
    elif request.get_cookie("rola") == 'Zdravnik':
        return redirect(url('pogled_zdravnik'))
    elif request.get_cookie("rola") == 'Pacient':
        return redirect(url('pogled_pacient'))
    else:
        return redirect(url('prijava'))

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

    uporabniki = repo.uporabnik()
    existing_usernames = [uporabnik.username for uporabnik in uporabniki]
    
    
    if not all([ime, priimek, uporabnisko_ime, geslo, potrditev_gesla]):
        return template('registracija_zdravnik.html', 
                        napaka="Prosim, izpolnite vsa polja.")
    
    if uporabnisko_ime in existing_usernames:
        return template('registracija_zdravnik.html', 
                        napaka="Uporabnik s tem uporabnškim imenom že obstaja.")
    

    if geslo != potrditev_gesla:
        return template('registracija_zdravnik.html', 
                        napaka="Gesli se ne ujemata.")
    
    id_zdravnikov = [uporabnikk.id_zdravnik for uporabnikk in uporabniki]
    try:
        nas_zdravnik = repo.dobi_gen_dvoje(
                zdravnik, ime, priimek, prvi="ime", drugi="priimek"
                )
        
    except Exception as e:
        return template(
                'registracija_zdravnik.html', 
                napaka=(
                    f"Napaka pri registraciji: Imena {ime} {priimek} ni v bazi. "
                    f"Kot zdravnik morate biti za registracijo vnešeni v bazo."
                )
            )
    try:
        if nas_zdravnik.id in id_zdravnikov:
            return template('registracija_zdravnik.html', 
                            napaka="Ta zdravnik je že registriran.")

        else:

            auth.dodaj_uporabnika(
                uporabnisko_ime, nas_zdravnik.id, None, 'Zdravnik',
                ime, priimek, geslo=geslo)
            return template('registracija_uspesna.html', napaka = None)
        
    except Exception as e:
        return template('registracija_zdravnik.html', 
                        napaka="Napaka pri registraciji.")

@get('/registracija_pacient')
def registracija_pacient():

    return template('registracija_pacient.html', uporabnik=None, napaka=None)

@post('/registracija_pacient')
def registracija_pacient():
    """
    Processes the registration of a doctor.
    """
    ime = request.forms.getunicode('ime')
    priimek = request.forms.getunicode('priimek')
    szz = request.forms.getunicode('szz')
    uporabnisko_ime = request.forms.getunicode('username')
    geslo = request.forms.getunicode('password')
    potrditev_gesla = request.forms.getunicode('password2')
   
    uporabniki = repo.uporabnik()
    existing_usernames = [uporabnik.username for uporabnik in uporabniki]

    if not all([ime, priimek, szz, geslo, uporabnisko_ime, potrditev_gesla]):
        return template('registracija_pacient.html', 
                        napaka="Prosim, izpolnite vsa polja.")
    
    if uporabnisko_ime in existing_usernames:
        return template('registracija_pacient.html', 
                    napaka="Uporabnik s tem uporabniškim imenom že obstaja.")

    if geslo != potrditev_gesla:
        return template('registracija_pacient.html', 
                        napaka="Gesli se ne ujemata.")

    id_pacientov = [uporabnikk.id_pacient for uporabnikk in uporabniki]
    try:
        nas_pacient = repo.dobi_gen_id(pacient, szz, id_col="szz")
    except Exception as e:
        return template(
                'registracija_zdravnik.html', 
                napaka=(
                    f"Napaka pri registraciji: Imena {ime} {priimek} ni v bazi. "
                    f"Kot pacient morate biti za registracijo vnešeni v bazo."
                )
            )
    try:
        if nas_pacient.id in id_pacientov:
            return template('registracija_pacient.html', 
                            napaka="Ta pacient je že registriran.")
        else:
            auth.dodaj_uporabnika(
                uporabnisko_ime, None, nas_pacient.id, 'Pacient', 
                ime, priimek, geslo=geslo)
            return template('registracija_uspesna.html', 
                            napaka=None, ime=ime, priimek=priimek)
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
    username = request.forms.getunicode('username')
    password = request.forms.getunicode('password')

    if username == 'admin' and password == 'admin':
        if not auth.obstaja_uporabnik('admin'):
            auth.dodaj_uporabnika('admin', None, None, 'admin', 
                                  'G.', username, geslo=password)

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
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))

    return template('admin.html', rola = rola, napaka = None, admin=ime_priimek)

@get('/admin/prikazi_zdravnike')
@cookie_required
def prikazi_zdravnike():

    zdravniki = repo.zdravnik()
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    return template('prikazi_zdravnike.html', zdravniki = zdravniki, 
                    napaka = None, admin=ime_priimek)



@get('/admin/prikazi_paciente')
@cookie_required
def prikazi_paciente():

    pacienti = repo.pacient()
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    return template('prikazi_paciente.html', pacienti = pacienti, 
                    napaka = None, admin=ime_priimek)

@get('/admin/dodaj_zdravnika')
@cookie_required
def dodaj_zdravnika():
    """
    Dodajanje zdravnika.
    """
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    rola = request.get_cookie("rola")
    return template('dodaj_zdravnika.html', rola = rola, 
                    napaka = None, admin=ime_priimek)

@post('/admin/dodaj_zdravnika')
@cookie_required
def dodaj_zdravnika_post():
    """
    Processes the form submission to add a doctor.
    """
    rola = request.get_cookie("rola") 
    ime = request.forms.getunicode('ime')
    priimek = request.forms.getunicode('priimek')
    specializacija = request.forms.getunicode('spec')
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))

    if not ime or not priimek or not specializacija:
        return template('dodaj_zdravnika.html', rola = rola, 
                        napaka="Prosim, izpolnite vsa polja.", 
                        admin=ime_priimek)
    existing_doctors = [
    (zdravnik.ime, zdravnik.priimek) 
    for zdravnik in repo.zdravnik()
    ]
    if (ime, priimek) in existing_doctors:
        return template('dodaj_zdravnika.html', rola = rola, 
                        napaka="Zdravnik s tem imenom in priimkom že obstaja.",
                        admin=ime_priimek)
    try:
        existing_specializacije = [spec.opis for spec in repo.specializacije()]
        if specializacija not in existing_specializacije:
            repo.dodaj_gen(specializacije(opis=specializacija))
        
        a=repo.dobi_gen_id(specializacije, specializacija, id_col="opis")
        #max_id = repo.max_id(zdravnik, id_col="id")
        #new_id = max_id + 1
        repo.dodaj_gen(zdravnik(ime=ime, priimek=priimek, specializacija=a.id))
        return template('dodajanje_uspesno_admin.html', 
                        napaka="Zdravnik uspešno dodan",
                        admin=ime_priimek)
    except Exception as e:
        return template('dodaj_zdravnika.html', 
                        napaka=f"Napaka pri dodajanju zdravnika: {e}",
                        admin=ime_priimek)
    
@get('/admin/prikazi_uporabnike')
@cookie_required
def prikazi_uporabnike():

    uporabniki = repo.uporabnik()
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    return template('prikazi_uporabnike.html', uporabniki = uporabniki, 
                    napaka = None, admin=ime_priimek)

##----------------FUNCTIONS FOR ZDRAVNIK-----------------##
@get('/pogled_zdravnik')
@zdravnik_required
def pogled_zdravnik():
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    return template('pogled_zdravnik.html', napaka = None,
                    zdravnik=ime_priimek)

@get('/pogled_zdravnik/prikazi_moje_paciente')
@zdravnik_required
def prikazi_moje_paciente():
    uporabnikk = request.get_cookie("uporabnik")

    zdravnik = repo.dobi_gen_id(uporabnik, uporabnikk, id_col="username")

    pacientii = repo.izberi_paciente_zdravnika(zdravnik.ime, zdravnik.priimek)
    
    diagnoze = repo.diagnoza()
    id_pacientov = [diag.id_pacient for diag in diagnoze]

    pacienti = [pacient for pacient in pacientii if pacient.id in id_pacientov]


    pacienti_diag = repo.pacient_to_pacientDiag(pacienti)
    # Example of sorting by 'ime' (name) and then by 'priimek' (surname)
    pacienti_diag = sorted(pacienti_diag, key=lambda x: 
                           (x.ime, x.priimek, x.koda))
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    
    return template('prikazi_moje_paciente.html', 
                    pacienti_diag=pacienti_diag, napaka = None,
                    zdravnik=ime_priimek)

@get('/pogled_zdravnik/prikazi_seznam_pacientov')
@zdravnik_required
def prikazi_seznam_pacientov():
    uporabnikk = request.get_cookie("uporabnik")

    zdravnik = repo.dobi_gen_id(uporabnik, uporabnikk, id_col="username")

    pacienti = repo.izberi_paciente_zdravnika(zdravnik.ime, zdravnik.priimek)
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    return template('prikazi_seznam_pacientov.html', pacienti = pacienti, 
                    napaka = None, zdravnik=ime_priimek)

@post('/pogled_zdravnik/update_aktivnost')
def update_aktivnost():
    id_diagnoza = int(request.forms.getunicode('id'))
    aktivnost = request.forms.getunicode('aktivnost') == 'true'

    diag_stara = repo.dobi_gen_id(diagnoza, id_diagnoza, id_col="id")
    diag_stara.aktivnost = aktivnost
    repo.posodobi_gen(diag_stara, id_col = "id")

    return redirect(url('prikazi_moje_paciente'))

@get('/pogled_zdravnik/dodaj_pacienta')
@zdravnik_required
def dodaj_pacienta():
    """
    Dodajanje pacienta.
    """
    rola = request.get_cookie("rola") 
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    return template('dodaj_pacienta.html', rola=rola, napaka = None,
                    zdravnik=ime_priimek)

@post('/pogled_zdravnik/dodaj_pacienta')
@zdravnik_required
def dodaj_pacienta_post():
    """
    Processes the form submission to add a patient.
    """
    rola = request.get_cookie("rola")
    ime = request.forms.getunicode('ime')
    priimek = request.forms.getunicode('priimek')
    szz = request.forms.getunicode('szz')
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    if not ime or not priimek or not szz:
        return template('dodaj_pacienta.html', rola=rola, 
                        napaka="Prosim, izpolnite vsa polja.",
                        zdravnik=ime_priimek)
    existing_pacients = [pacient.szz for pacient in repo.pacient()]
    if int(szz) in existing_pacients:
        moje_ime, moj_priimek = repo.dobi_ime_in_priimek_uporabnika(
            request.get_cookie("uporabnik")
        )

        vsi_moji_pacienti = [pacientt.szz for pacientt \
                                in repo.izberi_paciente_zdravnika(
                                    moje_ime, moj_priimek)]

        if int(szz) in vsi_moji_pacienti:
            return template('dodajanje_uspesno.html', 
                            napaka="Pacient že dodan.",
                            zdravnik=ime_priimek)
        else:
            pacientt = repo.dobi_gen_id(pacient, int(szz), id_col="szz")
            zdravnikk = repo.dobi_gen_id(
                uporabnik, request.get_cookie("uporabnik"), id_col="username"
                )
            bridgee=bridge(
                id_pacient=pacientt.id, id_zdravnik=zdravnikk.id_zdravnik
                )
            repo.dodaj_gen(bridgee, serial_col=None)

            return template('dodajanje_uspesno.html', 
                            napaka="Pacient uspešno dodan.",
                            zdravnik=ime_priimek)
    else:
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
                            napaka="Pacient uspešno dodan.",
                            zdravnik=ime_priimek)
        except Exception as e:
            return template('dodaj_pacienta.html', rola=rola, 
                            napaka=f"Napaka pri dodajanju pacienta: {e}",
                            zdravnik=ime_priimek)

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
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    return template('dodaj_diagnozo.html', rola=rola, napaka=None,
                    zdravnik=ime_priimek)

@post('/pogled_zdravnik/dodaj_diagnozo')
@zdravnik_required
def dodaj_diagnozo_post():
    """
    Processes the form submission to add a diagnosis to a patient.
    """
    rola = request.get_cookie("rola")
    szz = request.forms.getunicode('szz')
    detajl = request.forms.getunicode('diagnoza')
    koda = request.forms.getunicode('koda')
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))

    uporabnikk = request.get_cookie("uporabnik")
    zdravnikk = repo.dobi_gen_id(uporabnik, uporabnikk, id_col="username")
    zdravnik_id = zdravnikk.id_zdravnik
   
    if not szz or not detajl or not koda:
        return template('dodaj_diagnozo.html', rola=rola, 
                        napaka="Prosim, izpolnite vsa polja.",
                        zdravnik=ime_priimek)
    
    try:
        pacientt = repo.dobi_gen_id(pacient, int(szz), id_col="szz")
        moje_ime, moj_priimek = repo.dobi_ime_in_priimek_uporabnika(
            request.get_cookie("uporabnik")
        )

        vsi_moji_pacienti = [pacientt.szz for pacientt \
                                in repo.izberi_paciente_zdravnika(
                                    moje_ime, moj_priimek)]
        if pacientt in vsi_moji_pacienti:
            diagnozaa = diagnoza(
                id_pacient=pacientt.id,
                id_zdravnik= zdravnik_id, 
                detajli=detajl, 
                koda=koda, 
                aktivnost=True
                )
            repo.dodaj_gen(diagnozaa)
            return template('dodajanje_diagnoze_uspesno.html', 
                            napaka="Diagnoza uspešno dodana.",
                            zdravnik=ime_priimek)
        else:
            return template(
                'dodaj_diagnozo.html', 
                rola=rola, 
                napaka="Niste zdravnik tega pacienta.",
                zdravnik=ime_priimek
                )
    except Exception as e:
        return template('dodaj_diagnozo.html', rola=rola, 
                        napaka=f"Napaka pri dodajanju diagnoze: {e}",
                        zdravnik=ime_priimek)

@get('/pogled_zdravnik/moja_specializacija')
@zdravnik_required
def moja_specializacija():
    """
    Prikaz specializacije zdravnika.
    """
    uporabnikk = request.get_cookie("uporabnik")
    zdravnik = repo.dobi_gen_id(uporabnik, uporabnikk, id_col="username")
    spec = repo.specializacija_zdravnik(zdravnik.ime, zdravnik.priimek)
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))

    return template('moja_specializacija.html', specializacija = spec, 
                    napaka=None, zdravnik=ime_priimek)

##----------------FUNCTIONS FOR PACIENT-----------------##
@get('/pogled_pacient')
@pacient_required
def pogled_pacient():
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    return template('pogled_pacient.html', napaka = None, pacient=ime_priimek)

@get('/pogled_pacient/moje_diagnoze')
@pacient_required
def moje_diagnoze():
    uporabnikk = repo.dobi_gen_id(uporabnik, request.get_cookie("uporabnik"), 
                                  id_col="username")
    diagnoze = repo.prikazi_diagnoze_pacienta(uporabnikk.id_pacient)
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    return template('moje_diagnoze.html', diagnoze=diagnoze, napaka=None,
                    pacient=ime_priimek)

@get('/pogled_pacient/moji_podatki')
@pacient_required
def moji_podatki():
    uporabnikk = repo.dobi_gen_id(uporabnik, request.get_cookie("uporabnik"), 
                                  id_col="username")
    pacientt = repo.pacient_dobi_info(uporabnikk.id_pacient)
    ime_priimek = \
            repo.dobi_ime_priimek_uporabnika(request.get_cookie("uporabnik"))
    return template('moji_podatki', pacientt = pacientt, napaka = None,
                    pacient=ime_priimek)



# Glavni program


# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
