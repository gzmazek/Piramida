import bottle
import model
from model import Stanje, Uporabnik, Prijatelj, Igra, Igralec, Karta

DATOTEKA_S_STANJEM = "stanje.json"

# Tu dodaj da če datoteka ne obstaja da jo nardi

stanje = model.stanje_iz_datoteke(DATOTEKA_S_STANJEM)

def shrani():
    stanje.v_datoteko(stanje)

@bottle.get('/')
def osnovna_stran():
    return bottle.template("uvodna_stran.html")

@bottle.get("/registracija/")
def registracija_get():
    return bottle.template("registracija.html")

@bottle.post("/registracija/")
def registracija_post():
    uporabnisko_ime = bottle.request.query["uporabnisko_ime"]
    geslo = bottle.request.query["geslo"]
    stanje.dodaj_uporabnika(Uporabnik(uporabnisko_ime, geslo))
    shrani()
    bottle.redirect("/")

@bottle.get('/prijava/')
def prijava_get():
    return bottle.template("prijava.html")

#@bottle.post("/dodajanje-igralcev/")
#def zacni_igro():
#    igra = model.Igra(bottle.request.forms("stevilo_vrstic"))
#    return bottle.template("dodajanje-igralcev.html", igrana_igra=igra)
    
bottle.run(reloader=True, debug=True)