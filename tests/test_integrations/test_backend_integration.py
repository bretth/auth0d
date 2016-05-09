
# import time
import unittest
from mock import Mock

# import requests

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from auth0plus.management.auth0p import Auth0

from auth0db.backends import MigrateToAuth0Backend, _get_or_create_user
from auth0db.compatibility import get_user_model


class TestMigrateToAuth0Backend1(unittest.TestCase):
    @unittest.skipIf(settings.SKIP_INTEGRATION_TESTS, settings.REASON)
    def setUp(self):
        self.backend = MigrateToAuth0Backend()
        auth0 = Auth0(
            settings.AUTH0_DOMAIN,
            settings.AUTH0_USER_JWT,
            client_id=settings.AUTH0_CLIENT_ID,
            default_connection=settings.AUTH0_CONNECTION)
        user, created = auth0.users.get_or_create(
            defaults={'email_verified': True, 'password': 'HailToTheThief'},
            email='thom.yorke@radiohead.com')

    def test__authenticate(self):
        """
        User exists on Auth0. Authenticate.
        """
        user_info = self.backend._authenticate('thom.yorke@radiohead.com', 'HailToTheThief')
        self.assertEqual(user_info['email'], 'thom.yorke@radiohead.com')


class TestMigrateToAuth0Backend2(TestCase):

    @unittest.skipIf(settings.SKIP_INTEGRATION_TESTS, settings.REASON)
    def setUp(self):
        self.UserModel = get_user_model()

    def test__get_or_create_user(self):
        """
        User exists on Auth0 and has been authenticated and may or may not exist locally.
        Create or get them from the local db.
        """
        user_info = {'email': 'thom.yorke@radiohead.com'}
        user = _get_or_create_user(self.UserModel, user_info)
        self.assertEqual(user.email, user_info['email'])
        

class TestMigrateToAuth0Backend3(TestCase):
    @unittest.skipIf(settings.SKIP_INTEGRATION_TESTS, settings.REASON)
    def setUp(self):
        self.backend = MigrateToAuth0Backend()
        UserModel = get_user_model()
        user2 = UserModel(
            email='jonny.greenwood@radiohead.com',
            first_name='Jonny',
            last_name='Greenwood',
            is_active=True)
        user2.set_password('PabloHoney')
        user2.save()
        self.user2 = user2

    def test__create_auth0_user(self):
        """
        User exists locally and is authenticated but didn't authenticate on Auth0
        so probably doesn't exist (or the password was different).
        """
        user = self.backend._create_auth0_user(self.user2, 'PabloHoney')
        self.assertEqual(user.email, 'jonny.greenwood@radiohead.com')


class TestMigrateToAuth0BackendAuth(TestCase):
    """
    Test MigrateToAuth0Backend.authenticate
    """

    def setUp(self):
        self.backend = MigrateToAuth0Backend()
        self.backend._authenticate = Mock(return_value=None)
        self.backend._create_auth0_user = Mock()
  
    def test_auth_no_user(self):
        """
        User doesn't exist anywhere
        """

        with self.assertRaises(PermissionDenied):
            self.backend.authenticate(
                email='colin.greenwood@radiohead.com',
                password='Amnesiac2001')


class TestMigrateToAuth0BackendAuth2(TestCase):
    """
    Test MigrateToAuth0Backend.authenticate
    """

    def setUp(self):
        self.backend = MigrateToAuth0Backend()
        self.backend._authenticate = Mock(return_value=None)
        self.backend._create_auth0_user = Mock()
        UserModel = get_user_model()
        user = UserModel(
            username='jonny',
            email='jonny.greenwood@radiohead.com',
            first_name='Jonny',
            last_name='Greenwood',
            is_active=True)
        user.set_password('PabloHoney')
        user.save()
        self.user = user

    def test_auth_no_auth0_user(self):
        """
        User exists locally and should authenticate locally and create a auth0 remote user
        """
        user = self.backend.authenticate(
            username='jonny',
            email='jonny.greenwood@radiohead.com',
            password='PabloHoney')
        self.assertEqual(self.backend._create_auth0_user.call_args[0], (self.user, 'PabloHoney'))
        self.assertEqual(user.email, 'jonny.greenwood@radiohead.com')




