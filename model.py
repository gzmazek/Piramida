from dataclasses import dataclass


@dataclass
class Karta:
    stevilo: int
    barva: str
    ali_je_odprta: bool

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
