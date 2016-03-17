# -*- coding: utf-8 -*-
from auth0 import Authentication, Management, HTTPError

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
    
    def __init__(self, authentication=None, management=None):
        self.auth0 = authentication or Authentication.connect(
            settings.AUTH0_DOMAIN, settings.AUTH0_CLIENT_ID, settings.AUTH0_CONNECTION)
        self.api = management or Management.connect(settings.AUTH0_DOMAIN, settings.AUTH0_USER_JWT)

    def _authenticate(self, email, password, username=None):
        access_token = self.auth0.authenticate(username or email, password)
        if access_token:  # authenticated in Auth0
            return self.auth0.get_user_info(access_token)

    def _create_auth0_user(self, user, raw_password, email_verified=True, commit=True):
        kwargs = {'email': user.email, 'password': raw_password, 'email_verified': email_verified}
        lucene_q = 'email:"%s"' % user.email
        if user.username and user.username != user.email:
            kwargs['username'] = user.username
            lucene_q = 'username:"%s"' % user.username
        try:
            a0_user = self.api.users.get(q=lucene_q) or self.api.users.create(**kwargs)
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
        except HTTPError as e:  # implementing code can handle failure.
            # if email is not unique on default will raise a 400 error on Auth0
            # e.response.json()['message'] == "The user already exists."
            auth0_users_create_failed.send(
                sender=self.__class__,
                error=e,
                connection=self.api,
                email=user.email
            )
            return None

    def authenticate(self, username=None, password=None, **kwargs):
        user = None
        UserModel = get_user_model()
        email = kwargs.get('email', '')
        # authenticate via Auth0
        userinfo = self._authenticate(UserModel, email, password, username)
        if userinfo:
            user = _get_update_or_create_user(UserModel, userinfo)
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


def _get_update_or_create_user(UserModel, userinfo, defaults={'is_active': True}):
    """ Get or create the Django User
    :param User UserModel: The django project UserModel
    :param dict user_info: The Auth0 user_info profile
    :param dict defaults: get_or_create defaults
    :return: User
    """
    if not userinfo:
        return None
    email = userinfo['email']
    username = userinfo.get('username', None)

    if UserModel.USERNAME_FIELD == 'username':
        defaults['email'] = email
        user, created = UserModel._default_manager.get_or_create(
            username=username, defaults=defaults)
    elif UserModel.USERNAME_FIELD == 'email':
        user, created = UserModel._default_manager.get_or_create(
            email=email, defaults=defaults)
    else:
        raise UnhandledUserNameField("USERNAME_FIELD can only be username or email")
    if user and not created:
        if user.email != email:
            user.email = email
            user.save()
    return user
