import time
import bottle
import model
from model import Stanje, Uporabnik, Prijatelj, Igra, Igralec, Karta, uporabnik_iz_slovarja

DATOTEKA_S_STANJEM = "stanje.json"
PISKOTEK_PRIJAVA = "prijavljen"
PISKOTEK_UPORABNISKO_IME = "uporabn"
SKRIVNOST = "psst..."

# Tu dodaj da če datoteka ne obstaja da jo nardi

stanje = model.stanje_iz_datoteke(DATOTEKA_S_STANJEM)

def trenutni_uporabnik():
    uporabnisko_ime = bottle.request.get_cookie(PISKOTEK_UPORABNISKO_IME, secret=SKRIVNOST)
    return stanje.uporabniki[uporabnisko_ime] if uporabnisko_ime else 0

def shrani():
    stanje.v_datoteko("stanje.json")

@bottle.get('/')
def osnovna_stran():
    return bottle.template("uvodna_stran.html", uporabnik=trenutni_uporabnik())

@bottle.get("/registracija/")
def registracija_get():
    return bottle.template("registracija.html", napaka=None)

@bottle.post("/registracija/")
def registracija_post():
    uporabnisko_ime = bottle.request.forms["uporabnisko_ime"]
    geslo = bottle.request.forms["geslo"]
    if uporabnisko_ime in stanje.uporabniki.keys():
        return bottle.template("registracija.html", napaka="zasedno")
    else:
        stanje.dodaj_uporabnika(Uporabnik(uporabnisko_ime, geslo))
        shrani()
        bottle.redirect("/")

@bottle.post('/prijava/')
def prijava_get():
    uporabnisko_ime = bottle.request.forms["uporabnisko_ime"]
    geslo = bottle.request.forms["geslo"]
    if uporabnisko_ime in stanje.uporabniki.keys():
        if geslo == stanje.uporabniki[uporabnisko_ime].geslo:
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
    prijatelji = trenutni_uporabnik().prijatelji
    return bottle.template('moji_prijatelji.html', prijatelji=prijatelji)
    

bottle.run(reloader=True, debug=True)