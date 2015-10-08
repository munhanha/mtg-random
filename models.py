#!/usr/bin/env python
#
# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#user models
import random_utils
import constants

import logging

import re, unicodedata


#cleans search parameters (PINGE)
RE__TEXT_SEARCH_INDEX = re.compile('\w+', re.U)
def text_indexes(*objs, **params):
	indexes = params['text_search_indexes'] if 'text_search_indexes' in params else []
	normalize = params['normalize'] if 'normalize' in params else True
	exclude_non_normalized = params['exclude_non_normalized'] if 'exclude_non_normalized' in params else True
	for obj in objs:
		if not obj: continue
		str_ = unicode(obj)
		strs = RE__TEXT_SEARCH_INDEX.findall(str_.strip().lower())
		for s in strs:
#      if s == 'u': continue # TODO: ignoring 'u' from unicode objects
			if s not in indexes: indexes.append(s)
			if normalize:
				ns = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
				if ns != s and ns not in indexes:
					if exclude_non_normalized: indexes.remove(s)
					indexes.append(ns)
	return indexes

##################################
##############USERS###############
##################################
from google.appengine.ext import db

#keeps finals users
class Page_Users(db.Model):
	email = db.StringProperty()
	id = db.StringProperty(default="")
	nome = db.StringProperty()
	morada = db.StringProperty()
	codigopostal = db.StringProperty()
	telefone = db.StringProperty()
	pais = db.StringProperty()
	saldo = db.IntegerProperty(default=25)
	saldo_total = db.IntegerProperty(default=0)
	#VALORES FIXOS
	clicks_total = db.IntegerProperty(default=0)
	clicks_total_rare_fix = db.IntegerProperty(default=0)
	clicks_total_uncommon_fix = db.IntegerProperty(default=0)
	clicks_total_common_fix = db.IntegerProperty(default=0)
	#VALORES VARIAVEIS
	clicks_total_rare = db.IntegerProperty(default=0)
	clicks_total_uncommon = db.IntegerProperty(default=0)
	clicks_total_common = db.IntegerProperty(default=0)
	#NOT YET USED
	filtros = db.StringProperty()
	text_search_indexes = db.StringListProperty(default=[])
	
	def put(self, **kwargs):
		self.text_search_indexes = text_indexes(self.email, self.nome, self.morada, self.codigopostal, self.telefone, self.pais)
		super(Page_Users, self).put(**kwargs)
 
	@classmethod
	def search(cls, query, **params):
		q = cls.all() #.filter('email =', email) # TODO: 2b customized
		for s in 	text_indexes(query): # ['flame', 'jet']; ['rui', 'pinge', 'cacador']
			q = q.filter('text_search_indexes =', s)
		return q

#keeps temporary users	
class Temp_User(db.Model):
	email = db.StringProperty()
	nome = db.StringProperty()
	morada = db.StringProperty()
	codigopostal = db.StringProperty()
	telefone = db.StringProperty()
	pais = db.StringProperty()
	confirmation = db.StringProperty()
	
##################################
##############CARTAS##############
##################################
class cartas_mtg(db.Model):
	nome = db.StringProperty()
	cor = db.StringProperty()
	custo = db.StringProperty()
	tipo = db.StringProperty()
	poder_resistencia = db.StringProperty()
	texto = db.StringProperty()
	raridade = db.StringProperty()
	edicao = db.StringProperty()
	stock = db.IntegerProperty(default=0)
	importance = db.IntegerProperty(default=0)
	random_number = db.FloatProperty()
	disponivel = db.BooleanProperty()
	real_value = db.IntegerProperty(default=0)
	text_search_indexes = db.StringListProperty(default=[])
	
	#FOR FIRST PUT ONLY
	def put_DB(self, **kwargs):
		
		stock = self.stock
		
		if stock <= 0:
			self.disponivel = False
		else:
			self.disponivel = True
	
		self.text_search_indexes = text_indexes(self.nome, self.cor, self.custo, self.tipo, self.poder_resistencia, self.texto, self.raridade, self.edicao)
		super(cartas_mtg, self).put(**kwargs)
		
	def put(self, **kwargs):
		
		stock = self.stock
		
		if stock <= 0:
			self.disponivel = False
		else:
			self.disponivel = True
	
		super(cartas_mtg, self).put(**kwargs)	
 
	@classmethod
	def search(cls, query, **params):
		q = cls.all() #.filter('email =', email) # TODO: 2b customized
		for s in 	text_indexes(query): # ['flame', 'jet']; ['rui', 'pinge', 'cacador']
			q = q.filter('text_search_indexes =', s)
		return q
		
	#Fetches only admin defined ocurrences
	@classmethod
	def user_search(cls, query, colour, edition, **params):
		
		toReturn = []
		
		#Don t have keywords
		if query == "":
			query = colour + " " + edition
		
		
		if colour != '' and edition != '':
			q = cls.all().filter('edicao =', edition).filter('cor =', colour).filter('real_value >',0)
			for s in text_indexes(query):
				toReturn = q.filter('text_search_indexes =', s).fetch(constants.USER_SEARCH_COUNT_WITH_COLOUR_EDITION)
		elif colour !='':
			q = cls.all().filter('cor =', colour).filter('real_value >',0)
			for s in text_indexes(query):
				toReturn = q.filter('text_search_indexes =', s).fetch(constants.USER_SEARCH_COUNT)
		elif edition !='':
			q = cls.all().filter('edicao =', edition).filter('real_value >',0)
			for s in text_indexes(query):
				toReturn = q.filter('text_search_indexes =', s).fetch(constants.USER_SEARCH_COUNT)
		else:
			q = cls.all().filter('real_value >',0)
			for s in text_indexes(query):
				toReturn = q.filter('text_search_indexes =', s).fetch(constants.USER_SEARCH_COUNT)
			
		return toReturn
		
##################################
#############Compras##############
##################################
class compras(db.Model):
	user = db.StringProperty()
	cartas = db.StringListProperty(default=[])
	last_buy = db.DateTimeProperty(auto_now_add=True)

##################################
############Historico#############
##################################
class Historico(db.Model):
	user = db.StringProperty(required=True)
	codigo = db.IntegerProperty(required=True)
	cartas = db.StringListProperty(required=True, default=[])
	metodo = db.StringProperty(choices=set(["Internacional", "Internacional Rastreio", "Azul", "Registado"]))
	estado = db.StringProperty(required=True, choices=set(["Por Processar", "Pagamento Aceite", "Processado", "Enviado"]), default="Por Processar")
	morada = db.StringProperty()
	codigopostal = db.StringProperty()
	telefone = db.StringProperty()
	pais = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	text_search_indexes = db.StringListProperty(default=[])
	
	
	def put(self, **kwargs):
		self.text_search_indexes = text_indexes(self.user, self.codigo, self.metodo, self.morada, self.telefone, self.codigopostal)
		super(Historico, self).put(**kwargs)
 
	@classmethod
	def search(cls, query, **params):		
		estado = params['estado']
		q = cls.all().filter('estado =', estado) # TODO: 2b customized
		for s in 	text_indexes(query): # ['flame', 'jet']; ['rui', 'pinge', 'cacador']
			q = q.filter('text_search_indexes =', s)
		return q
	
##################################
##########Carregamentos###########
##################################
class carregamentos(db.Model):
	user = db.StringProperty(required=True)	
	metodo = db.StringProperty(required=True)
	valor = db.StringProperty(required=True)
	moeda = db.StringProperty(required=True)
	date = db.DateTimeProperty(auto_now_add=True)

##################################
#####Historico Carregamentos######
##################################
class historico_carregamentos(db.Model):
	user = db.StringProperty(required=True)	
	metodo = db.StringProperty(required=True)
	valor = db.StringProperty(required=True)
	moeda = db.StringProperty(required=True)
	date = db.DateTimeProperty(auto_now_add=True)
	
	
##################################
##CARTAS QUE OS USERS PODEM VER###
##################################	
class user_cards(db.Model):
	name_card = db.StringProperty(required=True)	
		
#DEPOIS REMOVER	
class db_fixer_edition(db.Model):
	edition = db.StringProperty()