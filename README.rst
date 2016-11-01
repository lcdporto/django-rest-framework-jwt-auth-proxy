=====
Django REST Framework JWT Authentication Proxy
=====

Reuse the same authentication server.


Disclaimer
-----------

This is a work in progress not yet suitable to use in production.
Presently only api-token-auth is implemented, refresh is next.

Quick Start
-----------


1. Add the app to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        '...',
    ]

2. Include the URLconf in your project urls.py like this::

    url(r'^.../', include('...urls')),
