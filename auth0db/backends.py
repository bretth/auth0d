# -*- coding: utf-8 -*-
import json

from auth0plus.management.auth0p import Auth0
from auth0plus.exceptions import Auth0Error, MultipleObjectsReturned
from auth0.v2.authentication import Database, Users


import django.dispatch
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_backends
from django.core.exceptions import PermissionDenied
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from .compatibility import get_user_model

from .exceptions import UnhandledUserNameField
from .models import Auth0User

auth0_user_created = django.dispatch.Signal(providing_args=["auth0_user"])
auth0_users_create_failed = django.dispatch.Signal(
    providing_args=["error", "connection", "email", "password"])


class MigrateToAuth0Backend(ModelBackend):
    """
    This Auth0 backend must be the first authentication backend in settings.

    It authenticates the user against Auth0. If that fails it authenticates against
    the other backends in turn. After a successful authentication it creates an Auth0 email user.
    """
    
    def __init__(self):
        self.auth0 = Auth0(
            settings.AUTH0_DOMAIN,
            settings.AUTH0_USER_JWT,
            client_id=settings.AUTH0_CLIENT_ID,
            default_connection=settings.AUTH0_CONNECTION)
        self.db = Database(settings.AUTH0_DOMAIN)
        self.users = Users(settings.AUTH0_DOMAIN)

    def _authenticate(self, email, password, username=None):
        access_token = self.db.login(
            settings.AUTH0_CLIENT_ID,
            username or email, password,
            settings.AUTH0_CONNECTION).get('access_token', None)

        if access_token:  # authenticated in Auth0
            return json.loads(self.users.userinfo(access_token))

    def _create_auth0_user(self, user, raw_password, email_verified=True, commit=True):
        kwargs = {'password': raw_password, 'email_verified': email_verified}
        # handle username
        req_username = getattr(settings, 'AUTH0_REQUIRE_USERNAME', False)
        if user.USERNAME_FIELD == 'username' and req_username:
            kwargs['username'] = user.username
        if getattr(user, 'username', None) and not req_username:  # store legacy username
            kwargs['app_metadata'] = {"username": user.username}
        
        # handle names
        # https://ask.auth0.com/t/where-to-store-first-and-last-name-using-db-and-active-directory/2128
        kwargs['user_metadata'] = {
            'given_name': getattr(user, 'first_name', None),
            'family_name': getattr(user, 'last_name', None)}
    
        try:
            a0_user, created = self.auth0.users.get_or_create(defaults=kwargs, email=user.email)
            # user has authenticated locally but not on Auth0, but they may already exist on Auth0
            if not created:
                a0_user.password = raw_password
                a0_user.save()
            a0_local, created = Auth0User.objects.get_or_create(
                auth0_id=a0_user.user_id, defaults={'user': user})
            if a0_local and not created:  # possibly we actually want an error raised here?
                if a0_local.user != user:
                    a0_local.user = user
                    if commit:
                        a0_local.save()
            if created:
                auth0_user_created.send(sender=self.__class__, auth0_user=a0_user)
            return a0_user
        except (Auth0Error, MultipleObjectsReturned) as err:
            auth0_users_create_failed.send(
                sender=self.__class__,
                error=err,
                connection=self.auth0,
                email=user.email
            )
            return None

    def authenticate(self, username=None, password=None, **kwargs):
        user = None
        UserModel = get_user_model()
        email = kwargs.get('email', '')
        # authenticate via Auth0
        userinfo = self._authenticate(email, password, username)
        if userinfo:
            user = _get_or_create_user(UserModel, userinfo)
        if user:
            return user
        # no user so try and authenticate through other backends
        for backend in get_backends()[1:]:
            if UserModel.USERNAME_FIELD == 'email':
                # django has a more arbitrary **credentials model
                # but we're only going to handle email and username backends
                user = backend.authenticate(email, password)
            else:
                user = backend.authenticate(username, password)
            if not user:
                continue
            elif user and user.email:  # create the user on Auth0.
                self._create_auth0_user(user, password)
            if user:
                return user
        # if we didn't authenticate raise an error to ensure django
        # doesn't also try and authenticate down the backends again
        raise PermissionDenied


def _get_or_create_user(UserModel, userinfo, defaults={'is_active': True}):
    """ Get or create the Django User
    
    :param User UserModel: The django project UserModel
    :param dict user_info: The Auth0 user_info profile
    :param dict defaults: get_or_create defaults
    :return: User
    """
    if not userinfo:
        return None
    email = userinfo['email']
    username = userinfo.get('username', userinfo.get('app_metadata', {}).get('username', ''))
    if UserModel.USERNAME_FIELD == 'username':
        defaults['email'] = email
        user, created = UserModel._default_manager.get_or_create(
            username=username, defaults=defaults)
    elif UserModel.USERNAME_FIELD == 'email':
        if username:
            defaults['username'] = username
        user, created = UserModel._default_manager.get_or_create(
            email=email, defaults=defaults)
    else:
        raise UnhandledUserNameField("USERNAME_FIELD can only be username or email")
    return user
