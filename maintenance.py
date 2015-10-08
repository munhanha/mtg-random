# -*- coding: utf-8 -*-

from models import cartas_mtg


def check_DB(request):
	cards = cartas_mtg.all().filter('stock > ', 0)
	
	comum  = 0
	incomum = 0
	rara = 0
	
	um = 0
	dois = 0
	tres = 0
	quatro = 0
	cinco = 0
	seis = 0
	sete = 0
	oito = 0
	nove = 0
	dez = 0
	onze = 0
	doze = 0
	treze = 0
	
	um_stock = 0
	dois_stock = 0
	tres_stock = 0
	quatro_stock = 0
	cinco_stock = 0
	seis_stock = 0
	sete_stock = 0
	oito_stock = 0
	nove_stock = 0
	dez_stock = 0
	onze_stock = 0
	doze_stock = 0
	treze_stock = 0
	
	for card in cards:
		raridade = card.raridade
		stock = card.stock
		importancia = card.importance
		
		if raridade == "Rare" or raridade == "Mytic":
			rara += stock
		elif raridade == "Uncommon":
			incomum += stock
		elif raridade == "Common":
			comum += stock
			
		if importancia == 1:
			um = um + 1
			um_stock = um_stock + card.stock
		elif importancia == 2:
			dois = dois +1
			dois_stock = dois_stock + card.stock
		elif importancia == 3:
			tres = tres +1
			tres_stock = tres_stock + card.stock
		elif importancia == 4:
			quatro = quatro +1
			quatro_stock = quatro_stock + card.stock
		elif importancia == 5:
			cinco = cinco +1
			cinco_stock = cinco_stock + card.stock
		elif importancia == 6:
			seis = seis +1
			seis_stock = seis_stock + card.stock
		elif importancia == 7:
			sete = sete +1
			sete_stock = sete_stock + card.stock
		elif importancia == 8:
			oito = oito +1	
			oito_stock = oito_stock + card.stock
		elif importancia == 9:
			nove = nove +1	
			nove_stock = nove_stock + card.stock
		elif importancia == 10:
			dez = dez +1	
			dez_stock = dez_stock + card.stock
		elif importancia == 11:
			onze = onze +1	
			onze_stock = onze_stock + card.stock
		elif importancia == 12:
			doze = doze +1	
			doze_stock = doze_stock + card.stock
		elif importancia == 13:
			treze = treze +1	
			treze_stock = treze_stock + card.stock
			
	toReturn = "Comum = " + str(comum) + " Incomum = " + str(incomum) + " Rara = " + str(rara)
	
	toReturn = toReturn+ "<p></p>"

	toReturn = toReturn + "IMPORTANCIAS"
	
	toReturn = toReturn+ "<p></p>"
	
	toReturn = toReturn+ "1 = " + str(um) + " <b>//</b> Stock = " + str(um_stock) + "<p></p>"
	toReturn = toReturn+ "2 = " + str(dois) + " <b>//</b> Stock = " + str(dois_stock) + "<p></p>"
	toReturn = toReturn+ "3 = " + str(tres) + " <b>//</b> Stock = " + str(tres_stock) + "<p></p>"
	toReturn = toReturn+ "4 = " + str(quatro) + " <b>//</b> Stock = " + str(quatro_stock) + "<p></p>"
	toReturn = toReturn+ "5 = " + str(cinco) + " <b>//</b> Stock = " + str(cinco_stock) + "<p></p>"
	toReturn = toReturn+ "6 = " + str(seis) + " <b>//</b> Stock = " + str(seis_stock) + "<p></p>"
	toReturn = toReturn+ "7 = " + str(sete) + " <b>//</b> Stock = " + str(sete_stock) + "<p></p>"
	toReturn = toReturn+ "8 = " + str(oito) + " <b>//</b> Stock = " + str(oito_stock) + "<p></p>"
	toReturn = toReturn+ "9 = " + str(nove) + " <b>//</b> Stock = " + str(nove_stock) + "<p></p>"
	toReturn = toReturn+ "10 = " + str(dez) + " <b>//</b> Stock = " + str(dez_stock) + "<p></p>"
	toReturn = toReturn+ "11 = " + str(onze) + " <b>//</b> Stock = " + str(onze_stock) + "<p></p>"
	toReturn = toReturn+ "12 = " + str(doze) + " <b>//</b> Stock = " + str(doze_stock) + "<p></p>"
	toReturn = toReturn+ "13 = " + str(treze) + " <b>//</b> Stock = " + str(treze_stock) + "<p></p>"
		
			

	return toReturn