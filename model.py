from dataclasses import dataclass
import random
import json 

POZIREK = "P"
KOZAREC = "K"
PIJACE = {"pivo", "cuba-libre", "gin-tonic", "vino"}
BARVE = ["modra", "zelena", "rumena", "rdeča"]
SPIJ_DO_KONCA_IN_NAROCI_NOV_KOZAREC = "X"

############################# SPLOŠNE FUNKCIJE #############################
def sestavi_piramido(n):
    """Sestavi sezanm vrstic, kjer so karte zaprte"""
    return [[Karta(vrednost=n-j) for _ in range(2 * (j + 1))] for j in range(n)]

def koliko_pozirkov(igralec, karta):
    pozirki = 0
    for i in igralec.karte:
        if i == karta:
            pozirki += karta.vrednost
    return pozirki
############################################################################

class Karta:
    def __init__(self, stevilo=None, barva=None, odprtost=False, vrednost=1):  #Tukaj pazi da je na koncu False saj vmes preverjam tako da dam na True
        self.stevilo = (stevilo if stevilo != None else random.randrange(10))
        self.barva = (barva if barva != None else random.choice(BARVE))
        self.ali_je_odprta = odprtost
        self.vrednost = vrednost # Vrednost pomeni število požirkov
    
    def __repr__(self) -> str:
        return f"{self.stevilo}"


    def __eq__(self, other):
        return self.stevilo == other.stevilo

    def __gt__(self, other):
        return self.stevilo > other.stevilo
    
    def odpri_karto(self):  # Tukaj naredi nekaj da ni vredu če obrneš 
        self.ali_je_odprta = True
        return self

    def v_slovar(self): # To je samo, če igralec med igro zapusti spletno stran, potem bo imel moćnost nadaljuj igro in začni novo igro, ki to igro izbriše
        return {
            "stevilo": self.stevilo,
            "barva": self.barva,
            "odprtost": self.ali_je_odprta,
            "vrednost": self.vrednost
        }
    
def karta_iz_slovarja(slovar):
    return Karta(
        slovar["stevilo"],
        slovar["barva"],
        slovar["odprtost"],
        slovar["vrednost"]
    )


class Igralec: # Paziti moramo, da so igralci vsi z drugačnimi imeni, za to bo poskrbela že funkcija prijatelji
    def __init__(self, ime, pijaca, karte=[], stevilo_spitih=0, stanje_v_kozarcu=10):
        self.ime = ime
        self.pijaca = pijaca
        self.karte = karte
        self.stevilo_spitih = stevilo_spitih
        self.stanje_v_kozarcu = stanje_v_kozarcu # tukaj lahko kazneje narediš, da je stanje v kozarcu drugačno ampak zelo ni nujno

    def __eq__(self, other):
        return self.ime == other.ime
    
    def napolni_kozarec(self):
        self.stanje_v_kozarcu += 10
        return SPIJ_DO_KONCA_IN_NAROCI_NOV_KOZAREC

# Verjetno bo tu potrebno se dodat kekšne return stvari, da sprožimo neko pitje/deljenje
    def dodeli_pozirke(self, n=1):
        self.stanje_v_kozarcu -= n
        self.stevilo_spitih += n
        while self.stanje_v_kozarcu <= 0:
            self.napolni_kozarec()

    def ugiba_prvo_karto(self, barva: str): # V vmesniku bo treba vmes tu vprašat za barvo, 
        # pa nekje mores dodat da te opozori ce se zatipkas/naredi da lahko izbiras
        """Za argument zapišemo barvo, ki jo igralec ugiba"""
        self.karte.append(Karta(odprtost=True))
        if barva == self.karte[-1].barva:
            pass
        else:
            self.dodeli_pozirke(self.karte[-1].vrednost) # !!!!! Tukaj namesto tega messega printanja samo das return pa tisto funkcijo s katero sprozis sporocilo
    
    def ugiba_drugo_karto(self, vecje_manjse: bool):
        """Za argument zapiše True, če bo naslednja karta STROGO večja in False drugače. Če se karta ponovi, igralec vedno pije."""
        self.karte.append(Karta(odprtost=True))
        if self.karte[-1] > self.karte[-2]:
            pass
        else:
            self.dodeli_pozirke(self.karte[-1].vrednost)

    def ugiba_tretjo_karto(self, vmes: bool):
        """Za argument zapiše True, če bo karta točno med obema trenutnima kartama. Ponovno se karta ne sme ponoviti."""
        a = self.karte[0]
        b = self.karte[1]
        self.karte.append(Karta(odprtost=True))
        nova = self.karte[-1]
        if (a < nova and nova < b) or (b < nova and nova < a):
            pass
        else:
            self.dodeli_pozirke(self.karte[-1].vrednost)
        
    def v_slovar(self):
        return {
            "ime": self.ime,
            "pijaca": self.pijaca,
            "karte": [karte.v_slovar() for karte in self.karte],
            "popito": self.stevilo_spitih,
            "stanje": self.stanje_v_kozarcu
        }

def igralec_iz_slovarja(slovar):
    return Igralec(
        slovar["ime"],
        slovar["pijaca"],
        [karta_iz_slovarja(sl) for sl in slovar["karte"]],
        slovar["popito"],
        slovar["stanje"]
    )
    
class Igra:
    def __init__(self, n=4, igralci=[], piramida=0, prva_zaprta_karta=None):
        self.velikost_piramide = n
        self.igralci = igralci
        self.piramida = (sestavi_piramido(n) if piramida == 0 else piramida)
        self.prva_zaprta_karta = ([n - 1, 0] if prva_zaprta_karta == None else prva_zaprta_karta) # Prva zaprta pomeni, da je to karta, ki jo moramo nslednjo odpreti
        self.vse_karte_igralcev = set() # To se naredi da se ob tem ko nardis igro naredi

    def dodaj_igralca(self, ime):
        self.igralci.append(Igralec(ime))

    def odpri_naslednjo_karto(self):
        """Funkcija odpre nasledno karto, spremeni self.prva_zaprta_karta in vrne karto, ki smo jo odprli."""
        n = self.velikost_piramide
        karta_ki_jo_odpiram = self.piramida[self.prva_zaprta_karta[0]][self.prva_zaprta_karta[1]].odpri_karto()
        if self.prva_zaprta_karta == [0, 1]:
            self.prva_zaprta_karta = None ## !!! TUKAJ MORAŠ IGRO ZAKLJUČITI POTEM KO SPIJEJO tisti en loop se naj še naredi potem pa konec
        elif 2 * self.prva_zaprta_karta[0] + 1 == self.prva_zaprta_karta[1]:
            self.prva_zaprta_karta = [self.prva_zaprta_karta[0] - 1, 0]
        else:
            self.prva_zaprta_karta[1] += 1
        return karta_ki_jo_odpiram

    def preveri_kdo_dobi_pozirke(self, karta: Karta):
        """Funkcija vzame karto in vrne slovar z elementi {Igralec: požirki}. Tukaj ni važno, ali se karta deli ali pije."""
        return {igralec: koliko_pozirkov(igralec, karta) for igralec in self.igralci}
    
    def naredi_potezo(self): # Ta je verjetno malo manj uporabna
        """Funkcija odpre naslednjo karto in vsem doda koliko mora narediti vsak požirkov"""
        ali_se_deli = self.prva_zaprta_karta[1] > self.prva_zaprta_karta[0] # True, če se mora deliti
        slovar_pozirkov = self.preveri_kdo_dobi_pozirke(self.odpri_naslednjo_karto())
        return (ali_se_deli, slovar_pozirkov)
    
    def podeli_pozirke(self, igralec_ki_dobi: Igralec, st_pozirkov: int):
        for i in self.igralci:
            if i == igralec_ki_dobi:
                i.dodeli_pozirke(st_pozirkov)
    
    def v_slovar(self):
        return {
            "igralci": [igralec.v_slovar() for igralec in self.igralci],
            "piramida": list(map(lambda seznam: list(map(lambda karta: karta.v_slovar(), seznam)), self.piramida)), # Ta stvar je zlo grda poglej ce sploh dela pa jo polesaj
            "prva_zaprta_karta": self.prva_zaprta_karta, # sicer ni potrebno ker se lahko izrazi
        }

def igra_iz_slovarja(slovar: dict): # To stvar boš moral še zelo preveriti ker ne vem če dela prav!!
    return Igra(
        len(slovar["piramida"]),
        [igralec_iz_slovarja(sl) for sl in slovar["igralci"]],
        [list(map(karta_iz_slovarja, vrstica)) for vrstica in slovar["piramida"]],
        slovar["prva_zaprta_karta"]
    )

class Prijatelj: # Ta prijatelj se potem spremeni v Igralec, pri njem boš še lahko dodal koliko je spil v življenju, kaj naraje pije, komu je največ podelil...
    def __init__(self, ime, e_mail, pozirkov_spite_pijace={}):
        self.ime = ime
        self.e_mail = e_mail
        self.pozirkov_spite_pijace = pozirkov_spite_pijace
    
    def v_slovar(self):
        return {
            "ime": self.ime,
            "e_mail": self.e_mail,
            "pozirkov_spite_pijace": self.pozirkov_spite_pijace
        }
    
def prijatelj_iz_slovarja(slovar):
    return Prijatelj(
        slovar["ime"],
        slovar["e_mail"],
        slovar["pozirkov_spite_pijace"]
    )
    
class Uporabnik: 
    def __init__(self, igra=None, prijatelji=set()):
        self.igra = igra # Igralec ima lahko samo eno on-going igro, bilo bi neuporabno in nesmiselno jih imeti več
        self.prijatelji = prijatelji
    
    def dodaj_prijatelja(self, prijatelj: Prijatelj):
        self.prijatelji.add(prijatelj)

    def odstrani_prijatelja(self, prijatelj):
        self.prijatelji.remove(prijatelj)

    def v_slovar(self):
        return {
            "igra": self.igra.v_slovar(),
            "prijatelji": [prijatelj.v_slovar() for prijatelj in self.prijatelji]
        }
    
def uporabnik_iz_slovarja(slovar):
    return Uporabnik(
        igra_iz_slovarja(slovar["igra"]),
        [prijatelj_iz_slovarja(prijatelj) for prijatelj in slovar["prijatelji"]]
    )

class Stanje:
    def __init__(self, uporabniki=[]):
        self.uporabniki = uporabniki
    
    def dodaj_uporabnika(self, uporabnik: Uporabnik):
        self.uporabniki.append(uporabnik)
    
    def v_slovar(self):
        return {
            "uporabniki": [uporabnik.v_slovar() for uporabnik in self.uporabniki]
        }

    def v_datoteko(self, ime_datoteke):
        with open(ime_datoteke, "w") as f:
            json.dump(self.v_slovar(), f, ensure_ascii=False, indent=2)

##### Dodaj še stanje iz slovarja !!!