import random

from random import choice

from models import cartas_mtg
from models import Page_Users
from models import compras


#USER MODULES
import page_users_utils
import constants
import card_database_utils
import compras_historico_utils

#logging
import logging

#Number of cards to take out of final list by IMPORTANCE
NUMBER_CARDS_TO_TAKE_OUT_BY_IMPORTANCE = constants.NUMBER_CARDS_TO_TAKE_OUT_BY_IMPORTANCE

NUMBER_OF_COMMON_UNCOMMON_TO_TAKE = constants.NUMBER_OF_COMMON_UNCOMMON_TO_TAKE
NUMBER_OF_RARE_TO_TAKE = constants.NUMBER_OF_RARE_TO_TAKE
NUMBER_OF_MYTIC_TO_TAKE = constants.NUMBER_OF_MYTIC_TO_TAKE

#########################################
#############Common Functions############
#########################################

def object_card_to_string(card,winner=False):
	SEPARATOR = "###"
	SUCCESS = "Carta###"
	SUCCESS_WINNER = "WINNER###"
	
	if winner:
		return SUCCESS_WINNER 
		+ card.nome 
		+ SEPARATOR 
		+ card.cor 
		+ SEPARATOR 
		+ card.custo 
		+ SEPARATOR 
		+ card.tipo 
		+ SEPARATOR 
		+ card.poder_resistencia 
		+ SEPARATOR 
		+ card.texto 
		+ SEPARATOR 
		+ card.raridade 
		+ SEPARATOR 
		+ card.edicao
	else:
		return SUCCESS 
		+ card.nome 
		+ SEPARATOR 
		+ card.cor 
		+ SEPARATOR 
		+ card.custo 
		+ SEPARATOR 
		+ card.tipo 
		+ SEPARATOR 
		+ card.poder_resistencia 
		+ SEPARATOR 
		+ card.texto 
		+ SEPARATOR 
		+ card.raridade 
		+ SEPARATOR 
		+ card.edicao


def bubblesort(l):
	for passesLeft in range(len(l)-1, 0, -1):
		for index in range(passesLeft):
			if l[index].importance < l[index + 1].importance:
				l[index].importance, l[index + 1].importance = l[index + 1].importance, l[index].importance
	return l	
	
def take_out_cards_by_importance(list_cards):
	sorted_list = bubblesort(list_cards)
	
	sorted_list.reverse()
	
	for i in range(NUMBER_CARDS_TO_TAKE_OUT_BY_IMPORTANCE):
		if len(sorted_list) == 1:
			break
		sorted_list.pop()	
	
	
	return sorted_list
	

#########################################
###########Random Functions##############
#########################################
def get_reg_random():
	#RANDOM
	random_number1 = random.random()
	random_number2 = random.random()
	
	random_str_1 = str(random_number1)[2:]
	random_str_2 = str(random_number2)[2:]
	
	total_random = random_str_1 + random_str_2
	
	return total_random
	
def get_random_number():
	return random.random()

#########################################
################BUY CARD#################
#########################################	
	
	
#THE SECOND MOST IMPORTANT FUNCTION OF ALL
def get_random_card_prepare(request):

	WINNER = False

	raridade = None
	
	accepted_rarities = ["Common","Uncommon","Rare"]
	
	try:
		raridade = request.POST['rarity']
	except:
		return "Erro###Raridade inv&aacute;lida"
	
	if raridade not in accepted_rarities:
		return "Erro###Raridade inv&aacute;lida"

	
	#Get user
	user = Page_Users.all().filter("email =", request.user.email).get()
	
	
	if user.clicks_total % constants.NUMBER_OCCURRENCES == 0 and user.clicks_total != 0 and constants.WINNERS_ACTIVE:
		WINNER = True
	
	
	#RETIRAR GUITA AO GAJO
	#Actualiza o numero de clicks de acordo com raridade
	#faz reset aos clicks nas seguintes condicoes
	#rara    = 100 -> reset
	#incomum = 150 -> reset
	#comum   = 150 -> reset
	user = page_users_utils.change_saldo_user(user,raridade,winner=WINNER)
	
	if user == None:
		return "Erro###Saldo insuficiente para efectuar a compra"
	
	#gets card
	#carta = get_random_card(raridade)
	carta = prepare_get_random_card(raridade,logica_de_negocio(user,raridade))
	
	#ADD CARTA AND USER TO MODEL COMPRAS!!!
	compras_historico_utils.add_to_compras(request.user.email,carta)
	
	#-1 NO STOCK DA CARTA
	card_database_utils.decrement_card_stock(carta)
	
	
	#Adiciona cartas ao return
	if WINNER:
		toReturn = object_card_to_string(carta,winner=True)
	else:
		toReturn = object_card_to_string(carta)
	
	
	#Adiciona novo saldo 
	toReturn = toReturn + "###" + str(user.saldo)
	
	logging.info("O user " + request.user.email + " comprou a carta " + carta.nome + " com raridade " + carta.raridade)
	
	return toReturn



#Defines business logic
#returns importancia of the card to take
#returns 0 if not special event
def logica_de_negocio(user,raridade):
	
	NUMBER_CLICKS = 0
	IMPORTANCIA = 1
	
	"""
	Raras

	15x - Recebe uma carta ate 2,50 euro Igual a importancia 10
	30x - Uma carta ate 3,50 euro Importancia 11
	50x Uma carta ate 5,5 euro importancia 12
	100x Uma carta ate 12,50 euro importancia 13
	Normal Uma carta ate 5,5 euro importancia 1

	"""
	if raridade == "Rare" or raridade == "Mytic":
		NUMBER_CLICKS = user.clicks_total_rare
		if NUMBER_CLICKS == 15:
			IMPORTANCIA = 10
		elif NUMBER_CLICKS  == 30:
			IMPORTANCIA = 11
		elif NUMBER_CLICKS == 50:
			IMPORTANCIA = 12		
		elif NUMBER_CLICKS == 100:
			IMPORTANCIA = 13
	
	
	#if raridade == "Rare" or raridade == "Mytic":
	#	NUMBER_CLICKS = user.clicks_total_rare
	#	if NUMBER_CLICKS % 100 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 13
	#	elif NUMBER_CLICKS % 50 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 12
	#	elif NUMBER_CLICKS % 30 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 11		
	#	elif NUMBER_CLICKS % 15 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 10
	
	"""
	Incomuns 

	15x - Carta ate 0,45 euro importancia 5
	30x - Carta ate 0,9 euro importancia 6
	50x Carta ate 1,5 euro importancia 7
	100x Carta ate 2,50  importancia 8
	150x Carta ate 5 euro importancia 9
	Normal: carta ate importancia 1
	"""
	
	
	if raridade == "Uncommon":
		NUMBER_CLICKS = user.clicks_total_uncommon
		if NUMBER_CLICKS == 150:
			IMPORTANCIA = 9
		elif NUMBER_CLICKS == 100:
			IMPORTANCIA = 8
		elif NUMBER_CLICKS == 50:
			IMPORTANCIA = 7
		elif NUMBER_CLICKS == 30:
			IMPORTANCIA = 6			
		elif NUMBER_CLICKS == 15:
			IMPORTANCIA = 5
	
		
	#if raridade == "Uncommon":
	#	NUMBER_CLICKS = user.clicks_total_uncommon
	#	if NUMBER_CLICKS % 150 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 9
	#	elif NUMBER_CLICKS % 100 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 8
	#	elif NUMBER_CLICKS % 50 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 7
	#	elif NUMBER_CLICKS % 30 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 6			
	#	elif NUMBER_CLICKS % 15 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 5
			
	"""
	Comum 

	50x Carta ate 0,35 euro importancia 2
	100x Carta ate 0,55euro importancia 3
	150x carta ate 2 euro importancia 4
	Normal ate importancia 1
	"""
	
	if raridade == "Common":
		NUMBER_CLICKS = user.clicks_total_common
		if NUMBER_CLICKS == 150:
			IMPORTANCIA = 4
		elif NUMBER_CLICKS == 20:
			IMPORTANCIA = 3
		elif NUMBER_CLICKS == 10:
			IMPORTANCIA = 2
	
	
	#if raridade == "Common":
	#	NUMBER_CLICKS = user.clicks_total_common
	#	if NUMBER_CLICKS % 150 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 4
	#	elif NUMBER_CLICKS % 100 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 3
	#	elif NUMBER_CLICKS % 50 == 0 and NUMBER_CLICKS != 0:
	#		IMPORTANCIA = 2
	
	return IMPORTANCIA

	

def prepare_get_random_card(raridade,importancia):

	cartas = []
	
	counter = 0
	importancia = importancia
	
	while(True):
	
		rand = get_random_number()
		
		if raridade == "Rare":
			cartas = cartas_mtg.all().filter('raridade =', raridade).filter('disponivel =',True).filter("importance =",importancia).filter('random_number > ',rand).fetch(limit=NUMBER_OF_RARE_TO_TAKE)
			#cartas = cartas + cartas_mtg.all().filter('raridade =', "Mytic").filter('disponivel =',True).filter("importance =",importancia).filter('random_number > ',rand).fetch(limit=NUMBER_OF_MYTIC_TO_TAKE)
		else:
			cartas = cartas_mtg.all().filter('raridade =', raridade).filter('disponivel =',True).filter("importance =",importancia).filter('random_number > ',rand).fetch(limit=NUMBER_OF_COMMON_UNCOMMON_TO_TAKE)
			
		
		if cartas == []:
			if raridade == "Rare":
				cartas = cartas_mtg.all().filter('raridade =', raridade).filter('disponivel =',True).filter("importance =",importancia).filter('random_number < ',rand).fetch(limit=NUMBER_OF_RARE_TO_TAKE)
				#cartas = cartas_mtg.all().filter('raridade =', "Mytic").filter('disponivel =',True).filter("importance =",importancia).filter('random_number < ',rand).fetch(limit=NUMBER_OF_MYTIC_TO_TAKE)
			else:
				cartas = cartas_mtg.all().filter('raridade =', raridade).filter('disponivel =',True).filter("importance =",importancia).filter('random_number < ',rand).fetch(limit=NUMBER_OF_COMMON_UNCOMMON_TO_TAKE)
				
		if cartas != []:
			break
			
		#if no card with choosen importance	
		counter	= counter + 1
		if counter == 10:
			importancia = 1
			
	toReturn = choice(cartas)
	
	return toReturn	
	
	
	
	
#THE MOST IMPORTANT FUNCTION OF ALL
def get_random_card(raridade):
	
	cartas = []
	
	while(True):
		
		cartas = None
	
		rand = get_random_number()
		
		if raridade == "Rare":
			cartas = cartas_mtg.all().filter('raridade =', raridade).filter('disponivel =',True).filter('random_number > ',rand).fetch(limit=NUMBER_OF_RARE_TO_TAKE)
			cartas = cartas + cartas_mtg.all().filter('raridade =', "Mytic").filter('disponivel =',True).filter('random_number > ',rand).fetch(limit=NUMBER_OF_MYTIC_TO_TAKE)
		else:
			cartas = cartas_mtg.all().filter('raridade =', raridade).filter('disponivel =',True).filter('random_number > ',rand).fetch(limit=NUMBER_OF_COMMON_UNCOMMON_TO_TAKE)
			
		if len(cartas) > 0:
			break

	cartas = take_out_cards_by_importance(cartas)
	
	toReturn = choice(cartas)
	
	logging.info("-------------------")
	logging.info("Nome " + str(toReturn.nome))
	logging.info("Stock " + str(toReturn.stock))
	logging.info("Importancia " + str(toReturn.importance))
	logging.info("-------------------")
	
	return toReturn
	
	

#########################################
###############SELL CARDS)###############
#########################################
def sell_card(request):

	nome = None
	edicao = None
	raridade = None
	
	try:
		nome = request.POST['nome']
		edicao = request.POST['edicao']
		raridade = request.POST['raridade']
	except:
		return "Erro###Campo com valor incorrecto"
	
	
	#card = cartas_mtg.all().filter('nome =', nome).filter('edicao > ',edicao).filter('raridade =',raridade).get()
	card_query = cartas_mtg.search(nome + " " + edicao + " " + raridade)
	
	try:
		card = card_query[0]
	except:
		return "Erro###Carta inexistente"
	
	#remover das compras
	found = compras_historico_utils.delete_card_from_compras(request.user.email, nome, edicao, raridade)

	if not found:
		return "Erro###Carta inexistente nas suas compras"
	
	#Get user
	user = Page_Users.all().filter("email =", request.user.email).get()
	
	#adicionar ao saldo do gajo
	user = page_users_utils.change_saldo_user(user, raridade, True)
	
	#adicionar a +1 ao stock da carta
	card_database_utils.increment_card_stock(card)

	
	return "Saldo###" + str(user.saldo)

#Sell all cards in card of user	
def sell_all(request , admin_user=None):
	
	user = None
	
	if admin_user != None:
		#get user
		#ADMIN ONLY
		user = Page_Users.all().filter("email =", admin_user).get()
		
		logging.info("ADMIN CALLING")
		logging.info(user.email)
	else:
		#get user
		user = Page_Users.all().filter("email =", request.user.email).get()
	
	
	
	#compras
	carrinho = None
	if admin_user != None:
		carrinho = compras.all().filter("user =", admin_user).get()
	else:
		carrinho = compras.all().filter("user =", request.user.email).get()
		
	
	cartas = carrinho.cartas
	
	valor = 0
	for raw_carta in cartas:
		carta = compras_historico_utils.transform_string_into_card(raw_carta)
		
		nome = carta.nome
		raridade = carta.raridade
		edicao = carta.edicao
		
		#TEMP - EDICOES CUJO O NOME FOI ALTERADO
		edicao = edicao.replace("Magic 2012","2012 Core Set (M12)")
		
		#END
		
		
		logging.info(raridade)
		card_query = cartas_mtg.search(nome + " " + edicao + " " + raridade)
		
		card = card_query[0]
		
		toAdd = 15
		#adicionar saldo
		if raridade == "Rare":
			toAdd = constants.VALUE_OF_RARE_CARD/2
		elif raridade == "Mytic":
			toAdd = constants.VALUE_OF_RARE_CARD/2
		elif raridade == "Uncommon":
			toAdd = constants.VALUE_OF_UNCOMMON_CARD/2
		elif raridade == "Common":
			toAdd = constants.VALUE_OF_COMMON_CARD/2
		valor = valor + toAdd
		
		#adicionar a +1 ao stock da carta
		card_database_utils.increment_card_stock(card)
		
	#actualizar carrinho
	carrinho.cartas = []
	carrinho.put()
	
	#actualizar user
	saldo_antigo = user.saldo
	novo_saldo = saldo_antigo + valor
	user.saldo = novo_saldo
	user.put()
	
	
#Empties a "carrinho" of given user
def admin_sell_all(request):

	try:
		user = request.POST['user']
	except:
		return "Erro###Campo com valor incorrecto"
		
	sell_all(request,user)
	
	return "Success###Carrinho esvaziado"
	
	
	