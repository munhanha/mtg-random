# -*- coding: utf-8 -*-

import datetime

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template

from google.appengine.api import users

from google.appengine.ext import db

import logging

#USER MODULES
import mail_utils
import random_utils
import page_users_utils
from decorators import is_staff
import card_database_utils
import constants
import compras_historico_utils
import maintenance

#Django Authentication
#from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login	, logout


#decorators
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


#####################################
##########ANONYMOUS USER#############
#####################################

def index(request):
	if request.user.is_staff:
		return HttpResponseRedirect("staff_admin")
	if request.user.is_authenticated():
		return HttpResponseRedirect("main")
	if not request.user.is_authenticated():
		return direct_to_template(request,"index.html",
			{'valor_do_site':constants.VALOR_MOEDA_DO_SITE_PORTUGAL, 
			'moeda':constants.MOEDA_DA_PAGINA ,
			'preco_comum':constants.VALUE_OF_COMMON_CARD,
			'preco_incomum': constants.VALUE_OF_UNCOMMON_CARD, 
			'preco_rara': constants.VALUE_OF_RARE_CARD,
			'preco_venda_comum':constants.VALUE_OF_COMMON_CARD/2, 
			'preco_venda_incomum': constants.VALUE_OF_UNCOMMON_CARD/2, 
			'preco_venda_rara': constants.VALUE_OF_RARE_CARD/2})

#login process
def start(request):
	return page_users_utils.page_login(request)
	
#fazer logout
@login_required(login_url='/')
def sair(request):
	logout(request)
	return direct_to_template(request, "index.html", {'info': "Obrigado pela sua visita."})
	

def register(request):
	return render_to_response('register.html')
		
def waiting_register_confirmation(request):
	return render_to_response('waiting_register_confirmation.html')

#adds user	
def addUser_temp(request):
	return page_users_utils.page_addUser_temp(request)
	
	
#ends registration	
def finish_registration(request,code):
	ok = page_users_utils.finish_registration(code)
	if ok:
		return HttpResponseRedirect('../../registry_successful.html')
	else:
		return HttpResponseRedirect('../../registry_unsuccessful.html')
	

#client view stock	
def client_view_stock(request):
	cards = card_database_utils.get_change_user_cards()
	rare1 = cards[:5]
	rare2 = cards[5:10]
	uncommon = cards[10:15]
	common = cards[15:20]
	
	return direct_to_template(request, "client_view_stock.html",
		{'rare1':rare1,
		'rare2':rare2,
		'uncommon':uncommon,
		'common':common})
	
#####################################
############ALL  USER	#############
#####################################
def recover_password_reset(request):
	return page_users_utils.recover_password_for_user(request)
	
#####################################
############NORMAL USER	#############
#####################################

#directs to main page algo game page
@login_required(login_url='/')
def main_page(request):
	pais = page_users_utils.get_pais_from_request(request)
	
	if pais == "Portugal":
		valor_moeda = constants.VALOR_MOEDA_DO_SITE_PORTUGAL
		return direct_to_template(request, "main_page.html", 
			{'portugal':pais,
			'valor_do_site':valor_moeda, 
			'moeda':constants.MOEDA_DA_PAGINA ,
			'preco_comum':constants.VALUE_OF_COMMON_CARD,
			'preco_incomum': constants.VALUE_OF_UNCOMMON_CARD, 
			'preco_rara': constants.VALUE_OF_RARE_CARD,
			'preco_venda_comum':constants.VALUE_OF_COMMON_CARD/2, 
			'preco_venda_incomum': constants.VALUE_OF_UNCOMMON_CARD/2, 
			'preco_venda_rara': constants.VALUE_OF_RARE_CARD/2, 
			'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)),
			'internacional': constants.CORREIO_INTERNACIONAL,
			'azul': constants.CORREIO_AZUL,
			'registado': constants.CORREIO_REGISTADO})
	if pais == "Brasil":	
		valor_moeda = constants.VALOR_MOEDA_DO_SITE_BRASIL
		return direct_to_template(request, "main_page.html", 
			{'brasil':pais,'valor_do_site':valor_moeda, 
			'moeda':constants.MOEDA_DA_PAGINA ,
			'preco_comum':constants.VALUE_OF_COMMON_CARD,
			'preco_incomum': constants.VALUE_OF_UNCOMMON_CARD, 
			'preco_rara': constants.VALUE_OF_RARE_CARD,
			'preco_venda_comum':constants.VALUE_OF_COMMON_CARD/2, 
			'preco_venda_incomum': constants.VALUE_OF_UNCOMMON_CARD/2, 
			'preco_venda_rara': constants.VALUE_OF_RARE_CARD/2, 
			'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)),
			'internacional': constants.CORREIO_INTERNACIONAL,
			'azul': constants.CORREIO_AZUL,
			'registado': constants.CORREIO_REGISTADO,
			'internacional_rastreio': constants.CORREIO_INTERNACIONAL_COM_RASTREIO})
		
	return direct_to_template(request, "main_page.html", 
		{'portugal':pais,'valor_do_site':valor_moeda, 
		'moeda':constants.MOEDA_DA_PAGINA ,
		'preco_comum':constants.VALUE_OF_COMMON_CARD,
		'preco_incomum': constants.VALUE_OF_UNCOMMON_CARD, 
		'preco_rara': constants.VALUE_OF_RARE_CARD,
		'preco_venda_comum':constants.VALUE_OF_COMMON_CARD/2, 
		'preco_venda_incomum': constants.VALUE_OF_UNCOMMON_CARD/2, 
		'preco_venda_rara': constants.VALUE_OF_RARE_CARD/2, 
		'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)),
		'internacional': constants.CORREIO_INTERNACIONAL,
		'azul': constants.CORREIO_AZUL,'registado': constants.CORREIO_REGISTADO})
	
@login_required(login_url='/')
def change_password(request):
	return direct_to_template(request, 'change_password.html', 
		{'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)), 
		'moeda': constants.MOEDA_DA_PAGINA})
	
@login_required(login_url='/')
def main_page_change_password(request):
	return page_users_utils.change_password(request)
	
@login_required(login_url='/')
def change_info(request):
	user = page_users_utils.get_user_info(request.user.email)
	cod_postal_items = page_users_utils.split_cod_postal(user.codigopostal)
	return direct_to_template(request, 'change_info.html', 
		{'nome':user.nome,'morada': user.morada, 
		'telefone':user.telefone, 
		'cod_post':cod_postal_items[0], 
		'cod_post2':cod_postal_items[1], 
		'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)), 
		'moeda': constants.MOEDA_DA_PAGINA} )

@login_required(login_url='/')
def main_page_change_info(request):
	return page_users_utils.change_info(request)
	
@login_required(login_url='/')
def get_random_card(request):
	return HttpResponse(random_utils.get_random_card_prepare(request))

@login_required(login_url='/')	
def sell_card(request):
	return HttpResponse(random_utils.sell_card(request))

@login_required(login_url='/')		
def sell_all(request):
	random_utils.sell_all(request)
	return HttpResponseRedirect("/view_cards")

@login_required(login_url='/')	
def view_cards(request):

	#random card list
	card_list = compras_historico_utils.return_list_of_cards_from_compras(request.user.email)
	
	#store card list
	card_list_store = compras_historico_utils.return_list_of_cards_from_request(request)
	
	#User country
	pais = page_users_utils.get_pais_from_request(request)
	
	#get total price for store cart
	total_price = compras_historico_utils.get_total_price_cart(card_list_store)
	
	#total price convertion
	total_price_conversion = card_database_utils.real_price_by_credits(total_price,pais)
	
	if pais == "Portugal":
		valor_moeda = constants.VALOR_MOEDA_DO_SITE_PORTUGAL
	if pais == "Brasil":	
		valor_moeda = constants.VALOR_MOEDA_DO_SITE_BRASIL
		
	if card_list == None and card_list_store == None:
		return direct_to_template(request, 'view_cartas.html', 
			{'valor_do_site':valor_moeda, 
			'moeda': constants.MOEDA_DA_PAGINA,
			'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)),'no_cards': "Nao tem cartas no seu carrinho"} )
	
	return direct_to_template(request, 'view_cartas.html', 
		{'valor_do_site':valor_moeda, 
		'moeda': constants.MOEDA_DA_PAGINA,
		'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)),
		'cartas_random': card_list,
		'cartas_store': card_list_store,
		'total_price':total_price, 
		'total_price_conversion':total_price_conversion})

@login_required(login_url='/')	
def checkout(request):

	user = page_users_utils.get_user_info(request.user.email)

	#random card list
	card_list_random = compras_historico_utils.return_list_of_cards_from_compras(request.user.email)
	
	#store card list
	card_list_store = compras_historico_utils.return_list_of_cards_from_request(request)
	
	#get total price for store cart
	total_price = compras_historico_utils.get_total_price_cart(card_list_store)
	
	#total price convertion
	total_price_conversion = card_database_utils.real_price_by_credits(total_price,user.pais)
	
	if user.pais == "Portugal":
		info = {'portugal':user.pais,
		'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)),
		'total_price':total_price,'total_price_conversion':total_price_conversion, 
		'moeda': constants.MOEDA_DA_PAGINA,'cartas_random': card_list_random,
		'cartas_store': card_list_store,
		'pais': user.pais,'morada': user.morada, 
		'telefone':user.telefone, 
		'cod_post':user.codigopostal,
		'nome':user.nome,
		'internacional': constants.CORREIO_INTERNACIONAL,
		'azul': constants.CORREIO_AZUL,
		'registado': constants.CORREIO_REGISTADO}
	if user.pais == "Brasil":
		info = {'brasil':user.pais,
		'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)),
		'total_price':total_price,
		'total_price_conversion':total_price_conversion, 
		'moeda': constants.MOEDA_DA_PAGINA,
		'cartas_random': card_list_random,
		'cartas_store': card_list_store,
		'pais': user.pais,
		'morada': user.morada, 
		'telefone':user.telefone, 
		'cod_post':user.codigopostal,
		'nome':user.nome,
		'internacional': constants.CORREIO_INTERNACIONAL,
		'internacional_rastreio': constants.CORREIO_INTERNACIONAL_COM_RASTREIO}
	
	return direct_to_template(request, 'checkout.html',info)

@login_required(login_url='/')	
def complete_checkout(request):
	return page_users_utils.complete_checkout(request)

@login_required(login_url='/')	
def success_checkout(request):
	last = compras_historico_utils.get_last_order_by_user(request.user.email)
	if last == None:
		return direct_to_template(request, 'success_checkout.html', {'no_orders':"XXX"})

	user = page_users_utils.get_user_info(request.user.email)
	
	saldo = user.saldo
	
	if saldo < 0:
		saldo = saldo*-1
		
		###WRONG!!!!
		nice_metodo = "Paypal"
		
		page_users_utils.add_payment_user(request,request.user.email, saldo, nice_metodo,store=True)
		if user.pais == "Portugal":
			return direct_to_template(request, 'success_checkout.html',
				{'order':last,
				'portugal':user.pais,
				'negative_client':saldo,
				'negative_client_conversion':card_database_utils.real_price_by_credits(saldo,user.pais)})
		if user.pais == "Brasil":
			return direct_to_template(request, 'success_checkout.html',
				{'order':last,
				'brasil':user.pais,
				'negative_client':saldo,
				'negative_client_conversion':card_database_utils.real_price_by_credits(saldo,user.pais)})
	
	return direct_to_template(request, 'success_checkout.html',{'order':last})

@login_required(login_url='/')
def orders(request):
	historicos = compras_historico_utils.from_user_get_historico(request.user.email)
	historicos = compras_historico_utils.arrange_cards_for_orders(historicos)
	if len(historicos) == 0:
		return direct_to_template(request, 'orders.html',
			{'no_orders':"Ainda n&atilde;o fez qualquer encomenda", 
			'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)), 
			'moeda': constants.MOEDA_DA_PAGINA})
	else:
		info = {'orders':historicos, 
		'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)), 'moeda': constants.MOEDA_DA_PAGINA}
		return direct_to_template(request, 'orders.html',info)	

@login_required(login_url='/')
def transfer_credit(request):
	user = page_users_utils.get_user_info(request.user.email)
	return direct_to_template(request, 
		'transfer_credit.html',
		{'transfer_cost':constants.CUSTO_TRANSFERENCIA_ENTRE_USERS,
		'moeda':constants.MOEDA_DA_PAGINA,
		'saldo':user.saldo })

@login_required(login_url='/')	
def transfer_credit_between_users(request):	
	return page_users_utils.transfer_credit(request)

@login_required(login_url='/')		
def payment(request):
	pais = page_users_utils.get_pais_from_request(request)
	
	if pais == "Portugal":
		return direct_to_template(request, 'payment.html',
			{'portugal':pais, 
			'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)), 
			'moeda': constants.MOEDA_DA_PAGINA,
			'valor_do_site': constants.VALOR_MOEDA_DO_SITE_PORTUGAL})
	if pais == "Brasil":
		return direct_to_template(request, 
			'payment.html',{'brasil':pais, 
			'saldo': str(page_users_utils.get_saldo_from_email(request.user.email)), 
			'moeda': constants.MOEDA_DA_PAGINA,
			'valor_do_site': constants.VALOR_MOEDA_DO_SITE_BRASIL})

@login_required(login_url='/')
def register_payment(request):
	return page_users_utils.register_payment(request)

@login_required(login_url='/')
def payment_registered(request):
	pais = page_users_utils.get_pais_from_request(request)
	metodo = page_users_utils.get_payment_method_by_user(request)
	
	metodo_code = 0
	if metodo == "Transferencia Bancaria":
		metodo = "transferencia"
		metodo_code = 1
	elif metodo == "Paypal":
		metodo = "paypal"
		metodo_code = 2
	elif metodo == "Pagamento servicos":
		metodo = "pagamento"
		metodo_code = 3
	
	if pais == "Portugal":
		return direct_to_template(request, 'payment_registered.html',{'portugal':pais,metodo:metodo_code})
	if pais == "Brasil":
		return direct_to_template(request, 'payment_registered.html',{'brasil':pais,metodo:metodo_code})
		
		
@login_required(login_url='/')
def main(request):
	user = page_users_utils.get_user_info(request.user.email)
	return direct_to_template(request, 'main.html',{'saldo':user.saldo, 'moeda': constants.MOEDA_DA_PAGINA})


@login_required(login_url='/')
#@is_staff(login_url='/')
def store(request):
	user = page_users_utils.get_user_info(request.user.email)
	numero_cartas = compras_historico_utils.get_total_number_cards(request)
	
	return direct_to_template(request, 
		'store.html',{'saldo':user.saldo,
		'moeda': constants.MOEDA_DA_PAGINA,
		'numero_cartas': numero_cartas,
		'number_results':constants.USER_SEARCH_COUNT})
	
@login_required(login_url='/')
def user_search_cards(request):	
	response = card_database_utils.search_cards_user(request)
	return response

@login_required(login_url='/')
def user_add_to_cart(request):
	response = compras_historico_utils.user_add_to_cart(request)
	return response

@login_required(login_url='/')
def clean_user_cart(request):
	compras_historico_utils.empty_store_cart(request)
	return HttpResponse("success")

@login_required(login_url='/')
def change_quantity_card(request):
	toReturn = compras_historico_utils.change_quantity_card(request)
	
	if toReturn == None:
		return HttpResponse("success")
		
	return toReturn
	
#####################################
############STAFF USER	#############
#####################################

#directs to main page for staff
@is_staff(login_url='/')
def staff_admin(request):
	return direct_to_template(request, 'staff_admin.html')
	
@is_staff(login_url='/')
def update_saldo(request):
	return page_users_utils.update_saldo(request)

@is_staff(login_url='/')
def search_users(request):
	return page_users_utils.search_users(request)
	
@is_staff(login_url='/')
def search_cards_admin(request):
	return card_database_utils.search_cards_admin(request)
	
@is_staff(login_url='/')
def add_card_db(request):
	return card_database_utils.add_card_to_db(request)

@is_staff(login_url='/')
def change_card_stock_importance(request):
	return card_database_utils.change_card_stock_importance(request)

@is_staff(login_url='/')
def search_orders_admin(request):
	return compras_historico_utils.search_orders_admin(request)

@is_staff(login_url='/')
def change_order_state(request):
	return compras_historico_utils.change_order_state(request)

@is_staff(login_url='/')
def admin_view_payments(request):
	return page_users_utils.admin_view_payments(request)
	
@is_staff(login_url='/')
def admin_payment_confirmation(request):
	return page_users_utils.admin_payment_confirmation(request)

@is_staff(login_url='/')	
def get_specific_order(request, codigo):
	return compras_historico_utils.get_specific_order(request,codigo)

@is_staff(login_url='/')	
def admin_view_user_cart(request):
	return compras_historico_utils.admin_view_user_cart(request)

@is_staff(login_url='/')	
def change_user_cards(request):
	return card_database_utils.change_user_cards(request)

@is_staff(login_url='/')	
def admin_sell_all(request):
	return HttpResponse(random_utils.admin_sell_all(request))
	
@is_staff(login_url='/')
def check_DB(request):
	return HttpResponse(maintenance.check_DB(request))


	
	
	
	
	
from models import Page_Users
from models import cartas_mtg
from models import db_fixer_edition
from google.appengine.api import memcache
#APAGAR - APENAS PARA TESTES!!!!!		
@is_staff(login_url='/')
def fix_DB(request):

	edition = db_fixer_edition.all().get()
	
	if edition == None:
		edition = db_fixer_edition(edition = "")
		edition.put()
		return HttpResponse("NO ME GUSTA")

	query = cartas_mtg.all().filter('edicao =',edition.edition).filter('raridade =','Uncommon')
	
	
	last_cursor = memcache.get('DB_Fixer')
	if last_cursor:
		query.with_cursor(last_cursor)
	entries = query.fetch(50)
	cursor = query.cursor()
	memcache.set('DB_Fixer', cursor)
	
	quantidade = len(entries)
	
	for carta in entries:
		carta.stock = carta.stock + 4
		carta.put()
	
	return HttpResponse("Success " + str(quantidade))
	