.. _api:

.. module:: aiowallhaven

The Base Class, Functions and .. autofunction:: aiowallhaven.api.WallHavenAPI.get_user_uploads

.. autofunction:: aiowallhaven.api.WallHavenAPI.close

Exceptions
----------

HTTP failures raise ``aiohttp.ClientResponseError``. Its ``status`` attribute
contains the HTTP response code (for example, 401, 404, or 429), and its
``headers`` attribute includes response headers such as ``Retry-After``.
Connection and timeout errors propagate from aiohttp. Invalid search filter
arguments raise ``ValueError``.
