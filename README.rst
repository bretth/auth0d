===============================
auth0db
===============================

.. image:: https://img.shields.io/pypi/v/auth0db.svg
        :target: https://pypi.python.org/pypi/auth0db

.. image:: https://img.shields.io/travis/bretth/auth0db.svg
        :target: https://travis-ci.org/bretth/auth0db


Migrate Django users to Auth0

* Free software: ISC license

Warning
--------

This is alpha quality software. It was written to migrate users from a Django 1.4 project onto Auth0 but it is unlik

Introduction
------------

Auth0 is a login as a service provider which at it's simplest will offload the login process from your django based website and provide additional protections and external database backed authentication for your django project.

The primary goals of this project are:

* provide a simple user friendly method for migrating existing django users to Auth0 database authentication for legacy and recent django projects (I am working with Django 1.4)
* handle username or email as username django user models
* migrate a django username login to an email backed Auth0 login

A non-goal is to handle existing or proposed social authentication in User migration or to provide signup workflows. It you are not migrating users then the backend in this project defeats the benefits of Auth0's ratelimiting and DDOS mitigation.

User Migration Process
----------------------

Auth0 already provides a progressive migration path from your existing project as long as your django passwords are upgraded to bcrypt. If you want to go that route Auth0 `document that method <https://auth0.com/docs/connections/database/migrating>`_, but that route might require subscription to a premium plan and will still require progressive upgrading of all local passwords to use bcrypt first which defeats the potential benefits of this approach.

The path this project takes will be to retain your existing login method, views and templates but with the additional auth0db MigrateToAuth0Backend backend inserted ahead of your current backend which will allow you to use their free or other plans as appropriate. 

The migration process is as follows:

* User authenticates against the MigrateToAuth0Backend backend. If that fails the user is authenticated against your existing backend and a new Auth0 user created if they are authenticated on your current backend.
* If the user authenticates against Auth0 they will be created in django if they don't exist locally.
* A local Auth0User model holds the Auth0 user_id and has a one to one relationship with the new or existing User to allow tracking of migration.
* If a current django user needs to reset their password (usually via email) then a replacement SetPassword form can be passed into the standard django auth password_reset_confirm view that simply sets a new password on the Auth0 user if they exist *and* the local User.
* An auth0_migrated management command will show what percentage have been migrated

The end game in your migration will be switching over to your own new templates which use the Auth0 lock login widgets and sending password reset emails to any remaining active but in-frequent django based users you might have that don't have a corresponding Auth0User record.

To avoid any potential disruption for your users any methods that create or update a password on Auth0 should also update the local user model until the switchover is complete at which point you can safely remove the MigrateToAuth0Backend.

The other caveat is that in the event that multiple django usernames share a single email address, the first successful authenticated username will be migrated but the following ones never will, so you will need a plan to deal with these.

Getting started
---------------

Install auth0db::

    $ pip install auth0db 

Add *auth0db* to your *INSTALLED_APPS* django setting, and *auth0db.backends.MigrateToAuth0Backend* as your first authentication backend::

    AUTHENTICATION_BACKENDS = [
    'auth0db.backends.MigrateToAuth0Backend',
    'django.contrib.auth.backends.ModelBackend'
    ] 

You can use alternative backends to the ModelBackend as the backend you are migrating from so long as they support either email or username as their username, return a user instance with an email and take a password as an argument.

The newer Auth0 management api requires a JSON web token (jwt) which allows you to limit the scope of the api that your django project can access. To get that: 

- Login to auth0.com
- Go to their management api documentation (https://auth0.com/docs/api/v2)
- Add scopes for Create, Read, Update on the Users endpoint.
- Copy the generated `jwt` token for your AUTH0_USER_JWT setting.

While in Auth0 you will need the database 'connection' name that will store your users, the usual api keys, and the app domain.

In your django settings file you'll need the following settings::

    # Mandatory settings
    AUTH0_DOMAIN = "YOURAPP.XX.auth0.com"  #
    AUTH0_CLIENT_ID = "Your_Auth0_Client_ID"
    AUTH0_USER_JWT = 'jwt with CRU permissions on Users'
    AUTH0_CONNECTION = "Username-Password-Authentication"  # or whatever yours is called

    # Optional
    AUTH_USER_MODEL = "auth.User"  # default 
    AUTH0_REQUIRE_USERNAME = False  # default - to match the CONNECTION setting

    # Not required for Django >= 1.5, optional for Django pre 1.5
    # If your legacy User model has a different username field...   
    USERNAME_FIELD = "username"  # default

Since we need to dynamically set a foreign key to the User model you'll need to create a package folder in your project and use the appropriate migration setting to point to it for the database migration. I suggest putting it with your other local apps and giving it a name that can't clash when South/Django is locating all the migration folders. In this case our project folder is *djangoproject* so we'll create 'djangoproject.auth0db_migrations' with *__init__.py* in it.
::

    # Django pre 1.7 with South installed
    SOUTH_MIGRATION_MODULES = {
        'auth0db': 'djangoproject.auth0db_migrations',
    }

    # Django >= 1.7
    MIGRATION_MODULES = {
        'auth0db': 'djangoproject.auth0db_migrations',
    }

Now create initial migration of the auth0db and migrate it:

    # Django pre 1.7 with South installed
    ./manage.py schemamigration --initial auth0db

    # Django >= 1.7
    ./manage.py makemigration auth0db

Your migrations folder should now have the initial migration in it.
::
    # Migrate the app!
    ./manage.py migrate auth0db


Once migrated, the Auth0User model holds the user id and their corresponding auth0_id that can be used to track the migration.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
