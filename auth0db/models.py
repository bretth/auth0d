# -*- coding: utf-8 -*
from django.conf import settings
from django.db import models
from django.utils import timezone


class Auth0User(models.Model):

    auth0_id = models.CharField(max_length=36, primary_key=True)
    user = models.OneToOneField(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        on_delete=models.SET_NULL,
        null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    

