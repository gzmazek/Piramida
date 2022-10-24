import random
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
    uporabnik.v_svojo_datoteko()

def pridobi_stanje():
    return model.stanje_iz_datoteke(DATOTEKA_S_STANJEM)

def shrani_stanje(stanje):
    stanje.v_datoteko(DATOTEKA_S_STANJEM)

@bottle.route('/img/<filename>')
def server_static(filename):
    return bottle.static_file(filename, root='./img')

@bottle.get("/static/<ime_datoteke:path>")
def css(ime_datoteke):
    return bottle.static_file(ime_datoteke, root="views")

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
    elif "_" in uporabnisko_ime or "-" in uporabnisko_ime:
        return bottle.template("registracija.html", napaka="znaki")
    else:
        nov_uporabnik = Uporabnik(uporabnisko_ime, geslo, email, vzdevek)
        stanje = pridobi_stanje()
        stanje.dodaj_uporabnika(nov_uporabnik)
        shrani_stanje(stanje)
        nov_uporabnik.v_svojo_datoteko()
        bottle.redirect("/") 

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
    velikost = int(i)
    uporabnik.zacni_igro(velikost)
    shrani_uporabnika(uporabnik)
    dodaj_odstrani_prijatelja(uporabnik.uporabnisko_ime)
    
@bottle.post('/dodaj_odstrani_prijatelja_<prijatelj>')
def dodaj_odstrani_prijatelja(prijatelj):
    uporabnik = trenutni_uporabnik()
    izbrani_igralci = uporabnik.igra.igralci
    if prijatelj in izbrani_igralci:
        uporabnik.igra.izbrisi_igralca(prijatelj)
    else:
        uporabnik.igra.dodaj_igralca(prijatelj)
    shrani_uporabnika(uporabnik)
    bottle.redirect('/dodan_prijatelj')

@bottle.get('/dodan_prijatelj')
def dodan_prijatelj_get():
    uporabnik = trenutni_uporabnik()
    prijatelji = uporabnik.prijatelji
    izbrani_igralci = uporabnik.igra.igralci.keys()
    shrani_uporabnika(uporabnik)
    return bottle.template("nova_igra_igralci", prijatelji = prijatelji, izbrani_igralci = izbrani_igralci)

@bottle.get('/deljenje_kart')
def deljenje_kart():
    uporabnik = trenutni_uporabnik()
    igra = uporabnik.igra
    igralci = igra.igralci.values()
    vsi_odprti = True
    for igralec in igralci:
        if len(igralec.karte) != 3:
            vsi_odprti = False
            break
    return bottle.template("deljenje_kart.html", igralci = igralci, vsi_odprti=vsi_odprti)

@bottle.post('/ugiba_<stevilo_kdo_kaj>')
def ugiba_prvic(stevilo_kdo_kaj):
    stevilo_ugibanj = stevilo_kdo_kaj.split("_")[0]
    uporabnisko_ime = stevilo_kdo_kaj.split("_")[1]
    lastnost = stevilo_kdo_kaj.split("_")[2]
    uporabnik = trenutni_uporabnik()
    igra = uporabnik.igra
    if int(stevilo_ugibanj) == 1:
        igra.igralci[uporabnisko_ime].ugiba_prvo_karto(lastnost)
    elif int(stevilo_ugibanj) == 2:
        igra.igralci[uporabnisko_ime].ugiba_drugo_karto(lastnost)
    elif int(stevilo_ugibanj) == 3:
        igra.igralci[uporabnisko_ime].ugiba_tretjo_karto(lastnost)
    shrani_uporabnika(uporabnik)
    bottle.redirect('/deljenje_kart')

@bottle.post('/zacetek_igre')
def zacetek_igre():
    bottle.redirect('/piramida_igra_stanje')

@bottle.get('/piramida_igra_stanje')
def piramida_igra_stanje():
    uporabnik = trenutni_uporabnik()
    igra = uporabnik.igra
    piramida = igra.piramida
    igralci = igra.igralci
    return bottle.template("base_piramida_igra.html", piramida=piramida, igralci=igralci)

@bottle.post('/odpri_naslednjo_karto')
def odpri_naslednjo_karto_post():
    uporabnik = trenutni_uporabnik()
    igra = uporabnik.igra
    slovar_pozirkov = igra.naredi_potezo()
    if not slovar_pozirkov[0]: #Tu se potem pije, tu lahko potem narediš možnost, da če nima noben požirkov, se odpre nova karta; kasneje za update
        link = "/piramida_igra_pitje_0"
        for par in slovar_pozirkov[1].items():
            if par[1] != 0:
                link += f"_{par[0]}-{par[1]}" ### !!! uporabnisko ime ne sme imeti _ ali - v imenu!!! poglej po celi kodi se
        shrani_uporabnika(uporabnik)
        bottle.redirect(f'{link}')
    else:
        link = "/piramida_igra_deljenje_0"
        for par in slovar_pozirkov[1].items():
            if par[1] != 0:
                link += f"_{par[0]}-{par[1]}" ### !!! uporabnisko ime ne sme imeti _ ali - v imenu!!! poglej po celi kodi se
        shrani_uporabnika(uporabnik)
        bottle.redirect(f'{link}')

@bottle.get('/piramida_igra_pitje_<slovar_pitja>')
def piramida_igra_pitje_get(slovar_pitja):
    uporabnik = trenutni_uporabnik()
    igra = uporabnik.igra 
    igralci = igra.igralci.values()
    prva_zaprta = igra.prva_zaprta_karta
    zadnja_odprta = [prva_zaprta[0] - 1, (prva_zaprta[0] + 1) * 2] if prva_zaprta[1] == 0 else [prva_zaprta[0], prva_zaprta[1] - 1]
    odpirajoca_karta = igra.piramida[zadnja_odprta[0]][zadnja_odprta[1]]
    if slovar_pitja == "0":
        bottle.redirect('/piramida_igra_stanje')
    else:
        seznam_pitja = slovar_pitja.lstrip("0_").split("_")
        dict_pitja = {}
        for item in seznam_pitja:
            dict_pitja[item.split("-")[0]] = item.split("-")[1]
        for igralec in igralci:
            if igralec.ime not in dict_pitja.keys():
                dict_pitja[igralec.ime] = 0
        return bottle.template('piramida_igra_pitje.html', slovar_pitja=slovar_pitja, igralci=igralci, odpirajoca_karta=odpirajoca_karta, dict_pitja=dict_pitja)

@bottle.post('/piramida_odstej_pozirke_<slovar_pitja>')
def piramida_odstej_pozirke(slovar_pitja):
    uporabnik = trenutni_uporabnik()
    igra = uporabnik.igra
    seznam_pitja = slovar_pitja.lstrip("0_").split("_")
    for item in seznam_pitja:
        item = item.split("-")
        igra.podeli_pozirke(item[0], int(item[1]))
    shrani_uporabnika(uporabnik)
    bottle.redirect('/piramida_igra_stanje')

@bottle.get('/piramida_igra_deljenje_<slovar_deljenja>')
def piramida_igra_deljenje_get(slovar_deljenja):
    uporabnik = trenutni_uporabnik()
    igra = uporabnik.igra
    igralci = igra.igralci.values()
    prva_zaprta = igra.prva_zaprta_karta
    zadnja_odprta = [prva_zaprta[0] + 1, -1] if prva_zaprta[1] == 0 else [prva_zaprta[0], prva_zaprta[1] - 1]
    odpirajoca_karta = igra.piramida[zadnja_odprta[0]][zadnja_odprta[1]]
    if slovar_deljenja == "0":
        bottle.redirect('/piramida_igra_stanje')
    else:
        seznam_deljenja = slovar_deljenja.lstrip("0_").split("_")
        random.shuffle(seznam_deljenja)
        dict_deljenja = {}
        for item in seznam_deljenja:
            dict_deljenja[item.split("-")[0]] = item.split("-")[1]
        for igralec in igralci:
            if igralec.ime not in dict_deljenja.keys():
                dict_deljenja[igralec.ime] = 0
        zadnji = seznam_deljenja.pop()
        if zadnji[-1] != "1":
            delilec = zadnji.split("-")[0]
            novo_stevilo = int(zadnji.split("-")[1]) - 1
            seznam_deljenja.append(f"{delilec}-{str(novo_stevilo)}")
            nov_link = "piramida_igra_deljenje_0_" + "_".join(seznam_deljenja)
            return bottle.template('piramida_igra_deljenje.html',igralci=igralci, delilec=delilec, nov_link=nov_link, odpirajoca_karta=odpirajoca_karta, dict_deljenja=dict_deljenja)
        elif zadnji[-1] == "1":
            delilec = zadnji.split("-")[0]
            if len(seznam_deljenja) == 0:
                nov_link = "piramida_igra_deljenje_0"
            else:
                nov_link = "piramida_igra_deljenje_0_" + "_".join(seznam_deljenja)
            return bottle.template('piramida_igra_deljenje.html',igralci=igralci, delilec=delilec, nov_link=nov_link, odpirajoca_karta=odpirajoca_karta, dict_deljenja=dict_deljenja)

@bottle.post('/podeli_<igralec_link>')
def podeli_pozirek_post(igralec_link):
    uporabnik = trenutni_uporabnik()
    igra = uporabnik.igra
    igralec = igralec_link.split("_", 1)[0]
    link = igralec_link.split("_", 1)[1]
    igra.podeli_pozirke(igralec, 1)
    shrani_uporabnika(uporabnik)
    bottle.redirect(f"/{link}")

@bottle.post('/zakljuci_igro')
def zakljuci_igro_post():
    #Tukaj še naredi da se ti shranijo požirki nekam drugam v stanje.json
    bottle.redirect('/doma/')


bottle.run(reloader=True, debug=True)