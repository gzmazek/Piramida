from dataclasses import dataclass
import random

POZIREK = "P"
KOZAREC = "K"

# Spremenil bom raje v piramido oblike takšne, da se lahko sprehajam po piramidi
# ko odpiram kart po vrsti, torej da se skupaj držijo iste vrstice dveh piramid

def sestavi_piramido(n):
    """Sestavi sezanm vrstic, kjer so karte zaprte"""
    return [[Karta() for _ in range(2 * (j + 1))] for j in range(n)]


# Karte so pri tej igri vedno naključne, tudi ponavljajo se lahko, kasneje lahko dodaš
# še tiste posebne karte, zdaj pa samo 1 - 9 in barve

class Karta:
    def __init__(self, odprtost=True, vrednost=1):  #Tukaj pazi da je na koncu False saj vmes preverjam tako da dam na True
        self.stevilo = random.randrange(10)
        self.barva = random.choice(["modra", "zelena", "rumena", "rdeča"])
        self.ali_je_odprta = odprtost
        self.vrednost = vrednost # Vrednost pomeni število požirkov
    
    def __repr__(self):
        if not self.ali_je_odprta:
            return "X"
        else:
            return f"{self.stevilo}" # Tu naredi kasneje da se kar barva pokaže tako

# Ta del nisem prepričan kaj moram naredit, ker ne vem ali bo moral 
# raisat kaki exception in kaj narediti, če je karte že odprta
# !! res bi lahko pogledal še kak se raise svoj exception

    def odpri_karto(self):
        if not self.ali_je_odprta:
            self.ali_je_odprta = True


class Igralec:
    def __init__(self, ime):
        self.ime = ime
        self.karte = []
        self.stevilo_cakajocih_pozirkov = 0
        self.stevilo_spitih = 0

# Verjetno bo tu potrebno se dodat kekšne return stvari, da sprožimo neko pitje/deljenje
 
    def dodaj_prvo_karto(self, barva: str): # V vmesniku bo treba vmes tu vprašat za barvo, 
        # pa nekje mores dodat da te opozori ce se zatipkas/naredi da lahko izbiras
        self.karte.append(Karta())
        if barva == self.karte[-1].barva:
            pass
        else:
            self.stevilo_cakajocih_pozirkov += 1
            return POZIREK
    
#    def dodaj_drugo_karto(self, vecje_manjse):
#        self.karte.append(Karta())
#
#    def dodaj_tretjo_karto(self, barva):
#        self.karte.append(Karta())

# Tukaj boš moral dodati __repr__, da lahko piramido predstavim takšno kot je
# Pa tudi igralce, vsaj za tekstovni vmesnik

class Igra:
    def __init__(self, n=4):
        self.igralci = []
        self.piramida = sestavi_piramido(n)
        self.prva_zaprta_karta = [0,0] # Prva zaprta pomeni, da je to karta, ki jo moramo nslednjo odpreti
    
    def __repr__(self): # To boš še moral verjetno veliko spremeniti, da bo kot igra zahteva
        prikaz = ""
        prva_piramida = "Piramida za pitje: \n \n"
        druga_piramida = "Piramida za deljenje: \n \n"
        sirina = len(self.piramida)

        for i in range(sirina):
            prva_piramida += f"Piješ {sirina - i}:" + " " * (sirina - i) + " ".join(map(str, self.piramida[i][:(i + 1)])) + "\n"
        prikaz += prva_piramida
        
        prikaz += "_" * 2 * (sirina + 1) + "\n" * 2 # To je zdaj samo za med developmentom

        for i in range(sirina):
            druga_piramida += f"Deliš {sirina - i}:" + " " * (sirina - i) + " ".join(map(str, self.piramida[i][(i + 1):])) + "\n"
        prikaz += druga_piramida

        return prikaz

#    def odpri_naslednjo_karto(self):
#        karta = izberi_nakljucno_karto() Tukaj daj return karta, da lahko potem v funkciji vseeno pogledaš kdo ima karto

print(Igra(7))