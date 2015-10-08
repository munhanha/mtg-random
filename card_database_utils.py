from models import cartas_mtg
from models import user_cards

from django.http import HttpResponse

from django.utils import simplejson

#user models
import random_utils
import constants
import page_users_utils


#debug
import logging

####################################
##########DATABASE Functions########
####################################
#given a list of cards returns html to place in table
def cards_to_table_admin(cards):
	STR_START = "<tr>"
	STR_END = "</tr>"
	LINE_START = "<td>"
	LINE_END = "</td>"
	
	toReturn = ""
	
	for card in cards:
		toReturn += STR_START
		toReturn += LINE_START + card.nome + LINE_END
		toReturn += LINE_START + card.cor + LINE_END
		toReturn += LINE_START + card.custo + LINE_END
		toReturn += LINE_START + card.tipo + LINE_END
		toReturn += LINE_START + card.poder_resistencia + LINE_END
		#toReturn += LINE_START + card.texto.replace("%","") + LINE_END
		toReturn += LINE_START + card.raridade + LINE_END
		toReturn += LINE_START + card.edicao + LINE_END
		toReturn += LINE_START + str(card.stock) + LINE_END
		toReturn += LINE_START + str(card.importance) + LINE_END
		toReturn += LINE_START + str(card.real_value) + LINE_END
		toReturn += STR_END
	
	
	return toReturn


####################################
##########DATABASE Functions########
####################################
#search cards Admin (returns sensetive info like stock)
def search_cards_admin(request):
	
	keywords = request.POST['keywords']
	
	cards = cartas_mtg.search(keywords)
		
	return HttpResponse(cards_to_table_admin(cards))

#turns cost into imagens to be displayed in the user search cards
def card_cost_to_images(cost):

	cost = cost.replace("W","<img src=\"img/mana/mana_w.gif\">")
	cost = cost.replace("U","<img src=\"img/mana/mana_u.gif\">")
	cost = cost.replace("R","<img src=\"img/mana/mana_r.gif\">")
	cost = cost.replace("B","<img src=\"img/mana/mana_b.gif\">")
	cost = cost.replace("G","<img src=\"img/mana/mana_g.gif\">")
	
	cost = cost.replace("%`","<img src=\"img/mana/manapu.gif\">")
	cost = cost.replace("%@","<img src=\"img/mana/manapg.gif\">")
	cost = cost.replace("%!","<img src=\"img/mana/manapw.gif\">")
	cost = cost.replace("%$","<img src=\"img/mana/manapb.gif\">")
	cost = cost.replace("%^","<img src=\"img/mana/manapr.gif\">")
	
	cost = cost.replace("%Q","<img src=\"img/mana/manabg.gif\">")
	cost = cost.replace("%O","<img src=\"img/mana/manawb.gif\">")
	cost = cost.replace("%K","<img src=\"img/mana/manabr.gif\">")
	cost = cost.replace("%A","<img src=\"img/mana/managw.gif\">")
	cost = cost.replace("%I","<img src=\"img/mana/manaur.gif\">")
	cost = cost.replace("%P","<img src=\"img/mana/manarw.gif\">")
	cost = cost.replace("%S","<img src=\"img/mana/managu.gif\">")
	cost = cost.replace("%L","<img src=\"img/mana/manarg.gif\">")
	cost = cost.replace("%D","<img src=\"img/mana/manawu.gif\">")
	cost = cost.replace("%V","<img src=\"img/mana/manaub.gif\">")
	
	cost = cost.replace("%E","<img src=\"img/mana/mana2w.gif\">")
	cost = cost.replace("%F","<img src=\"img/mana/mana2u.gif\">")
	cost = cost.replace("%H","<img src=\"img/mana/mana2b.gif\">")
	cost = cost.replace("%J","<img src=\"img/mana/mana2r.gif\">")
	cost = cost.replace("%M","<img src=\"img/mana/mana2g.gif\">")
	
	
	return cost

#cleans the card text to be displayed in the user card search	
def clean_card_text(text):
	
	text = text.replace("\"","")
	
	return text


def real_price_by_credits(value,country):
	if country == "Portugal":
		return str(constants.MULTIPLICADOR_CREDITOS_PORTUGAL * value) + " &euro;"
	elif country == "Brasil":
		return str(constants.MULTIPLICADOR_CREDITOS_BRASIL * value) + " Real"
	

	
#search cards User
def search_cards_user(request):
	
	number_cards = 0
	
	country = page_users_utils.get_pais_from_request(request)
	
	dic = { "number_cards":number_cards, "cards":{} }
	
	try:
		keywords = request.POST['keywords']
	except:
		return HttpResponse(simplejson.dumps(dic), mimetype="application/json")
	try:
		edition = request.POST['edition']
	except:
		return HttpResponse(simplejson.dumps(dic), mimetype="application/json")
	try:
		colour = request.POST['colour']
	except:
		return HttpResponse(simplejson.dumps(dic), mimetype="application/json")
	
	if country not in constants.ALLOWED_COUNTRIES or colour not in constants.ALLOWED_COLOURS_USER_CARD_SEARCH:
		return HttpResponse(simplejson.dumps(dic), mimetype="application/json")
		
	cards = cartas_mtg.user_search(keywords, colour, edition)
	
	for card in cards:
		number_cards = number_cards + 1
		dic['cards']['card' + str(number_cards)] = {'name':card.nome,
		'colour':card.cor,
		'cost':card_cost_to_images(card.custo),
		'type':card.tipo,
		'power_res':card.poder_resistencia,
		'raridade':card.raridade,
		'edition':card.edicao,
		'stock':card.stock, 
		'preco':card.real_value,
		'preco_conversao':real_price_by_credits(card.real_value,country),
		'texto':clean_card_text(card.texto)}
	
	logging.info("User = "+ request.user.email)
	logging.info("Keywords = "+ keywords )
	logging.info("Edition = " + edition)
	logging.info("Colour = " + colour)
	
	
	dic['number_cards'] = number_cards
	return HttpResponse(simplejson.dumps(dic), mimetype="application/json")


#adds a card to the database
def add_card_to_db(request):
	
	name = ""
	colour = ""
	cost = ""
	type = ""
	power_resistance = ""
	text = ""
	rarity = ""
	edition = ""
	quantidade = None
	importancia = None
	
	
	try:
		name = request.POST['name']
		colour = request.POST['colour']
		cost = request.POST['cost']
		type = request.POST['type']
		power_resistance = request.POST['power_resistance']
		text = request.POST['text']
		rarity = request.POST['rarity']
		edition = request.POST['edition']
		quantidade = int(request.POST['stock'])
		importancia = int(request.POST['importance'])
		
	except:
		return HttpResponse('Erro nos dados da carta ' + name)
		
	if len(text) > 500:
		logging.info(name)
		text = text[:500]
		
	#cleans % from text
	text = text.replace("%","")
	
	if rarity == "R" or rarity == "R // R":
		rarity = "Rare"
	
	if rarity == "M" or rarity == "M // M":
		rarity = "Mytic"
		
	if rarity == "U" or rarity == "U // U":
		rarity = "Uncommon"
		
	if rarity == "C" or rarity == "C // C":
		rarity = "Common"
	
	
	carta_comparacao = cartas_mtg.all().filter('nome =',name).filter('edicao =',edition).get()
	
	if carta_comparacao != None:
		return HttpResponse('Carta jah existe ' + name)
		
		
	
	card = cartas_mtg(nome = name,
					cor = colour,
					custo = cost,
					tipo = type,
					poder_resistencia = power_resistance,
					texto = text,
					raridade = rarity,
					random_number = random_utils.get_random_number(),
					stock = int(quantidade),
					importance = int(importancia),
					edicao = edition)
	
	card.put_DB()
	
	
	return HttpResponse('Success')

#change_card_stock_importance
def change_card_stock_importance(request):
	
	carta = ""
	stock = None
	importancia = None
	valor_real = None
	
	try:
		carta = request.POST['carta']
	except:
		return HttpResponse('Valores incorrectos')
	
	try:
		stock = request.POST['stock']
		stock = int(stock)
	except:
		stock = None
		
	try:	
		importancia = request.POST['importancia']
		importancia = int(importancia)	
	except:
		importancia = None
		
	try:	
		valor_real = request.POST['valor_real']
		valor_real = int(valor_real)	
	except:
		valor_real = None	
		
	
	if stock < 0 and stock != None:
		return HttpResponse('Valor do stock n&atilde;o pode ser inferior a 0')
	if importancia < 0 and importancia != None:
		return HttpResponse('Valor da importancia n&atilde;o pode ser inferior a 0')
	if importancia > 20 and importancia != None:
		return HttpResponse('Valor da importancia n&atilde;o pode ser superior a 20')
	
	carta_a_alterar = cartas_mtg.search(carta)
		
	if carta_a_alterar.count() == 0:
		return HttpResponse('Carta inexistente')
	
	if carta_a_alterar.count() != 1:
		return HttpResponse('Existe mais que uma carta com o mesmo nome')
	
		
	carta_final = carta_a_alterar[0]
	
	if stock != None:
		carta_final.stock = stock
	if importancia != None:
		carta_final.importance = importancia
	if valor_real != None:
		carta_final.real_value = valor_real
	
	carta_final.put()
	
	return HttpResponse('Efectuado com sucesso')

	
def decrement_card_stock(card):

	real_card = cartas_mtg.all().filter("nome =",card.nome).filter("edicao =",card.edicao).filter("cor =",card.cor).filter("custo =",card.custo).filter("tipo =",card.tipo).get()
	real_card.stock = real_card.stock -1
	real_card.put()

def decrement_card_stock_store(nome,edicao,quantity):

	real_card = cartas_mtg.all().filter("nome =",nome).filter("edicao =",edicao).get()
	real_card.stock = real_card.stock - int(quantity)
	real_card.put()

def increment_card_stock(card):

	real_card = cartas_mtg.all().filter("nome =",card.nome).filter("edicao =",card.edicao).filter("cor =",card.cor).filter("custo =",card.custo).filter("tipo =",card.tipo).get()
	real_card.stock = real_card.stock +1
	real_card.put()



#changes user cards(cartas do sistema)	
def change_user_cards(request):	

	rand = random_utils.get_random_number()

	cards_rare = cartas_mtg.all().filter("raridade =","Rare").filter("disponivel =", True).filter("importance =",13).filter('random_number > ',rand).fetch(10)
	
	if len(cards_rare) < 10:
		cards_rare = cards_rare + cartas_mtg.all().filter("raridade =","Rare").filter("disponivel =", True).filter("importance =",12).filter('random_number > ',rand).fetch(10-len(cards_rare))
	if len(cards_rare) < 10:
		cards_rare = cards_rare + cartas_mtg.all().filter("raridade =","Rare").filter("disponivel =", True).filter("importance =",11).filter('random_number > ',rand).fetch(10-len(cards_rare))	
	if len(cards_rare) < 10:
		cards_rare = cards_rare + cartas_mtg.all().filter("raridade =","Rare").filter("disponivel =", True).filter("importance =",10).filter('random_number > ',rand).fetch(10-len(cards_rare))
	if len(cards_rare) < 10:
		cards_rare = cards_rare + cartas_mtg.all().filter("raridade =","Rare").filter("disponivel =", True).filter("importance =",1).filter('random_number > ',rand).fetch(10-len(cards_rare))
		
	
	cards_uncommon = cartas_mtg.all().filter("raridade =","Uncommon").filter("disponivel =", True).filter("importance =",9).filter('random_number > ',rand).fetch(5)
	if len(cards_uncommon) < 5:
		cards_uncommon = cards_uncommon + cartas_mtg.all().filter("raridade =","Uncommon").filter("disponivel =", True).filter("importance =",8).filter('random_number > ',rand).fetch(5-len(cards_uncommon))
	if len(cards_uncommon) < 5:
		cards_uncommon = cards_uncommon + cartas_mtg.all().filter("raridade =","Uncommon").filter("disponivel =", True).filter("importance =",7).filter('random_number > ',rand).fetch(5-len(cards_uncommon))
	if len(cards_uncommon) < 5:
		cards_uncommon = cards_uncommon + cartas_mtg.all().filter("raridade =","Uncommon").filter("disponivel =", True).filter("importance =",6).filter('random_number > ',rand).fetch(5-len(cards_uncommon))
	if len(cards_uncommon) < 5:
		cards_uncommon = cards_uncommon + cartas_mtg.all().filter("raridade =","Uncommon").filter("disponivel =", True).filter("importance =",5).filter('random_number > ',rand).fetch(5-len(cards_uncommon))
	if len(cards_uncommon) < 5:
		cards_uncommon = cards_uncommon + cartas_mtg.all().filter("raridade =","Uncommon").filter("disponivel =", True).filter("importance =",1).filter('random_number > ',rand).fetch(5-len(cards_uncommon))
		
		
	cards_common = cartas_mtg.all().filter("raridade =","Common").filter("disponivel =", True).filter("importance =",4).filter('random_number > ',rand).fetch(5)
	if len(cards_common) < 5:
		cards_common = cards_common + cartas_mtg.all().filter("raridade =","Common").filter("disponivel =", True).filter("importance =",3).filter('random_number > ',rand).fetch(5-len(cards_common))
	if len(cards_common) < 5:
		cards_common = cards_common + cartas_mtg.all().filter("raridade =","Common").filter("disponivel =", True).filter("importance =",2).filter('random_number > ',rand).fetch(5-len(cards_common))
	if len(cards_common) < 5:
		cards_common = cards_common + cartas_mtg.all().filter("raridade =","Common").filter("disponivel =", True).filter("importance =",1).filter('random_number > ',rand).fetch(5-len(cards_common))
	
	
	cards = cards_rare + cards_uncommon + cards_common
	
	if len(cards) == 20:
		#delete
		q = user_cards.all().fetch(20)
		for card in q:
			card.delete()
			
		#add
		for card in cards:
			card_toAdd = user_cards(name_card = card.nome)
			card_toAdd.put()
	
	return HttpResponse("sucess")
	
	
def get_change_user_cards():
	return user_cards.all().fetch(20)