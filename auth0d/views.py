# -*- coding: utf-8 -*-
from auth0 import Authentication

from django.views.decorators.cache import never_cache
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.http import is_safe_url

from .utils import _get_update_or_create_user


def get_update_or_create_user(code, redirect_to=''):
    conn = Authentication.connect(
        settings.AUTH0_DOMAIN, settings.AUTH0_CLIENT_ID, settings.AUTH0_CLIENT_SECRET)
    access_token = conn.get_access_token(code, redirect_to)
    userinfo = conn.get_userinfo(access_token)
    return _get_update_or_create_user(userinfo)


def get_redirect_to(request):
    # the state parameter is set in the login template passed back to us by Auth0
    redirect_to = request.GET.get('state', '')
    # As per contrib.auth.views.login ensure the user-originating redirection url is safe.
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
    return redirect_to

    
@never_cache
def login_callback(request):
    user = get_update_or_create_user(request.GET.get('code'), get_redirect_to(request))
    # set the backend to the first backend path (the Auth0 backend)
    user.backend = settings.AUTHENTICATION_BACKENDS[0]
    # log the user in
    login(request, user)
    return HttpResponseRedirect(get_redirect_to(request))
