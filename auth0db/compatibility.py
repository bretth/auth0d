# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User


try:
    from raven.contrib.django.raven_compat.models import client
except ImportError:
    class Client(object):
        def captureException(self):
            pass

        def extra_context(self):
            pass

        def user_context(self):
            pass

    client = Client()


try:
    from django.contrib.auth import get_user_model
except ImportError:
    def get_user_model():
        """
        Get django.contrib.auth.models.User for legacy django versions
        that don't have get_user_model. We add a USERNAME_FIELD
        """
        User.USERNAME_FIELD = getattr(settings, 'USERNAME_FIELD', 'username')

        return User


def password_validators_help_text_html():
    return ''


def validate_password(password2, user):
    pass
