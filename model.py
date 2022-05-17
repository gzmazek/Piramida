from dataclasses import dataclass
import random

POZIREK = "P"
KOZAREC = "K"
PIJACE = {"pivo", "cuba-libre", "gin-tonic", "vino"}
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

# Karte so pri tej igri vedno naključne, tudi ponavljajo se lahko, kasneje lahko dodaš
# še tiste posebne karte, zdaj pa samo 1 - 9 in barve

class Karta:
    def __init__(self, odprtost=False, vrednost=1):  #Tukaj pazi da je na koncu False saj vmes preverjam tako da dam na True
        self.stevilo = random.randrange(10)
        self.barva = random.choice(["modra", "zelena", "rumena", "rdeča"])
        self.ali_je_odprta = odprtost
        self.vrednost = vrednost # Vrednost pomeni število požirkov

    def __eq__(self, other):
        return self.stevilo == other.stevilo

    def __gt__(self, other):
        return self.stevilo > other.stevilo
    
    def __repr__(self):
        if not self.ali_je_odprta:
            return "X"
        else:
            return f"{self.stevilo}" # Tu naredi kasneje da se kar barva pokaže tako

# Ta del nisem prepričan kaj moram naredit, ker ne vem ali bo moral 
# raisat kaki exception in kaj narediti, če je karte že odprta
# !! res bi lahko pogledal še kak se raise svoj exception

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


class Igralec: # Paziti moramo, da so igralci vsi z drugačnimi imeni, za to bo poskrbela že funkcija prijatelji
    def __init__(self, ime):
        self.ime = ime
        self.karte = []
        self.stevilo_cakajocih_pozirkov = 0
        self.stevilo_spitih = 0
        self.stevilo_nepodeljenih = 0 # To bom kasneje izločil, tako kot eno od zgornjih, igralec potrebuje le stanje v kozarcu in število spitih
        self.stanje_v_kozarcu = 10 # tukaj lahko kazneje narediš, da je stanje v kozarcu drugačno ampak zelo ni nujno

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
    
#    def v_slovar(self):
#        return {
#           ""
#        }

# Tukaj boš moral dodati __repr__, da lahko piramido predstavim takšno kot je
# Pa tudi igralce, vsaj za tekstovni vmesnik

class Igra:
    def __init__(self, n=4):
        self.velikost_piramide = n
        self.igralci = []
        self.piramida = sestavi_piramido(n)
        self.prva_zaprta_karta = [n - 1, 0] # Prva zaprta pomeni, da je to karta, ki jo moramo nslednjo odpreti
        self.vse_karte_igralcev = set()

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

        for i in self.igralci:
            prikaz += f"Igralec {i.ime}: Karte: {i.karte}. Narediti mora {i.stevilo_cakajocih_pozirkov} požirkov. Deli jih lahko še {i.stevilo_nepodeljenih}. \n"

        return prikaz

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
        if ali_se_deli:
            for igralec in self.igralci:
                igralec.stevilo_nepodeljenih += slovar_pozirkov[igralec]
        else:
            for igralec in self.igralci:
                igralec.stevilo_cakajocih_pozirkov += slovar_pozirkov[igralec]
        print(self) # Ta del je samo za zdaj, ko igram v terminalu in preverjam delovanje funkcij
    
    def podeli_pozirke(self, igralec_ki_dobi: Igralec, st_pozirkov: int):
        for i in self.igralci:
            if i == igralec_ki_dobi:
                i.dodeli_pozirke(st_pozirkov)


class Prijatelj: # Ta prijatelj se potem spremeni v Igralec, pri njem boš še lahko dodal koliko je spil v življenju, kaj naraje pije, komu je največ podelil...
    def __init__(self, ime, e_mail):
        self.ime = ime
        self.e_mail = e_mail
        self.pozirkov_spite_pijace = {}
    
class Uporabnik: 
    def __init__(self, igra=None):
        self.igra = igra # Igralec ima lahko samo eno on-going igro, bilo bi neuporabno in nesmiselno jih imeti več
        self.prijatelji = set()
    
    def dodaj_prijatelja(self, prijatelj: Prijatelj):
        self.prijatelji.add(prijatelj)

    def odstrani_prijatelja(self, prijatelj):
        self.prijatelji.remove(prijatelj)

#############################################
#Ta del kode je samo za preizkušanje funkcij#
#############################################

poskusna_igra = Igra(4)

poskusna_igra.dodaj_igralca("Vita")
poskusna_igra.dodaj_igralca("Gal")
poskusna_igra.dodaj_igralca("Maša")

print(poskusna_igra)

poskusna_igra.igralci[0].ugiba_prvo_karto("modra")
poskusna_igra.igralci[1].ugiba_prvo_karto("modra")
poskusna_igra.igralci[2].ugiba_prvo_karto("modra")

print(poskusna_igra)

poskusna_igra.igralci[0].ugiba_drugo_karto(True)
poskusna_igra.igralci[1].ugiba_drugo_karto(True)
poskusna_igra.igralci[2].ugiba_drugo_karto(True)

print(poskusna_igra)

poskusna_igra.igralci[0].ugiba_tretjo_karto(True)
poskusna_igra.igralci[1].ugiba_tretjo_karto(True)
poskusna_igra.igralci[2].ugiba_tretjo_karto(True)

print(poskusna_igra)
