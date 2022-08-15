import bottle
import model
from model import CAKAJOCA_PROSNJA, Stanje, Uporabnik, Igra, Igralec, Karta, uporabnik_iz_slovarja, uporabnik_iz_svoje_datoteke

DATOTEKA_S_STANJEM = "stanje.json"
PISKOTEK_PRIJAVA = "prijavljen"
PISKOTEK_UPORABNISKO_IME = "uporabnik"
SKRIVNOST = "psst..."

# Tu dodaj da če datoteka ne obstaja da jo nardi

def trenutni_uporabnik():
    uporabnisko_ime = bottle.request.get_cookie(PISKOTEK_UPORABNISKO_IME, secret=SKRIVNOST)
    return uporabnik_iz_svoje_datoteke(uporabnisko_ime) if uporabnisko_ime else 0

def shrani_uporabnika(uporabnik):
    uporabnik.v_svojo_datoteko() #Shrani od uporabnika v njegovo datoteko

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

@bottle.get('/moji_prijatelji/<napaka>')
def moji_prijatelji_get(napaka):
    uporabnik = trenutni_uporabnik()
    uporabnisko_ime = uporabnik.uporabnisko_ime
    igra = uporabnik.igra
    stanje = pridobi_stanje()
    prijatelji = [par[0] for par in stanje.uporabniki[uporabnisko_ime].prijatelji_in_deljenje.items() if par[1] != CAKAJOCA_PROSNJA] # Tu lahko ful polešaš še s filter..., da ni dveh istih vrstic
    pending_prosnje = [par[0] for par in stanje.uporabniki[uporabnisko_ime].prijatelji_in_deljenje.items() if par[1] == CAKAJOCA_PROSNJA] 
    prosnje = stanje.uporabniki[uporabnisko_ime].prosnje
    return bottle.template('moji_prijatelji.html', prijatelji=prijatelji, igra=igra, pending_prosnje=pending_prosnje, prosnje=prosnje, napaka=napaka)

@bottle.post('/poslji_prosnjo/')
def poslji_prosnjo_post():
    uporabnisko_ime = bottle.request.forms["uporabnisko_ime"]
    if uporabnisko_ime == trenutni_uporabnik().uporabnisko_ime:
        bottle.redirect('/moji_prijatelji/lonely')
    elif uporabnisko_ime in pridobi_stanje().uporabniki[trenutni_uporabnik().uporabnisko_ime].prosnje:
        sprejmi_prosnjo_post(uporabnisko_ime)
    elif uporabnisko_ime in pridobi_stanje().uporabniki.keys():
        stanje = pridobi_stanje()
        stanje.uporabniki[uporabnisko_ime].dodaj_prosnjo(trenutni_uporabnik().uporabnisko_ime)
        stanje.uporabniki[trenutni_uporabnik().uporabnisko_ime].dodaj_prosnjo_med_prijatelje(uporabnisko_ime)
        shrani_stanje(stanje)
        bottle.redirect('/moji_prijatelji/none') # tu bi se znebil tega none/// V redirect lahko dodam da ni tega prijatelja neko kodo, nevem 001 recimo ta prijatelj ne obstaja
    else:
        bottle.redirect('/moji_prijatelji/no-user')

@bottle.post('/izbrisi_prosnjo/<poslana_prosnja>')
def izbrisi_prosnjo_post(poslana_prosnja):
    stanje = pridobi_stanje()
    stanje.uporabniki[poslana_prosnja].izbrisi_prosnjo(trenutni_uporabnik().uporabnisko_ime)
    stanje.uporabniki[trenutni_uporabnik().uporabnisko_ime].prijatelji_in_deljenje.pop(poslana_prosnja)
    shrani_stanje(stanje)
    bottle.redirect('/moji_prijatelji/0')

@bottle.post('/sprejmi_<mogoce_prijatelj>/')
def sprejmi_prosnjo_post(mogoce_prijatelj):
    stanje = pridobi_stanje()
    uporabnik = trenutni_uporabnik().uporabnisko_ime
    stanje.uporabniki[mogoce_prijatelj].prijatelji_in_deljenje[uporabnik] = [0, 0]
    stanje.uporabniki[uporabnik].izbrisi_prosnjo_in_dodaj_prijatelja(mogoce_prijatelj)
    shrani_stanje(stanje)
    dodan_prijatelj_uporabnik = uporabnik_iz_svoje_datoteke(uporabnik).dodaj_prijatelja(mogoce_prijatelj)
    dodan_prijatelj_prijatelj = uporabnik_iz_svoje_datoteke(mogoce_prijatelj).dodaj_prijatelja(uporabnik)
    dodan_prijatelj_uporabnik.v_svojo_datoteko()
    dodan_prijatelj_prijatelj.v_svojo_datoteko()
    bottle.redirect('/moji_prijatelji/0')

@bottle.post('/izbrisi_prijatelja_<prijatelj>/')
def izbrisi_prijatelja(prijatelj):
    stanje = pridobi_stanje()
    uporabnik = trenutni_uporabnik().uporabnisko_ime
    stanje.uporabniki[uporabnik].prijatelji_in_deljenje.pop(prijatelj)
    stanje.uporabniki[prijatelj].prijatelji_in_deljenje.pop(uporabnik)
    shrani_stanje(stanje)
    dodan_prijatelj_uporabnik = uporabnik_iz_svoje_datoteke(uporabnik).odstrani_prijatelja(prijatelj)
    dodan_prijatelj_prijatelj = uporabnik_iz_svoje_datoteke(prijatelj).odstrani_prijatelja(uporabnik)
    dodan_prijatelj_uporabnik.v_svojo_datoteko()
    dodan_prijatelj_prijatelj.v_svojo_datoteko()
    bottle.redirect('/moji_prijatelji/0') # pred to funkcijo naredi, da te najprej tisti gumb nekam preusmeri im potem tam gumb na to funkcjio, ki realno zbriše stvari

@bottle.get('/nova_igra')
def nova_igra():
    uporabnik = trenutni_uporabnik()
    igra = uporabnik.igra
    return bottle.template("nova_igra.html", igra=igra)

@bottle.post('/zacni_igro_<i>/')
def zacni_igro_i(i):
    uporabnik = trenutni_uporabnik()
    velikost = int(i) # tu lahko daš da v naslovu zahteva int
    uporabnik.zacni_igro(velikost)
    shrani_uporabnika(uporabnik)
    dodaj_prijatelja(uporabnik.uporabnisko_ime)
    
@bottle.post('/dodaj_prijatelja_<prijatelj>')
def dodaj_prijatelja(prijatelj):
    uporabnik = trenutni_uporabnik()
    izbrani_igralci = ["ME"]
    return bottle.template("nova_igra_igralci", izbrani_igralci = izbrani_igralci)


bottle.run(reloader=True, debug=True)