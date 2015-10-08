from models import compras
from models import cartas_mtg
from models import Historico

from django.http import HttpResponse

from django.utils import simplejson

import constants
import page_users_utils
import card_database_utils


import datetime

#debug
import logging


#########################################
#############Common Functions############
#########################################

#transforms a card into a string to put in model 
def transform_card_into_string(card):
	nome = card.nome
	cor = card.cor
	custo = card.custo
	tipo = card.tipo
	poder_resistencia = card.poder_resistencia
	texto = card.texto
	raridade = card.raridade
	edicao = card.edicao
	
	str_separator = "###"
	
	#str = nome +str_separator+ cor +str_separator+ custo +str_separator+ tipo +str_separator+ poder_resistencia +str_separator+ texto +str_separator+ raridade +str_separator+ edicao
	
	str = nome +str_separator+ raridade +str_separator+ edicao
	
	return str

def transform_string_into_card(str):

	info_list = str.split("###")
	
	nome = info_list[0]
	
	cor = ""
	custo = ""
	tipo = ""
	poder_resistencia = ""
	texto = ""
	
	raridade = info_list[1]
	edicao = info_list[2]
	
	card = cartas_mtg(nome = nome,
					cor = cor,
					custo = custo,
					tipo = tipo,
					poder_resistencia = poder_resistencia,
					texto = texto,
					raridade = raridade,
					edicao = edicao)
	
	return card

	
#returns a table from model compras
def user_cart_list_to_html(compra,date=None):
	if compra == None or len(compra) == 0:
		return "<tr><td>N/A</td><td>N/A</td><td>N/A</td><td>N/A</td>"

	if date == None:
		date = "N/A"
	
	STR_START = "<tr>"
	STR_END = "</tr>"
	LINE_START = "<td>"
	LINE_END = "</td>"
	
	toReturn = ""
	
	for raw_carta in compra:
		carta = transform_string_into_card(raw_carta)
		toReturn += STR_START
		toReturn += LINE_START + carta.nome + LINE_END
		toReturn += LINE_START + carta.raridade + LINE_END
		toReturn += LINE_START + carta.edicao + LINE_END
		toReturn += LINE_START + str(date) + LINE_END
		toReturn += STR_END

	return toReturn	


	
#TO BE IMPROVED
#to use with orders to table admin	
def card_list_to_html(cards):
	toReturn = ""
	SEPARATOR = "<p></p>"
	LINE = "-"
	
	for card in cards:
		toReturn += card.nome
		toReturn += LINE
		toReturn += card.edicao
		toReturn += LINE
		toReturn += card.raridade
		toReturn += SEPARATOR
		
	return toReturn
		
def orders_to_table_admin(orders):
	STR_START = "<tr>"
	STR_END = "</tr>"
	LINE_START = "<td>"
	LINE_END = "</td>"
	
	toReturn = ""
	
	card_list = []
	
	for order in orders:
		for raw_card in order.cartas:
			card_list.append(transform_string_into_card(raw_card))
	
		#to view specific orders
		url = "/orders/" + str(order.codigo)+"/"
		link = "<a href=\""+url+"\" target=\"_blank\">cartas</a>"
		
		
		toReturn += STR_START
		toReturn += LINE_START + order.user + LINE_END
		toReturn += LINE_START + str(order.codigo) + LINE_END
		toReturn += LINE_START + order.metodo + LINE_END
		toReturn += LINE_START + order.estado + LINE_END
		toReturn += LINE_START + order.morada + LINE_END
		toReturn += LINE_START + order.pais + LINE_END
		toReturn += LINE_START + order.codigopostal + LINE_END
		toReturn += LINE_START + order.telefone + LINE_END
		toReturn += LINE_START + str(order.date) + LINE_END
		#toReturn += LINE_START + card_list_to_html(card_list) + LINE_END
		toReturn += LINE_START + link  + LINE_END
		toReturn += STR_END
		card_list = []
	
	return toReturn

	
#########################################
############Compras Functions############
#########################################

#Returns list of compras for a user
#Returns None if user has no compras
def return_list_of_cards_from_compras(user):
	user_list = compras.all().filter('user =', user).fetch(limit=1)
	
	if len(user_list) == 0:
		return None
	
	toReturn = []
	
	user = user_list[0]
	
	cartas = user.cartas
	
	for carta in cartas:
		toReturn.append(transform_string_into_card(carta))
	
	if toReturn == []:
		return None
		
	return toReturn



#Returns list of compras for a user
#Returns None if user has no compras
#Deletes all cards in compras
def return_and_delete_list_of_cards_by_user(user):
	user = compras.all().filter('user =', user).get()
	
	if user == None:
		return None
	
	toReturn = []
	
	cartas = user.cartas
	
	for carta in cartas:
		toReturn.append(carta)
	
	if toReturn == []:
		return None
	
	user.cartas = []
	user.put()
	
	return toReturn	

#adds a card to the compras model
def add_to_compras(user,carta):
	user_list = compras.all().filter('user =', user).fetch(limit=1)
	
	carta_str = transform_card_into_string(carta)
	
	#user does not exist
	if len(user_list) == 0:
		cartas = []
		cartas.append(carta_str)
		
		compra_nova = compras(user = user,
						cartas = cartas)
		compra_nova.put()
		
	#user exists
	else:
		user = user_list[0]
	
		user_current_cards = user.cartas
	
		user_current_cards.append(carta_str)
		
		#update data
		user.last_buy = datetime.datetime.now()
	
		user.put()
		
#deletes a card from compras
#returns None if nothing exists		
def delete_card_from_compras(user, nome, edicao, raridade):
	
	user = compras.all().filter('user =', user).get()
	
	new_list = None
	
	
	if user != None:
	
		raw_card_list = user.cartas
		card_list = []
	
		new_list = []
		
		
		for raw_card in raw_card_list:
			card_list.append(transform_string_into_card(raw_card))
	
		
		
		found = False
		for card in card_list:
			if card.nome == nome and card.edicao == edicao and card.raridade == raridade and not found:
				found = True
				pass
			else:
				new_list.append(transform_card_into_string(card))
	
	
	user.cartas = new_list
	
	#update data
	user.last_buy = datetime.datetime.now()
	
	user.put()
		
	return found
	
	
	
#########################################
###########Historico Functions###########
#########################################	

#Return the full orders by user
def from_user_get_historico(user):
	return Historico.all().filter('user =', user).fetch(1000)

	
#return the cards from an order	
def get_cards_from_order(user,codigo):
	history = Historico.all().filter('user =', user).filter('codigo =',codigo).get()
	
	if history == None:
		return history
	
	cards_raw = history.cartas
	
	toReturn = []
	
	for card_raw in cards_raw:
		toReturn.append(transform_string_into_card(card_raw))
		
	return toReturn	

def get_last_order_by_user(user):
	return Historico.all().filter('user =', user).order('-date').get()
	
#searches the Historico model	
def search_orders_admin(request):
	
	keywords = request.POST['keywords']
	
	order_type = request.POST['order_type']
	
	orders = Historico.search(keywords, estado=order_type)
		
	return HttpResponse(orders_to_table_admin(orders))


#changes the state of an order	
def change_order_state(request):

	try:
		codigo = int(request.POST['order'])
	except:
		return HttpResponse("Encomenda Inv&aacute;lida")
		
	new_state = request.POST['new_state']
	
	
	order = Historico.all().filter('codigo =',codigo).get()
	
	if order == None:
		return HttpResponse("Encomenda Inv&aacute;lida")
		
	order.estado = new_state
	
	order.put()
	
	return HttpResponse("Efectuado com sucesso")
	
	
#shows specific order (cards)
def get_specific_order(request,codigo):
	
	try:
		codigo = int(codigo)
	except:
		return HttpResponse("Encomenda inv&aacute;lida")
	
	order = Historico.all().filter('codigo =',codigo).get()
	
	if order == None:
		return HttpResponse("Encomenda inv&aacute;lida")
	
	
	cards = []
	
	for card_raw in order.cartas:
		cards.append(transform_string_into_card(card_raw))
		
	return HttpResponse(card_list_to_html(cards))
	
		
#arranges cards for the orders page
def arrange_cards_for_orders(orders):

	toReturn = []

	for order in orders:
	
		cards_by_order = []
	
		cards = order.cartas
		for card in cards:
			clean_card = transform_string_into_card(card)
			
			cards_by_order.append(str(clean_card.nome) + " - " + str(clean_card.edicao))
		
		order.cartas = cards_by_order
		toReturn.append(order)
		
	return toReturn		
		
		

#return a cart (compras) of given user
def admin_view_user_cart(request):

	try:
		user = request.POST['user']
	except:
		user = None
	
	if user == None:
		return HttpResponse(user_cart_list_to_html(None))
		
	compra = compras.all().filter('user =',user).get()
	
	if compra == None:
		return HttpResponse(user_cart_list_to_html(None))

	return HttpResponse(user_cart_list_to_html(compra.cartas,compra.last_buy))

	

#########################################
##############Store Functions############
#########################################

#aligns (several cards with the same name/edition together)
#does not allow more than X of the same card

#ERRORS
# 1 - Falha na conversao para int do numero de cartas
# 2 - quantidade acima da permitida por utilizador
def allign_dic_carrinho(carrinho, card_name, card_edition, card_quantity):
	number_cards = carrinho['number_cards']
	

	for card in range(number_cards):
		card_id = "card" + str(card+1)
		
		try:
			if (carrinho['cards'][card_id]['name'] == card_name) and (carrinho['cards'][card_id]['edition'] == card_edition):
			
				try:
					quantity = int(carrinho['cards'][card_id]['quantity']) + int(card_quantity)
				except:
					return 1
				if quantity > constants.MAX_NUMBER_CARDS_PER_USER:
					return 2
			
				carrinho['cards'][card_id]['quantity'] = quantity
				carrinho['total_number_cards'] = carrinho['total_number_cards'] + int(card_quantity)
				return carrinho
		except:
			pass
			
	number_cards = carrinho['number_cards'] + 1
	
	#add card to dic
	carrinho['cards']['card' + str(number_cards)] = {'name':card_name,'edition':card_edition,'quantity':card_quantity}
	
	#increment number_cards
	carrinho['number_cards'] = number_cards
	
	carrinho['total_number_cards'] = carrinho['total_number_cards'] + int(card_quantity)
	
	return carrinho

	
#empties a store cart
def empty_store_cart(request):
	carrinho = str({ "number_cards":0, "total_number_cards":0, "cards":{} })
	request.session['carrinho'] = str(carrinho)
	
	
#Adds a card (name+edition+quantity) to a user session
def user_add_to_cart(request):
	
	try:
		edition = request.POST['card_edition']
	except:
		dic_erro = { "error":"A edicao da carta esta em falta."}
		return HttpResponse(simplejson.dumps(dic_erro), mimetype="application/json")
	try:
		name = request.POST['card_name']
	except:
		dic_erro = { "error":"O nome da carta esta em falta."}
		return HttpResponse(simplejson.dumps(dic_erro), mimetype="application/json")
	try:
		quantity = request.POST['card_quantity']
	except:
		dic_erro = { "error":"A quantidade desejada da carta esta em falta."}
		return HttpResponse(simplejson.dumps(dic_erro), mimetype="application/json")
		
	carrinho = request.session.get('carrinho')
	
	#if carrinho does not exist
	if carrinho == None:
		carrinho = str({ "number_cards":0, "total_number_cards":0, "cards":{} })
	
	#if error reset carrinho object in session
	try:
		carrinho_dic = eval(carrinho)
	except:
		carrinho = str(dic_cards = { "number_cards":0, "total_number_cards":0, "cards":{} })

	new_carrinho = allign_dic_carrinho(carrinho_dic, name, edition, quantity)
	
	if new_carrinho == 1:
		dic_erro = { "error":"Falha de conversao, o seu carrinho vai sofrer um reset"}
		carrinho = str({ "number_cards":0, "total_number_cards":0, "cards":{} })
		request.session['carrinho'] = carrinho
		return HttpResponse(simplejson.dumps(dic_erro), mimetype="application/json")
	elif new_carrinho == 2:
		dic_erro = { "error":"Maximo de " + str(constants.MAX_NUMBER_CARDS_PER_USER) + " cartas iguais por utilizador"}
		return HttpResponse(simplejson.dumps(dic_erro), mimetype="application/json")
	else:
		request.session['carrinho'] = str(new_carrinho)
	
	dic_sucess = { "success":"Adicionados " 
	+ str(quantity) 
	+ " " 
	+ name 
	+ " de " 
	+ edition, 
	"total_number_cards": new_carrinho['total_number_cards']}
	return HttpResponse(simplejson.dumps(dic_sucess), mimetype="application/json")

	
	
class cartas_mtg_store:
	
	def __init__(self, nome, raridade, edicao, stock, real_value,conversion, quantity):
		self.nome = nome
		self.raridade = raridade
		self.edicao = edicao
		self.stock = stock
		self.real_value = real_value
		self.conversion = conversion
		self.quantity = quantity


#From a request returns a list of cards (cards in a session) STORE
#returns None if no card in cart
def return_list_of_cards_from_request(request):	
	carrinho = request.session.get('carrinho')
	
	if carrinho == None:
		return None
	
	pais = page_users_utils.get_pais_from_request(request)
	
	carrinho = eval(carrinho)
	
	if int(carrinho['number_cards']) == 0:
		return None
	
	cards_cart = []
	
	number_cards = carrinho['number_cards']
	
	
	logging.info("number_cards " + str(number_cards))
	logging.info("total_number_cards " + str(carrinho['total_number_cards']))
	
	for card in range(number_cards):
		card_id = "card" + str(card+1)
		
		try:
			name = carrinho['cards'][card_id]['name']
			edition = carrinho['cards'][card_id]['edition']
			quantity = carrinho['cards'][card_id]['quantity']
			
			logging.info(name)
			logging.info(edition)
			logging.info(quantity)
	
			real_card = cartas_mtg.all().filter('nome =',name).filter('edicao =',edition).get()
		
			stock = real_card.stock
			real_value = real_card.real_value
			conversion = card_database_utils.real_price_by_credits(real_value,pais)
			raridade = real_card.raridade
		
			#to not use card and to add field quantity
			card_in_cart = cartas_mtg_store(name,raridade,edition,stock,real_value,conversion,quantity)
		
			cards_cart.append(card_in_cart)
		except:
			pass
			
	if cards_cart == []:
		return None
		
	return cards_cart
	
#returns total number of cards in ones cart
def get_total_number_cards(request):
	carrinho = request.session.get('carrinho')
	
	if carrinho == None:
		return 0
	
	carrinho = eval(carrinho)
	
	if carrinho == None:
		numero_cartas = 0
	else:
		numero_cartas = carrinho["total_number_cards"]

	return numero_cartas
	
#returns total cost (real value) in a list o cards (store)
def get_total_price_cart(card_list):

	value_toReturn = 0
	
	if card_list == None or len(card_list) == 0:
		return value_toReturn

	for card in card_list:
		real_value = int(card.real_value)
		multiplier = int(card.quantity)
		
		value_toReturn = value_toReturn + (real_value * multiplier)
		
		
	return value_toReturn

#changes quantity of card in a store cart
def change_quantity_card(request):
	carrinho = request.session.get('carrinho')
	
	if carrinho == None:
		return None
	
	nome = None
	edicao = None
	raridade = None
	quantity = None
		
	try:
		nome = request.POST['nome']
	except:
		logging.info("nome")
		return HttpResponse("Nome em falta")
	try:
		edicao = request.POST['edicao']
	except:
		logging.info("edicao")
		return HttpResponse("Edicao em falta")
	try:
		raridade = request.POST['raridade']
	except:
		logging.info("raridade")
		return HttpResponse("Raridade em falta")
	try:
		quantity = int(request.POST['quantity'])
	except:
		logging.info("quantidade")
		return HttpResponse("Quantidade em falta")

	carta_real = cartas_mtg.all().filter('nome =',name).filter('edicao =',edition).get()
	
	if carta_real == None:
		return HttpResponse("Carta invalida")
		
	if quantity < 0 or quantity > constants.MAX_NUMBER_CARDS_PER_USER:
		return HttpResponse("A quantidade tem de ser um valor entre 0 e  "+ str(constants.MAX_NUMBER_CARDS_PER_USER) + " unidades")
		
	if quantity > carta_real.stock:
		return HttpResponse("Apenas existe " + str(carta_real.stock) + " em stock")
			
	try:		
		carrinho = eval(carrinho)
	except:
		carrinho = { "number_cards":0, "total_number_cards":0, "cards":{} }
		request.session['carrinho'] = str(carrinho)
		return HttpResponse("Carrinho Inv&aacute;lida")
		
		
	number_cards = carrinho['number_cards']
	
	for card in range(number_cards):
		card_id = "card" + str(card+1)
		
		try:
			if (carrinho['cards'][card_id]['name'] == nome) and (carrinho['cards'][card_id]['edition'] == edicao):
				if quantity != 0:
					#valor para tirar ao total_number_cards (diferenca entre a quantidade existente e a nova)
					diff = int(carrinho['cards'][card_id]['quantity']) - quantity
					carrinho['total_number_cards'] = int(carrinho['total_number_cards']) - diff
					carrinho['cards'][card_id]['quantity'] = quantity
				if quantity == 0:
					carrinho['total_number_cards'] = int(carrinho['total_number_cards']) - int(carrinho['cards'][card_id]['quantity']) 
					#carrinho['number_cards'] = int(carrinho['number_cards']) - 1
					del carrinho['cards'][card_id]
					if int(carrinho['total_number_cards']) == 0:
						empty_store_cart(request)
						return None
				break
		except:
			pass
			
	request.session['carrinho'] = str(carrinho)