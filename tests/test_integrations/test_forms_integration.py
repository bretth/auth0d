import unittest

from django.conf import settings
from django.test import TestCase
from mock import patch

from auth0db.compatibility import get_user_model
from auth0db.forms import SetPasswordForm
from auth0db.models import Auth0User


class TestSetPasswordFormIntegration(TestCase):
    @unittest.skipIf(settings.SKIP_INTEGRATION_TESTS, settings.REASON)
    def setUp(self):
        # Setup local user
        User = get_user_model()
        user = User(username='thom', email='thom.yorke@radiohead.com', is_active=True)
        pw = 'KidA2001'
        new_pw = 'TheKingOfLimbs2011'
        user.set_password(pw)
        user.save()
        self.user = user

        # setup form with new password
        pwf = SetPasswordForm(user)
        pwf.cleaned_data = {'new_password1': new_pw, 'new_password2': new_pw}
        self.pwf = pwf
        
        # setup Auth0 user
        self.a0u, created = self.pwf.auth0.users.get_or_create(
            defaults={
                'email_verified': True, 'password': pw,
                'app_metadata': {'username': user.username}},
            email=user.email)
        if not created:
            self.a0u.password = pw
            self.a0u.save()

        # setup Auth0 local
        self.local_a0u = Auth0User.objects.create(auth0_id=self.a0u.user_id, user=self.user)

        # patch out raven integration
        self.patch1 = patch('auth0db.forms.client')
        self.mock_client = self.patch1.start()

    def tearDown(self):
        self.a0u.delete()
        self.patch1.stop()

    def test_save_with_auth0_user(self):
        """
        Test with an actual auth0 user to change the password against
        """

        self.pwf.save()
        self.assertTrue(hasattr(self.pwf, 'auth0_id'))
        self.assertFalse(self.mock_client.user_context.called)



