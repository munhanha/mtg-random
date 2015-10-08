# -*- coding: utf-8 -*-

#Django Authentication
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login	, logout

#django return types
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template

import django.utils.encoding 

from google.appengine.ext import db

from models import Temp_User
from models import Page_Users
from models import Historico
from models import carregamentos
from models import historico_carregamentos


import re,sys,unicodedata,string,random, uuid


#USER MODULES
import random_utils
import mail_utils
import constants
import compras_historico_utils
import card_database_utils


import logging

#######################################
##########VALOR DAS CARTAS#############
#######################################
VALUE_OF_COMMON_CARD = constants.VALUE_OF_COMMON_CARD
VALUE_OF_UNCOMMON_CARD = constants.VALUE_OF_UNCOMMON_CARD
VALUE_OF_RARE_CARD = constants.VALUE_OF_RARE_CARD

#######################################
##########Common functions#############
#######################################

#simple function to validade if string is a email
#returns true if it checks out
def validateEmail(email):

	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return True
	return False

#transforms latin chars to ASCII chars
def latin_to_ascii(line):
	aux = ""
	
	return aux.join((c for c in unicodedata.normalize('NFD', line) if unicodedata.category(c) != 'Mn'))
	
#generates random string (N is size of the generated string)
def generate_random_string(N = 8):
	random_pass = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))
	return random_pass


def change_password_for_user(user,new_password):
	
	#u user of django
	try:
		u = User.objects.get(username__exact=user)
	except:
		return 'Utilizador inexistente'
	
	#user from page
	user = Page_Users.all().filter("id =", user).get()
	
	if user == None:
		return 'Utilizador inexistente'

	#change in the django
	u.set_password(new_password)
	u.save()
	
	#change in the user
	user.password = new_password
	user.put()

	return "Success"

#Given a email(login) return the user object
def get_user_info(email):
	return Page_Users.all().filter("email =", email).get()

#Splits a codigo postal
def split_cod_postal(cod_postal):

	items = cod_postal.split("-")
	
	return items
	
#Given a email(login) return the full name
#returns "" if not found or not unique
def get_name_from_email(email):
	#user from page
	user = Page_Users.all().filter("email =", email)
	
	if user.count() != 1:
		return ""
		
	if user.count() == 0:
		return ""
	
	user_actual = user[0]
	
	return user_actual.nome
	
#Given a email(login) return the saldo
#returns "" if not found or not unique
def get_saldo_from_email(email):
	#user from page
	user = Page_Users.all().filter("email =", email).get()

	return user.saldo
	
#Given a email(login) return the country
#returns "" if not found or not unique
def get_pais_from_email(email):
	#user from page
	user = Page_Users.all().filter("email =", email)
	
	if user.count() != 1:
		return ""
		
	if user.count() == 0:
		return ""
	
	user_actual = user[0]
	
	return user_actual.pais		

#Sees if the country is in the session, if not goes to DB
#May save a trip to the database	
def get_pais_from_request(request):
	pais = request.session.get('Pais')
	
	if pais in constants.ALLOWED_COUNTRIES:
		return pais
	else:
		pais = get_pais_from_email(request.user.email)
		request.session['Pais'] = pais
		return pais
	
#given a list of users returns html to place in table
def users_to_table(users):
	STR_START = "<tr>"
	STR_END = "</tr>"
	LINE_START = "<td>"
	LINE_END = "</td>"
	
	toReturn = ""
	
	for user in users:
		toReturn += STR_START
		toReturn += LINE_START + user.email + LINE_END
		toReturn += LINE_START + user.nome + LINE_END
		toReturn += LINE_START + user.morada + LINE_END
		toReturn += LINE_START + user.codigopostal + LINE_END
		toReturn += LINE_START + user.telefone + LINE_END
		toReturn += LINE_START + str(user.saldo) + LINE_END
		toReturn += LINE_START + user.pais + LINE_END
		toReturn += LINE_START + str(user.clicks_total) + LINE_END
		toReturn += LINE_START + str(user.clicks_total_common_fix) + LINE_END
		toReturn += LINE_START + str(user.clicks_total_uncommon_fix) + LINE_END
		toReturn += LINE_START + str(user.clicks_total_rare_fix) + LINE_END
		toReturn += STR_END

		
	return toReturn
	
#given a list of payments returns html to place in table
def payments_to_table(payments):
	STR_START = "<tr>"
	STR_END = "</tr>"
	LINE_START = "<td>"
	LINE_END = "</td>"
	
	toReturn = ""
	
	for payment in payments:
		toReturn += STR_START
		toReturn += LINE_START + payment.user + LINE_END
		toReturn += LINE_START + payment.metodo + LINE_END
		toReturn += LINE_START + payment.valor + LINE_END
		toReturn += LINE_START + payment.moeda + LINE_END
		toReturn += LINE_START + str(payment.date) + LINE_END
		toReturn += STR_END

	return toReturn	
	
#######################################
##########Derived from views###########
#######################################	

#all login logic
#FUNCTION CALLED BY VIEW
def page_login(request):
	username = ""
	password = ""
	
	try:
		username = request.POST['username']
		password = request.POST['password']
	except:
		try:
			if not user.is_active:
				return direct_to_template(request, "index.html", {'error': "Conta desabilitada"})
			if request.user.is_staff:
				request.session['Pais'] = get_pais_from_email(request.user.email)
				return HttpResponseRedirect("staff_admin")
			if request.user.is_authenticated():
				request.session['Pais'] = get_pais_from_email(request.user.email)
				return HttpResponseRedirect("main")
		except:
			return direct_to_template(request, "index.html")
			
	username = username.lower()
	#get real username
	real_user = Page_Users.all().filter('email =',username).get()
	
	if real_user == None:
		return direct_to_template(request, "index.html", {'error': "Username ou password incorrectos."})
	
	username = real_user.id
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
		else:
			return direct_to_template(request, "index.html", {'error': "Conta desabilitada"})
	else:
		return direct_to_template(request, "index.html", {'error': "Username ou password incorrectos."})
		
	if request.user.is_staff:
		request.session['Pais'] = get_pais_from_email(request.user.email)
		return HttpResponseRedirect("staff_admin")
	if request.user.is_authenticated():
		request.session['Pais'] = get_pais_from_email(request.user.email)
		return HttpResponseRedirect("main")
	if not request.user.is_authenticated():
		return direct_to_template(request, "index.html", {'error': "Username ou password incorrectos."})
		
	return direct_to_template(request, "index.html", {'error': "Username ou password incorrectos."})


#Checks user information
def verify_user_info(email,password,nome,morada,codigopostal,telefone,pais):
	allowed_expressions_chars = re.compile('^[a-zA-Z\s]+$',re.UNICODE)
	allowed_expressions_numbers = re.compile('^[0-9-]+$')
	allowed_expressions_password = re.compile('^[\w\W]+$')
	allowed_expressions_morada = re.compile('^[a-zA-Z0-9-ºª.,\s]+$',re.UNICODE)
	
	
	clean_nome = latin_to_ascii(nome)
	clean_morada = latin_to_ascii(morada)
	clean_codigopostal = latin_to_ascii(codigopostal)
	clean_pais = latin_to_ascii(pais)
	

	if validateEmail(email) == False:
		return "O Email n&atilde;o apresenta uma sintaxe correcta."
		
	#verifica se jah existe
	temps = db.GqlQuery("SELECT * FROM Temp_User WHERE email= \'" + email+"\'")
	users = db.GqlQuery("SELECT * FROM Page_Users WHERE email= \'" + email+"\'")
	
	if temps.count() != 0:
		return "Email j&aacute; existente em base de dados."
	if users.count() != 0:
		return "Email j&aacute; existente em base de dados."	
		
	if len(password) < 6 or len(password) > 16:
		return "Password com tamanho inv&aacute;lido."
	
	match_password = allowed_expressions_password.match(password)
	if not match_password:
		return "Password com caracteres inv&aacute;lidos."
	
	match_nome = allowed_expressions_chars.match(clean_nome)
	if not match_nome:
		return "Nome com caracteres inv&aacute;lidos."
	
	if len(nome) < 5 or len(nome) > 50:
		return "Nome com tamanho inv&aacute;lido."
	
	match_morada = allowed_expressions_morada.match(clean_morada)
	if not match_morada:
		return "Morada com caracteres inv&aacute;lidos."
	
	if len(morada) < 5 or len(morada) > 80:
		return "Morada com tamanho inv&aacute;lido."
		
	if len(telefone) < 9:
		return "Telefone com tamanho inv&aacute;lido."	
		
	match_telefone = allowed_expressions_numbers.match(telefone)
	if not match_telefone:
		return "Telefone com caracteres inv&aacute;lidos."
	
	match_pais = allowed_expressions_chars.match(clean_pais)
	if not match_pais:
		return "Pa&iacute;s com caracteres inv&aacute;lidos."
	
	match_codigopostal = allowed_expressions_numbers.match(clean_codigopostal)
	if not match_codigopostal:
		return "C&oacute;digo postal inv&aacute;lido."
		
#Checks user information
def verify_partial_user_info(morada,codigopostal,telefone):
	allowed_expressions_chars = re.compile('^[a-zA-Z\s]+$',re.UNICODE)
	allowed_expressions_numbers = re.compile('^[0-9-]+$')
	allowed_expressions_morada = re.compile('^[a-zA-Z0-9-ºª.,\s]+$',re.UNICODE)
	
	
	clean_morada = latin_to_ascii(morada)
	clean_codigopostal = latin_to_ascii(codigopostal)
	#clean_pais = latin_to_ascii(pais)
	
	
	match_morada = allowed_expressions_morada.match(clean_morada)
	if not match_morada:
		return "Morada com caracteres inv&aacute;lidos."
	
	if len(morada) < 5 or len(morada) > 80:
		return "Morada com tamanho inv&aacute;lido."
		
	if len(telefone) < 9:
		return "Telefone com tamanho inv&aacute;lido."	
		
	match_telefone = allowed_expressions_numbers.match(telefone)
	if not match_telefone:
		return "Telefone com caracteres inv&aacute;lidos."
	
	#match_pais = allowed_expressions_chars.match(clean_pais)
	#if not match_pais:
	#	return "Pa&iacute;s com caracteres inv&aacute;lidos."
	
	match_codigopostal = allowed_expressions_numbers.match(clean_codigopostal)
	if not match_codigopostal:
		return "C&oacute;digo postal inv&aacute;lido."		
	

#ADDs if all ok a user to temp data base 
#FUNCTION CALLED BY VIEW
def page_addUser_temp(request):

	email = None
	password = None
	nome = None
	morada = None
	codigopostal = None
	telefone = None
	pais = None

	try:
		email = request.POST['email']
		password =request.POST['password']
		nome = request.POST['nome']
		morada = request.POST['morada']
		codigopostal = request.POST['codigopostal'] +"-"+request.POST['codigopostal2']
		telefone = request.POST['telefone']
		pais = request.POST['pais']
		
	except:
		return HttpResponse("Valores de Input em falta.")
	
	#check server side info
	error = verify_user_info(email,password,nome,morada,codigopostal,telefone,pais)
	
	#print in page error if any
	if error != None:
		return HttpResponse(error)
	else:
		add_to_temp_users(email,password,nome,morada,codigopostal,telefone,pais)

	return HttpResponse('Success')
	
	
#Adds user to temp data base			
def add_to_temp_users(email,nome,morada,codigopostal,telefone,pais):
	temp_user = Temp_User(email = email,
						nome = nome,
						morada = morada,
						codigopostal = codigopostal,
						telefone = telefone,
						pais = pais)
	
	total_random = random_utils.get_reg_random()
	
	temp_user.confirmation = total_random
	
	#adds to temp users
	temp_user.put()
	
	#SEND MAIL with confirmation code
	mail_utils.sendRegistrationMain(email,total_random)


def add_permanent_user(email,nome,morada,codigopostal,telefone,pais):
	
	id = None
	while(True):
		id = uuid.uuid4().hex[:30]		
		user = Page_Users.all().filter("id =", id).get()
		if user == None:
			break
		
	#My DB
	user = Page_Users(email = email,
					id = id,
					nome = nome,
					morada = morada,
					codigopostal = codigopostal,
					telefone = telefone,
					pais = pais)
	
	user.put()
	
	#Django
	user = User.objects.create_user(id, email, password)
	user.is_staff = False
	user.save()

	
def finish_registration(code):
	all_ok = False

	temps = db.GqlQuery("SELECT * FROM Temp_User")
	
	for temp in temps:
		if temp.confirmation == code:
			add_permanent_user(temp.email,temp.nome,temp.morada,temp.codigopostal,temp.telefone,temp.pais)
			db.delete(temp)
			all_ok = True
			
	return all_ok
	
	
def update_saldo(request):
	
	user = None
	plus_saldo = None
	
	try:
		user = request.POST['email']
	except:
		return HttpResponse('Valor no utilizador incorrecto')
		
	try:
		plus_saldo = int(request.POST['saldo'])
	except :
		return HttpResponse('Valor no saldo incorrecto')

	saldo_existente = 0
	
	if not validateEmail(user):
		return HttpResponse('Email incorrecto')
	
	
	user = user.lower()
	user = Page_Users.all().filter("email =", user)
	
	if user.count() == 0:
		return HttpResponse('Utilizador inexistente')
	
	if user.count() != 1:
		return HttpResponse('Existe mais que um user com o mesmo email, erro severo')
		
	#update saldo
	user_actual = user[0]
	saldo_existente = user_actual.saldo
	user_actual.saldo = saldo_existente + plus_saldo
	
	
	#update saldo total
	saldo_total = user_actual.saldo_total
	saldo_total = saldo_total + plus_saldo
	user_actual.saldo_total = saldo_total
	
	
	#put
	user_actual.put()
	
	logging.info("CARREGAMENTO: O user " 
		+ request.user.email 
		+ " carregou o user " 
		+ user_actual.email 
		+ " com " 
		+ str(plus_saldo) 
		+ " Creditos")
	
	return HttpResponse('Efectuado com sucesso')

#Used when user buys cards

#Actualiza o numero de clicks de acordo com raridade
	#faz reset aos clicks nas seguintes condicoes
	#rara    = 100 -> reset
	#incomum = 150 -> reset
	#comum   = 150 -> reset
	
#inverted = True means selling a card
#Winner = True means user won X credits
def change_saldo_user(user_temp,rarity, inverted=False, winner=False):
	
	value = None
	
	if rarity == "Rare":
		value = VALUE_OF_RARE_CARD
	if rarity == "Mytic":
		value = VALUE_OF_RARE_CARD
	if rarity == "Uncommon":
		value = VALUE_OF_UNCOMMON_CARD
	if rarity == "Common":
		value = VALUE_OF_COMMON_CARD
		
	
	user_actual = Page_Users.all().filter("email =", user_temp.email).get()
	
	saldo_existente = user_actual.saldo
	saldo_novo = None
	
	if inverted:
		saldo_novo = saldo_existente + value/2
	else:
		saldo_novo = saldo_existente - value
	
	if saldo_novo < 0:
		return None
		
	user_actual.saldo = saldo_novo
	
	#WON (Y clicks)
	if winner:
		user_actual.saldo = saldo_novo + constants.WINNER_VALUE
	
	
	if inverted == False:
		n_clicks = user_actual.clicks_total
		n_clicks = n_clicks + 1
		user_actual.clicks_total = n_clicks
		
		if rarity == "Rare":
			user_actual.clicks_total_rare = user_actual.clicks_total_rare + 1
			user_actual.clicks_total_rare_fix = user_actual.clicks_total_rare_fix + 1
			if user_actual.clicks_total_rare > constants.RESET_CLICKS_RARE:
				user_actual.clicks_total_rare = 1
		if rarity == "Mytic":
			user_actual.clicks_total_rare = user_actual.clicks_total_rare + 1
			user_actual.clicks_total_rare_fix = user_actual.clicks_total_rare_fix + 1
			if user_actual.clicks_total_rare > constants.RESET_CLICKS_RARE:
				user_actual.clicks_total_rare = 1
		if rarity == "Uncommon":
			user_actual.clicks_total_uncommon = user_actual.clicks_total_uncommon + 1
			user_actual.clicks_total_uncommon_fix = user_actual.clicks_total_uncommon_fix + 1
			if user_actual.clicks_total_uncommon > constants.RESET_CLICKS_UNCOMMON:
				user_actual.clicks_total_uncommon = 1
		if rarity == "Common":
			user_actual.clicks_total_common = user_actual.clicks_total_common + 1
			user_actual.clicks_total_common_fix = user_actual.clicks_total_common_fix + 1
			if user_actual.clicks_total_common > constants.RESET_CLICKS_COMMON:
				user_actual.clicks_total_common = 1
	
	
	user_actual.put()
	
	return user_actual
	
#update saldo of given user
def update_saldo_from_user(user,value):
	user = Page_Users.all().filter("email =", user).get()
	user.saldo = user.saldo + value
	user.put()
	
	

#changes saldo of user based by metodo for card sending.
#Returns True if user has saldo
#Return False if he does not	
def change_saldo_user_checkout_by_metodo(user,metodo):

	CORREIO_INTERNACIONAL = constants.CORREIO_INTERNACIONAL
	CORREIO_AZUL = constants.CORREIO_AZUL
	CORREIO_REGISTADO = constants.CORREIO_REGISTADO
	CORREIO_INTERNACIONAL_COM_RASTREIO = constants.CORREIO_INTERNACIONAL_COM_RASTREIO
	
	user = Page_Users.all().filter("email =", user).get()
	
	saldo = user.saldo
	
	if metodo == "Internacional":
		if saldo < CORREIO_INTERNACIONAL:
			return False
		else:
			saldo = saldo - CORREIO_INTERNACIONAL
			user.saldo = saldo
			user.put()
			return True
			
	if metodo == "Azul":
		if saldo < CORREIO_AZUL:
			return False
		else:
			saldo = saldo - CORREIO_AZUL
			user.saldo = saldo
			user.put()
			return True
			
	if metodo == "Registado":
		if saldo < CORREIO_REGISTADO:
			return False
		else:
			saldo = saldo - CORREIO_REGISTADO
			user.saldo = saldo
			user.put()
			return True
	
	if metodo == "Internacional Rastreio":
		if saldo < CORREIO_INTERNACIONAL_COM_RASTREIO:
			return False
		else:
			saldo = saldo - CORREIO_INTERNACIONAL_COM_RASTREIO
			user.saldo = saldo
			user.put()
			return True
	
	
def search_users(request):
	
	keywords = request.POST['keywords']
	users = Page_Users.search(keywords) 
		
	return HttpResponse(users_to_table(users))

	
	
	
def recover_password_for_user(request):
	email = None

	try:
		email = request.POST['email']
	except:
		return HttpResponse("O Email n&atilde;o apresenta uma sintaxe correcta.")
	
	if not validateEmail(email):
		return HttpResponse("O Email n&atilde;o apresenta uma sintaxe correcta.")
	
	new_password = generate_random_string()
	
	user = Page_Users.all().filter('email =',email).get()
	
	if user == None:
		return 'Utilizador inexistente'
	
	erros = change_password_for_user(user.id,new_password)
	
	if erros == "Success":
		mail_utils.sendPasswordReset(user.email,new_password,user.nome)
	
	
	return HttpResponse(erros)

#changes password of a user
def change_password(request):
	
	user = request.user.username
	
	
	password = None
	password1 = None
	password2 = None
	
	try:
		password = request.POST['password']
		password1 = request.POST['password_1']
		password2 = request.POST['password_2']
	except:
		return HttpResponse('Campos mal preenchidos')
	
	
	u = User.objects.get(username__exact=user)
	
	
	if not u.check_password(password):
		return HttpResponse('Password original incorrecta')
	
	if password1 != password2:
		return HttpResponse('As novas passwords n&atilde;o sn&atilde;o iguais')
	
	
	new_password = password1
	
	allowed_expressions_password = re.compile('^[\w\W]+$')
	
	if len(new_password) < 6 or len(new_password) > 16:
		return HttpResponse("Password com tamanho inv&aacute;lido.")
	
	match_password = allowed_expressions_password.match(new_password)
	if not match_password:
		return HttpResponse("Password com caracteres inv&aacute;lidos.")
	
	
	erros = change_password_for_user(user,new_password)
	
	return HttpResponse(erros)
	
#changes info of user, morada codigo postal telefone e pais	
def change_info(request):

	user = request.user.email
	
	morada = None
	codigopostal = None
	codigopostal2 = None
	telefone = None
	#pais = None
	
	try:
		morada = request.POST['morada']
	except:
		return HttpResponse('Morada mal preenchida')
	
	try:
		codigopostal = request.POST['codigopostal']
	except:
		return HttpResponse('C&oacute;digo postal mal preenchido')	
		
	try:
		codigopostal2 = request.POST['codigopostal2']
	except:
		return HttpResponse('C&oacute;digo postal mal preenchido')	

	try:
		telefone = request.POST['telefone']
	except:
		return HttpResponse('Telefone mal preenchido')
	
	#try:
	#	pais = request.POST['pais']
	#except:
	#	return HttpResponse('Pa&iacute;s mal preenchido')
	
	
	cod_postal = codigopostal+"-"+codigopostal2
	
	#check server side info
	error = verify_partial_user_info(morada,codigopostal,telefone)
	
	#print in page error if any
	if error != None:
		return HttpResponse(error)
	else:
		
		user = Page_Users.all().filter("email =", user).get()
			
		user.morada = morada 
		user.codigopostal = cod_postal
		user.telefone = telefone
		#user.pais = pais
	
		user.put()
	
		return HttpResponse("Success")
		

			
		
def complete_checkout(request):
	
	allowed_order_random_store = ['All','Random','Store']
	
	try:
		metodo = request.POST['option']
	except:
		return HttpResponse("Tem de selecionar um modo de envio")
	try:
		order_random_store = request.POST['what_to_send']
	except:
		return HttpResponse("Tem de selecionar o que deseja receber")
	
	
	if order_random_store not in allowed_order_random_store:
		return HttpResponse("Tem de selecionar o que deseja receber")
	
	random_output = ""
	store_output = ""
	
	if order_random_store == "Random":
		return HttpResponse(complete_checktout_random(request))
	elif order_random_store == "Store":
		return HttpResponse(complete_checktout_store(request))
	elif order_random_store == "All":
		random_output = complete_checktout_random(request,True)
		store_output = complete_checktout_store(request)
	
	if random_output != "Success":
		return HttpResponse(random_output)
	if store_output != "Success":
		return HttpResponse(store_output)
	
	
	return HttpResponse("Success")

#portes pagos eh quando o cliente quer receber tudo entao os portes podem ser pagos depois
def complete_checktout_random(request,portes_pagos=False):
	
	user = request.user.email
	metodo = None
	codigo = None
	
	allowed_metodo = ['Internacional','Internacional Rastreio','Azul','Registado']
	
	
	try:
		metodo = request.POST['option']
	except:
		return "Tem de selecionar um modo de envio"

	#porque o correio internacional com rastreio vem com "_" mas no model nao suporta essa string
	metodo = metodo.replace("_"," ")
		
	if metodo not in allowed_metodo:
		return "Modo de envio incorrecto"
	
	if portes_pagos == False and not change_saldo_user_checkout_by_metodo(user,metodo):
		return "Saldo insuficiente para o modo de envio selecionado"
	
	last = Historico.all().order('-date').get()
	
	if last == None:
		codigo = 1
	else:
		codigo = last.codigo + 1
	
	cartas = compras_historico_utils.return_and_delete_list_of_cards_by_user(user)
	
	if cartas == None:
		return "Tem de ter cartas no seu carrinho para completar uma compra"
	
	
	user_info = get_user_info(user)
	
	historico = Historico(user = user,
						codigo = codigo,
						cartas = cartas,
						morada = user_info.morada,
						codigopostal = user_info.codigopostal,
						telefone = user_info.telefone,
						pais = user_info.pais,
						metodo = metodo)
						
	historico.put()
							
	return "Success"
	

	
def complete_checktout_store(request):
	
	user = request.user.email
	metodo = None
	codigo = None
	
	allowed_metodo = ['Internacional','Internacional Rastreio','Azul','Registado']
	
	
	try:
		metodo = request.POST['option']
	except:
		return "Tem de selecionar um modo de envio"

	#porque o correio internacional com rastreio vem com "_" mas no model nao suporta essa string
	metodo = metodo.replace("_"," ")
		
	if metodo not in allowed_metodo:
		return "Modo de envio incorrecto"
	
	
	last = Historico.all().order('-date').get()
	
	if last == None:
		codigo = 1
	else:
		codigo = last.codigo + 1
		
		
	####################################GUITA##########################################
	#store card list
	card_list_store = compras_historico_utils.return_list_of_cards_from_request(request)	
	total_price = compras_historico_utils.get_total_price_cart(card_list_store)
	
	if metodo == 'Internacional':
		total_price = total_price + constants.CORREIO_INTERNACIONAL
	elif metodo == 'Registado':
		total_price = total_price + constants.CORREIO_REGISTADO
	elif metodo == 'Internacional Rastreio':
		total_price = total_price + constants.CORREIO_INTERNACIONAL_COM_RASTREIO
	elif metodo == 'Azul':
		total_price = total_price + constants.CORREIO_AZUL
	
	update_saldo_from_user(request.user.email,total_price*-1)	

	
	cartas = compras_historico_utils.return_list_of_cards_from_request(request)
	
	if cartas == None:
		return "Tem de ter cartas no seu carrinho para completar uma compra"
	
	real_cartas_order = []
	for carta in cartas:
		toAdd = carta.nome + "###" + carta.raridade + "###" + carta.edicao + " x " + str(carta.quantity)
		real_cartas_order.append(toAdd)
		#####################################STOCK - RETIRAR"###########################################
		card_database_utils.decrement_card_stock_store(carta.nome,carta.edicao,carta.quantity)
		
		
	user_info = get_user_info(user)
	
	historico = Historico(user = user,
						codigo = codigo,
						cartas = real_cartas_order,
						morada = user_info.morada,
						codigopostal = user_info.codigopostal,
						telefone = user_info.telefone,
						pais = user_info.pais,
						metodo = metodo)
						
	historico.put()
	
	compras_historico_utils.empty_store_cart(request)
							
	return "Success"
	
	
#Transfers credit between users
def transfer_credit(request):

	user = request.user.email
	valor = None
	email_que_recebe_transferencia = None
	
	try:
		valor = request.POST['valor']
	except:
		return HttpResponse("Error###O campo valor s&oacute; pode conter valores num&eacute;ricos")
		
	try:
		email_que_recebe_transferencia = request.POST['email']
	except:
		return HttpResponse("Error###Campo de email n&atilde;o pode estar vazio")
		
	if valor == 0:
		return HttpResponse("Error###Quer mesmo transferir 0 cr&eacute;ditos?")
			
			
	try:
		valor = int(valor)
	except:
		return HttpResponse("Error###O campo valor s&oacute; pode conter valores num&eacute;ricos")
		
	if valor < 30:
		return HttpResponse("Error###O valor m&iacute;nimo &eacute; de 30 cr&eacute;ditos!")	
	
	if not validateEmail(email_que_recebe_transferencia):
		return HttpResponse("Error###Email inv&aacute;lido")
	
	if user.lower() == email_que_recebe_transferencia.lower():
		return HttpResponse("Error###N&atilde;o pode transferir saldo para si mesmo")
	
	
	#para as excepcoes das lojas parceiras (nao pagam nada)
	CUSTO_TRANSFERENCIA_ENTRE_USERS_LOCAL = constants.CUSTO_TRANSFERENCIA_ENTRE_USERS
	if user in constants.EXCEPCOES_NOS_CUSTOS_DE_TRANSFERENCIAS:
		CUSTO_TRANSFERENCIA_ENTRE_USERS_LOCAL = constants.CUSTO_TRANSFERENCIA_ENTRE_USERS_PARA_PARCEIROS
	#Fim das excepcoes para parceiros	
	
	user_original =	get_user_info(user)
	user_a_transferir = get_user_info(email_que_recebe_transferencia)
	
	if user_original == None or user_a_transferir == None:
		return HttpResponse("Error###User inv&aacute;lido")
	
	if user_original.saldo < valor + CUSTO_TRANSFERENCIA_ENTRE_USERS_LOCAL:
		return HttpResponse("Error###N&atilde;o tem saldo suficiente para efectuar esta opera&ccedil;&atilde;o")
	else:
		saldo_do_original = user_original.saldo
		saldo_do_original = saldo_do_original - valor - CUSTO_TRANSFERENCIA_ENTRE_USERS_LOCAL
		user_original.saldo = saldo_do_original
			
		logging.info("saldo apos tirar: " + str(user_original.saldo))
			
		saldo_do_que_recebe = user_a_transferir.saldo
		saldo_do_que_recebe = saldo_do_que_recebe + valor
		user_a_transferir.saldo = saldo_do_que_recebe
		user_a_transferir.saldo_total = user_a_transferir.saldo_total + saldo_do_que_recebe
		
		
		logging.info("saldo apos meter: " + str(user_a_transferir.saldo))
	
	
	user_original.put()
	user_a_transferir.put()
	
	
	return HttpResponse("Success###Transferiu com sucesso " + str(valor) +" cr&eacute;dito(s) para a conta " + email_que_recebe_transferencia +"###Saldo###"+ str(user_original.saldo))

#confirms payment for user
def confirm_payment_user(user):
	payment_order = carregamentos.all().filter("user =", user).get()
	
	if payment_order == None:
		return HttpResponse("Error###O user " + user + " n&atilde;o fez qualquer pedido de carregamento")
	
	if payment_order.valor == "0":
		return HttpResponse("Error###O user " + user + " n&atilde;o fez qualquer pedido de carregamento")
	
	logging.info("Foi confirmado o pagamento de " + str(payment_order.valor) + " para o user " + user + " na moeda " + payment_order.moeda)
	
	
	#TO PERMANENT RECORDS
	history_payment = historico_carregamentos(user = payment_order.user,
						metodo = payment_order.metodo,
						valor = payment_order.valor,
						moeda = payment_order.moeda)
	history_payment.put()
	
	
	#delete from temp record
	payment_order.delete()
	
	return HttpResponse("Success###O user " + user + " teve o seu carregamento confirmado")
	
	
#returns False if user already has payment 
#if store = True means we can add payment even if one exists
def add_payment_user(request,user, valor, metodo,store=False):
	valor = str(valor)
	
	#pais = get_pais_from_email(user)
	pais = get_pais_from_request(request)
	
	if store:
		moeda = "creditos"
	elif pais == "Portugal":
		moeda = "Euro"
	elif pais == "Brasil":
		moeda = "Real"
	
	ok = True
	nok = False
	
	payment_order = carregamentos.all().filter("user =", user).get()
	
	#does not exist
	if payment_order == None:
		carregamento = carregamentos(user = user,
								metodo = metodo,
								valor = valor,
								moeda = moeda)
		carregamento.put()
		
		return ok
	
	#payment order already exists
	if payment_order.valor != float(0) and not store:
		return nok
	
	#payment order does not exist
	payment_order.metodo = metodo
	payment_order.valor = valor
	payment_order.moeda = moeda
	payment_order.put()
	
	return ok

	
#registers payment intentions	
def register_payment(request):
	metodo = None
	valor = None
	nice_metodo = None
	
	#pais = get_pais_from_email(request.user.email)
	pais = get_pais_from_request(request)
	
	try:
		valor = request.POST['valor']
	except:
		return HttpResponse("Error###Valor do carregamento incorrecto")
	try:
		metodo = request.POST['metodo']
	except:
		return HttpResponse("Error###M&eacute;todo inv&aacute;")
	try:
		true_value = float(valor)
	except:
		return HttpResponse("Error###Valor do carregamento incorrecto")
	
	if true_value == 0:
		return HttpResponse("Error###N&atilde;o pode carregar 0 &euro;")
		
	
	if metodo.startswith("Transferencia"):
		nice_metodo = "Transferencia Bancaria"
	elif metodo.startswith("PAYPAL"):
		nice_metodo = "Paypal"
	elif metodo.startswith("Pagamento"):
		nice_metodo = "Pagamento servicos"
	else:
		return HttpResponse("Error###M&eacute;todo inv&aacute;")
	
	if true_value < 5 and pais == "Portugal":
		return HttpResponse("Error###Carregamento m&iacute;nimo de 5 &euro;")
	if true_value < 5 and pais == "Brasil":
		return HttpResponse("Error###Carregamento m&iacute;nimo de 15 Reais")
	
	if add_payment_user(request,request.user.email, true_value, nice_metodo):
		logging.info("O user " + request.user.email + " pediu um carregamento de " + str(true_value) + " creditos")
		return HttpResponse("Success")
	else:
		return HttpResponse("Error###J&aacute; tem um pedido de cr&eacute;dito pendente")


#Returns method of payment given request
def get_payment_method_by_user(request):
	payment_order = carregamentos.all().filter("user =", request.user.email).get()
	return payment_order.metodo
	
		
#returns all incomplete payments
def admin_view_payments(request):
	
	payments = carregamentos.all().filter('valor >', str(0))

	return HttpResponse(payments_to_table(payments))

#confirms payment for user	
def admin_payment_confirmation(request):
		
	user = None

	try:
		user = request.POST['user']
	except:
		return HttpResponse("Error###User n&atilde;o existe")
		
	return confirm_payment_user(user)
	