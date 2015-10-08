# -*- coding: utf-8 -*-

from google.appengine.api import mail

import smtplib

#User modules
import constants


ADMIN_MAIL = constants.ADMIN_MAIL
SITE_NAME = constants.SITE_NAME
SITE_LOCATION = constants.SITE_LOCATION

#registration mail (for new users)
def sendRegistrationMain(para,random_number):
	mensagem = """
	Muito Obrigado pelo seu interesse.
	
	De forma a completar o seu registo no site """+ SITE_NAME  +""" é favor seguir o link:
	http://""" + SITE_LOCATION + """/registration/""" + random_number + """
	
	O link irá estar activo durante 24 horas
	
	Cumprimentos da equipa do """ + SITE_NAME + """
	
	Muito obrigado
	"""

	assunto="Registo em " + SITE_NAME
	
	sendMail(assunto,mensagem,para)

#password reset mail	
def sendPasswordReset(para,new_password,name):
	mensagem = """	
	Caro """ + name + """,
	
	A sua nova password para o site """+ SITE_NAME +""" &eacute;: """ + new_password +"""
	
	Recomendamos que mude a sua password o quanto antes.
	
	
	Cumprimentos da equipa do """ + SITE_NAME + """
	
	Muito obrigado
	"""

	assunto="Registo em " + SITE_NAME
	
	sendMail(assunto,mensagem,para)


	
#GENERCIC SEND MAIL
def sendMail(assunto,mensagem,para,he_who_sends=ADMIN_MAIL):


	message = mail.EmailMessage(sender=he_who_sends,
                            subject=assunto)

	message.to = para
	message.body = mensagem

	message.send()
	