import time
import bottle
import model
from model import Stanje, Uporabnik, Prijatelj, Igra, Igralec, Karta, uporabnik_iz_slovarja, uporabnik_iz_svoje_datoteke

DATOTEKA_S_STANJEM = "stanje.json"
PISKOTEK_PRIJAVA = "prijavljen"
PISKOTEK_UPORABNISKO_IME = "uporabn"
SKRIVNOST = "psst..."

# Tu dodaj da če datoteka ne obstaja da jo nardi

def trenutni_uporabnik():
    uporabnisko_ime = bottle.request.get_cookie(PISKOTEK_UPORABNISKO_IME, secret=SKRIVNOST)
    return uporabnik_iz_svoje_datoteke(uporabnisko_ime) if uporabnisko_ime else 0

def shrani_uporabnika():
    trenutni_uporabnik().v_svojo_datoteko() #Shrani od uporabnika v njegovo datoteko

def pridobi_stanje():
    return model.stanje_iz_datoteke(DATOTEKA_S_STANJEM)

def shrani_stanje(stanje):
    stanje.v_datoteko(DATOTEKA_S_STANJEM)


@bottle.get('/')
def osnovna_stran():
    return bottle.template("uvodna_stran.html", uporabnik=0)

@bottle.get("/registracija/")
def registracija_get():
    return bottle.template("registracija.html", napaka=None)

@bottle.post("/registracija/")
def registracija_post():
    uporabnisko_ime = bottle.request.forms["uporabnisko_ime"]
    email = bottle.request.forms["email"]
    geslo = bottle.request.forms["geslo"]
    vzdevek = bottle.request.forms["vzdevek"]
    if uporabnisko_ime in pridobi_stanje().uporabniki.keys():
        return bottle.template("registracija.html", napaka="zasedno")
    else:
        nov_uporabnik = Uporabnik(uporabnisko_ime, geslo, email, vzdevek)
        stanje = pridobi_stanje()
        stanje.dodaj_uporabnika(nov_uporabnik)
        shrani_stanje(stanje)
        nov_uporabnik.v_svojo_datoteko()
        bottle.redirect("/")    ###### TU SEM OSTAL NAZADNJE, vglavnem pregledal in dela, nisem preveril prijave ampak verjetno se ne dela

@bottle.post('/prijava/')
def prijava_post():
    uporabnisko_ime = bottle.request.forms["uporabnisko_ime"]
    geslo = bottle.request.forms["geslo"]
    if uporabnisko_ime in pridobi_stanje().uporabniki.keys():
        if geslo == pridobi_stanje().uporabniki[uporabnisko_ime].geslo:
            bottle.response.set_cookie(PISKOTEK_UPORABNISKO_IME, uporabnisko_ime, path="/", secret=SKRIVNOST)
            bottle.redirect("/doma/")
    return bottle.template("uvodna_stran.html", uporabnik="Neveljavno")

@bottle.post('/odjava/')
def odjava_post():
    bottle.response.delete_cookie(PISKOTEK_UPORABNISKO_IME, path='/')
    bottle.redirect('/')

@bottle.get('/doma/')
def doma_get():
    uporabnik = trenutni_uporabnik()
    return bottle.template('doma.html', uporabnik=uporabnik)

@bottle.get('/moji_prijatelji/')
def moji_prijatelji_get():
    igra = trenutni_uporabnik().igra
    prijatelji = trenutni_uporabnik().prijatelji
    return bottle.template('moji_prijatelji.html', prijatelji=prijatelji, igra=igra)
    

bottle.run(reloader=True, debug=True)