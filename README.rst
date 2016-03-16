===============================
auth0d
===============================

.. image:: https://img.shields.io/pypi/v/auth0d.svg
        :target: https://pypi.python.org/pypi/django-auth0

.. image:: https://img.shields.io/travis/bretth/auth0d.svg
        :target: https://travis-ci.org/bretth/django-auth0


Auth0 authentication for Django

* Free software: ISC license
* Documentation: https://django-auth0.readthedocs.org.

Warning
--------

This is an experimental library. I have very little spare time and a history of unmaintained repositories, but hey if it works for you then go for it!

Introduction
------------

Auth0 is a login as a service provider which at it's simplest will offload the login process from your django based website and provide additional protections and external database backed authentication for your django backed project.

The primary goals of this project are:

* provide a method for migrating existing django users to Auth0 database authentication for older and recent django projects
* handle both username or email username django user models
* migrate a django username login to an email backed Auth0 login
* provide a callback for logging an Auth0 authenticated user into Django

A secondary goal of this project is to provide an an abstract user model for greenfield projects that need to link to Auth0 but don't need to migrate existing users. In this instance you may wish to implement your own User model that wraps the companion `py-auth0 library <https://github.com/bretth/py-auth0>_`.

It's a non-goal to handle social authentication in User migration or to provide signup workflows. It you are not migrating users then using this backend defeats the benefits of Auth0's ratelimiting and DDOS mitigation, so you may want to implement your own login callback modelled on the login_callback in this package's views.py instead.

User Migration
--------------

Auth0 already provides a progressive migration path from your existing project as long as your django passwords are upgraded to bcrypt. If you want to go that route Auth0 `document that method <https://auth0.com/docs/connections/database/migrating>`_, but that route might require subscription to a premium plan and will still require progressive upgrading of all local passwords to use bcrypt first which defeats the simplicity of this approach.

The path this project takes will be to retain your existing login method, views and templates but with the additional auth0d MigrateToAuth0Backend backend inserted ahead of your current backend which will allow you to use their free or more cost effective plans as appropriate. 

The migration is as follows:

* User authenticates against the Auth0 backend. If that fails the user is authenticated against your existing backend and a new Auth0 user created if they are authenticated on your current backend.
* If the user authenticates against Auth0 they will be created in django if they don't exist locally.
* A local Auth0User model holds the Auth0 user_id and has a one to one relationship with the new or existing User.
* If a current django user needs to reset their password (usually via email) then a replacement SetPassword form can be passed into the standard django auth password_reset_confirm view that simply sets a new password on the Auth0 user if they exist *and* the local User.
* An auth0_migrated management command will show what percentage have been migrated

The end game in your migration will be switching over to your own new templates which use the Auth0 lock login widgets and sending password reset emails to any remaining active but in-frequent django based users you might have that don't have a corresponding Auth0User record.

To avoid any potential disruption for your users any methods that create or update a password on Auth0 should also update the local user model until the switchover is complete at which point you can safely remove the MigrateToAuth0Backend.

The other caveat is that in the event that multiple django usernames share a single email address, the first successful authenticated username will be migrated but the following ones never will, so you will need a plan to deal with these.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
