# -*- coding: utf-8 -*-

"""
test_django-auth0
----------------------------------

Tests for `auth0d` module.
"""
import pytest
from django.conf import settings

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from auth0 import HTTPError

from auth0d.backends import _get_update_or_create_user, MigrateToAuth0Backend
from auth0d.compatibility import get_user_model
from auth0d.exceptions import UnhandledUserNameField
from auth0d.models import Auth0User


testsettings = [
    {'USERNAME_FIELD': 'email'},
    {'USERNAME_FIELD': None},
    {'USERNAME_FIELD': 'some_crazy_field'}
]


@pytest.fixture(params=testsettings)
def userinfo(request):
    # teardown previous
    if hasattr(settings, 'USERNAME_FIELD'):
        del settings.USERNAME_FIELD

    # setup
    username_field = request.param['USERNAME_FIELD']
    if username_field:
        settings.USERNAME_FIELD = username_field
    userinfo = {
        "connection": "Username-Password-Authentication",
        "email": "brett@example.com",
        "password": "pass",
        "email_verified": 'true',
        "user_id":  "auth0|56e00ca5bc1a37473fe4aa84"
        }
    if username_field == 'username':
        userinfo['username'] = 'brett'
    return userinfo


@pytest.fixture()
def UserModel(monkeypatch):
    User = get_user_model()

    def get_or_create(*args, **kwargs):
        defaults = kwargs.pop('defaults', {})
        defaults.update(kwargs)
        return User(id=1, **defaults), True

    User._default_manager.get_or_create = Mock(
        side_effect=get_or_create)
    return User


@pytest.fixture()
def backend(request, monkeypatch):
    ab = MigrateToAuth0Backend()

    def mock_auth0user(**kwargs):
        defaults = kwargs.pop('defaults', {})
        defaults.update(kwargs)
        return Auth0User(**defaults), True

    def mock_user(**kwargs):
        return ab.api.users(user_id='1', **kwargs)
    monkeypatch.setattr(ab.api.users, "create", mock_user)
    monkeypatch.setattr(ab.api.users, "get", lambda q: None)
    Auth0User.objects.get_or_create = Mock(side_effect=mock_auth0user)

    return ab


@pytest.fixture()
def failing_backend(request, monkeypatch):
    ab = MigrateToAuth0Backend()

    def mock_auth0user(**kwargs):
        defaults = kwargs.pop('defaults', {})
        defaults.update(kwargs)
        return Auth0User(**defaults), True

    def mock_user(**kwargs):
        raise HTTPError
    monkeypatch.setattr(ab.api.users, "create", mock_user)
    monkeypatch.setattr(ab.api.users, "get", lambda q: None)
    Auth0User.objects.get_or_create = Mock(side_effect=mock_auth0user)
    return ab


def test__get_update_or_create_user(userinfo, UserModel):

    try:
        user = _get_update_or_create_user(UserModel, userinfo)
        assert user.email == 'brett@example.com'
        username = userinfo.get('username', None)
        if username:
            assert user.username == username
        auth0_id_field = getattr(settings, 'AUTH0_ID_FIELD', None)
        if auth0_id_field:
            assert getattr(user, auth0_id_field) == userinfo['user_id']
    except UnhandledUserNameField:
        assert settings.USERNAME_FIELD not in ['email', 'username']


class TestMigrateToAuth0Backend(object):

    def test__create_auth_user(self, backend):
        User = get_user_model()
        user = User(id=1, email='brett@example.com')
        created = backend._create_auth0_user(user, '123', commit=False)
        assert created.email == 'brett@example.com'

        user = User(id=1, email='brett@example.com', username='brett')
        created = backend._create_auth0_user(user, '123', 'brett', commit=False)
        assert created.username == 'brett'

    def test__failing_create_auth_user(self, failing_backend):
        User = get_user_model()
        user = User(id=1, email='brett@example.com', username='brett')
        created = failing_backend._create_auth0_user(
            user, '123', commit=False)
        assert not created


