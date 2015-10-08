from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME

def is_staff(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
	"""
	Decorator for views that checks that the user is staff, redirecting
	to the log-in page if necessary.
	Possible usage:
	@is_staff
	def view....
	
	urlpatterns = patterns('',
		(r'^databrowse/(.*)', is_staff(databrowse.site.root)),
	)
	"""
	actual_decorator = user_passes_test(
		lambda u: u.is_staff,
		 login_url=login_url,
		redirect_field_name=redirect_field_name
	)
	if function:
		return actual_decorator(function)
	return actual_decorator
	
def is_superuser(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
	"""
	Decorator for views that checks that the user is superuser, redirecting
	to the log-in page if necessary.
	Possible usage:
	@is_superuser
	def view....
	
	urlpatterns = patterns('',
		(r'^databrowse/(.*)', is_staff(databrowse.site.root)),
	)
	"""
	actual_decorator = user_passes_test(
		lambda u: u.is_superuser,
		 login_url=login_url,
		redirect_field_name=redirect_field_name
	)
	if function:
		return actual_decorator(function)
	return actual_decorator	