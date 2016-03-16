# -*- coding: utf-8 -*-
from django.conf import settings
from django.test.utils import setup_test_environment


def pytest_configure():
    settings.configure(
        DATABASES={'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': ':memory:'},
        },
        DEBUG=False,
        SECRET_KEY=123,
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'auth0d'],
       LANGUAGE_CODE='en-us',
       TIME_ZONE='UTC',
       USE_I18N=True,
       USE_L10N=True,
       USE_TZ=True,
       AUTH0_DOMAIN="https://YOURAPP.XX.auth0.com",
       AUTH0_CLIENT_ID="123",
       AUTH0_JWT='123',
       AUTH0_CONNECTION="Username-Password-Authentication",
    )
    setup_test_environment()
