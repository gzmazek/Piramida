from dataclasses import dataclass
import random

POŽIREK = "P"
KOZAREC = "K"

# Spremenil bom raje v piramido oblike takšne, da se lahko sprehajam po piramidi
# ko odpiram kart po vrsti, torej da se skupaj držijo iste vrstice dveh piramid

def sestavi_piramido(n):
    """Sestavi sezanm vrstic, kjer so karte zaprte"""
    return [[Karta() for _ in range(2 * (j + 1))] for j in range(n)]


# Karte so pri tej igri vedno naključne, tudi ponavljajo se lahko, kasneje lahko dodaš
# še tiste posebne karte, zdaj pa samo 1 - 9 in barve

class Karta:
    def __init__(self, odprtost=True):
        self.stevilo = random.randrange(10)
        self.barva = random.choice(["modra", "zelena", "rumena", "rdeča"])
        self.ali_je_odprta = odprtost
    
    def __repr__(self):
        if not self.ali_je_odprta:
            return "X"
        else:
            return f"{self.barva} {self.stevilo}" # Tu naredi kasneje da se kar barva pokaže tako

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

# Verjetno bo tu potrebno se dodat kekšne return stvari, da sprožimo neko pitje/deljenje
 
    def dodaj_prvo_karto(self, barva: str): # V vmesniku bo treba vmes tu vprašat za barvo, 
        # pa nekje mores dodat da te opozori ce se zatipkas/naredi da lahko izbiras
        self.karte.append(Karta())
        if barva == self.karte[-1].barva:
            pass
        else:
            self.stevilo_cakajocih_pozirkov += 1
            return POŽIREK
    
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
    
#    def odpri_naslednjo_karto(self):
#        karta = izberi_nakljucno_karto()

print(sestavi_piramido(3))