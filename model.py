from dataclasses import dataclass
import random


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

    def odpri_karto(self):
        if not self.ali_je_odprta:
            self.ali_je_odprta = True


class Igralec:
    def __init__(self, ime):
        self.ime = ime
        self.karte = []
    
    def dodaj_karto(self, karta: Karta):
        self.karte.append(karta)

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