import bottle
import model

@bottle.get('/')
def osnovna_stran():
    return bottle.template("osnovna_stran.html")

#@bottle.post("/dodajanje-igralcev/")
#def zacni_igro():
#    igra = model.Igra(bottle.request.forms("stevilo_vrstic"))
#    return bottle.template("dodajanje-igralcev.html", igrana_igra=igra)
    
bottle.run(reloader=True, debug=True)