from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
	(r'^$', 'views.index'),
	(r'^start$', 'views.start'),
	(r'^register.html$', 'views.register'),
	(r'^addUser_temp$', 'views.addUser_temp'),
	
	#registration
	(r'^registration/(?P<code>\d+)/$', 'views.finish_registration'),
	(r'^waiting_register_confirmation.html$', 'views.waiting_register_confirmation'),
	(r'^registry_successful.html$', direct_to_template, {'template': 'registry_successful.html'}),
	(r'^registry_unsuccessful.html$', direct_to_template, {'template': 'registry_unsuccessful.html'}),
	
	#recover password
	(r'^recover_password$', direct_to_template, {'template': 'recover_password.html'}),
	(r'^recover_password_reset$', 'views.recover_password_reset'),
	(r'^password_recovery_success$', direct_to_template, {'template': 'password_recovery_success.html'}),
	
	(r'^faqs$', direct_to_template, {'template': 'faqs.html'}),
	
	(r'^contacts$', direct_to_template, {'template': 'contacts.html'}),
	
	(r'^info$', direct_to_template, {'template': 'info.html'}),
	
	###############################################
	##############NORMAL USER STUFF#################
	###############################################
	
	#main page for normal user(direct to game)
	(r'^main_page$', 'views.main_page'),
	
	#change_password Page
	(r'^change_password$', 'views.change_password'),
	
	#change_password
	(r'^main_page_change_password$', 'views.main_page_change_password'),
	
	#change_info Page
	(r'^change_info$', 'views.change_info'),
	
	#change_info
	(r'^main_page_change_info$', 'views.main_page_change_info'),
	
	#get random card
	(r'^get_random_card$',  'views.get_random_card'),
	
	#sell card
	(r'^sell_card$',  'views.sell_card'),
	
	#sell ALL THE CARDS
	(r'^sell_all$', 'views.sell_all'),
	
	#check cards won
	(r'^view_cards$',  'views.view_cards'),
	
	#Checkout
	(r'^checkout$',  'views.checkout'),
	
	#Complete checkout
	(r'^complete_checkout$',  'views.complete_checkout'),
	
	#Checkout success
	(r'^success_checkout$',  'views.success_checkout'),
	
	#View Orders
	(r'^orders$',  'views.orders'),
	
	#Transfer Credito Page
	(r'^transfer_credit$',  'views.transfer_credit'),
	
	#Transfer Credito
	(r'^transfer_credit_between_users$',  'views.transfer_credit_between_users'),
	
	#User payment info
	(r'^payment$',  'views.payment'),
	
	#Registar payment
	(r'^register_payment$',  'views.register_payment'),
	
	#Present options after payment registration
	(r'^payment_registered$',  'views.payment_registered'),
	
	#Client view stock
	(r'^client_view_stock$',  'views.client_view_stock'),
	
	#Client view stock
	(r'^main$',  'views.main'),
	
	#Client store view
	(r'^store$',  'views.store'),
	
	#Client store view
	(r'^user_search_cards$',  'views.user_search_cards'),
	
	#Client add to cart
	(r'^user_add_to_cart$',  'views.user_add_to_cart'),

	#Clean client cart
	(r'^clean_user_cart$',  'views.clean_user_cart'),

	#Change card quantity in user cart (store)
	(r'^change_quantity_card$',  'views.change_quantity_card'),	

	#logout
	(r'^sair$', 'views.sair'),
	

	###############################################
	##############ADMIN STUFF######################
	###############################################
	
	#main page for staff user
	(r'^staff_admin$', 'views.staff_admin'),
	
	#search users
	(r'^search_users$', 'views.search_users'),
	
	#search cards admin
	(r'^search_cards_admin$', 'views.search_cards_admin'),
	
	#search orders admin
	(r'^search_orders_admin$', 'views.search_orders_admin'),
	
	#update Saldo
	(r'^update_saldo$', 'views.update_saldo'),
	
	#add card to data base
	(r'^add_card_db$', 'views.add_card_db'),
	
	#change stock and importance of card
	(r'^change_card_stock_importance$',  'views.change_card_stock_importance'),
	
	#change order state
	(r'^change_order_state$', 'views.change_order_state'),
	
	#get orders
	(r'^admin_view_payments$', 'views.admin_view_payments'),
	
	#get all non final payments
	(r'^admin_view_payments$', 'views.admin_view_payments'),
	
	#confirms payment by user (delete payment request)
	(r'^admin_payment_confirmation$', 'views.admin_payment_confirmation'),
	
	#Shows current cart of given user
	(r'^admin_view_user_cart$', 'views.admin_view_user_cart'),
	
	#gets and shows cards of a specific order
	(r'^orders/(?P<codigo>\d+)/$', 'views.get_specific_order'),
	
	#Admin gives order to sell all cards of given user
	(r'^admin_sell_all$', 'views.admin_sell_all'),
	
	
	#Checks states of cards
	(r'^check_DB$',  'views.check_DB'),
	
	#Maintenance(???) url
	(r'^fix_DB$',  'views.fix_DB'),
	
	
	###############################################
	###############CRON JOBS#######################
	###############################################
	
	#Client store view
	(r'^change_user_cards$',  'views.change_user_cards'),
	
	
)
