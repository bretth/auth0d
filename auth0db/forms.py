from auth0plus.management import Auth0
from auth0plus.exceptions import Auth0Error
from django.contrib.auth.forms import SetPasswordForm as AuthSetPassForm
from django.conf import settings

from .compatibility import client


class SetPasswordForm(AuthSetPassForm):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    def __init__(self, user, *args, **kwargs):
        self.auth0 = kwargs.get(
            'auth0', Auth0(
                settings.AUTH0_DOMAIN,
                settings.AUTH0_USER_JWT,
                client_id=settings.AUTH0_CLIENT_ID,
                default_connection=settings.AUTH0_CONNECTION))
        super(SetPasswordForm, self).__init__(user, *args, **kwargs)

    def save(self, commit=True):
        try:  # set the pass on auth0 if they exist as well as locally
            self.auth0_id = self.user.auth0user.auth0_id
        except AttributeError:  # user hasn't been created on Auth0 yet
            return super(SetPasswordForm, self).save(commit)
        try:
            a0user = self.auth0.users.get(id=self.auth0_id)
            a0user.password = self.cleaned_data["new_password1"]
            if commit:
                a0user.save()
        except Auth0Error:
            # This is not critical. In the event the user trys to login the legacy backend
            # should succeed and then try and update the password again
            client.user_context({'email': self.user.email})
            client.extra_context({'auth0_user_id': self.auth0_id})
            client.captureException('Warning: Could not set new password on auth0')

        # we want the super form to save to the conventional backend
        return super(SetPasswordForm, self).save(commit)
