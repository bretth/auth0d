import os
from dotenv import load_dotenv
load_dotenv('.env')

# this setting is just for test running
SKIP_INTEGRATION_TESTS = int(os.getenv('SKIP_INTEGRATION_TESTS', 1))
REASON = 'SKIP_INTEGRATION_TESTS==1'

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'}}

SECRET_KEY = 123
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    'auth0db']

# LANGUAGE_CODE='en-us'
# TIME_ZONE='UTC'
# USE_I18N=True
# USE_L10N=True
# USE_TZ=True
AUTHENTICATION_BACKENDS = [
    'auth0db.backends.MigrateToAuth0Backend',
    'django.contrib.auth.backends.ModelBackend']

AUTH0_DOMAIN = os.getenv('DOMAIN')
AUTH0_CLIENT_ID = os.getenv('CLIENT_ID')
AUTH0_USER_JWT = os.getenv('JWT')
AUTH0_CONNECTION = os.getenv('CONNECTION')
