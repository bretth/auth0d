from auth0 import Management, HTTPError

from django.contrib.auth.forms import SetPasswordForm as AuthSetPassForm
from django.conf import settings


class SetPasswordForm(AuthSetPassForm):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    def __init__(self, user, *args, **kwargs):
        self.auth0 = kwargs.get(
            'auth0', Management.connect(settings.AUTH0_DOMAIN, settings.AUTH0_JWT))
        super(SetPasswordForm, self).__init__(user, *args, **kwargs)

    def save(self, commit=True):
        try:  # set the pass on auth0 if they exist as well as locally 
            auth0_id = self.user.auth0user.auth0_id
            a0user = self.auth0.users.get(id=auth0_id)
            a0user.password = self.cleaned_data["new_password1"]
            if commit:
                a0user.save()
        except (AttributeError, HTTPError):
            # probably should handle this better in the event the user exists on Auth0 but
            # we get a different HTTP or Comms error 
            pass
        # we want the super form to save to the conventional backend
        return super(SetPasswordForm, self).save(commit)
