
from django.test import TestCase

from auth0db.compatibility import get_user_model
from auth0db.forms import SetPasswordForm


class TestSetPasswordForm(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User(id=1, username='thom', email='thom.yorke@radiohead.com', is_active=True)
        pw = 'KidA2001'
        user.set_password(pw)
        self.user = user
        pwf = SetPasswordForm(user)
        pwf.cleaned_data = {'new_password1': pw, 'new_password2': pw}
        self.pwf = pwf

    def test_save_with_no_auth0_user(self):
        """
        Raises and catches AttributeError because user.auth0user does not exist yet
        """
        user = self.pwf.save(commit=False)
        self.assertEqual(user, self.user)





