# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User


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
