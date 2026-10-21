Usage
=====

.. _installation:

Installation of aiowallhaven
----------------------------

To use aiowallhaven, first install it using pip:

.. code-block:: console

   $ pip install aiowallhaven

.. _getsource:

Get the Source Code
-------------------

aiowallhaven is developed on Github. You can access the repository at anytime by `clicking this link <https://github.com/itsuchur/aiowallhaven>`_.

Feel free to clone the repository running the following command:

.. code-block:: console

    $ git clone https://github.com/itsuchur/aiowallhaven.git

Once you have a copy of the source, you can embed it in your own Python package, or install it into your site-packages easily:

.. code-block:: console

    $ cd aiowallhaven
    $ python -m pip install .

Client lifecycle and errors
---------------------------

Use ``async with WallHavenAPI(api_key) as client`` to reuse connections and
close them when finished, or call ``await client.close()`` explicitly.
Keep each client on a single event loop. Rate limiting is per client.
HTTP failures raise ``aiohttp.ClientResponseError``; inspect its ``status``
and ``headers`` attributes to handle authentication errors or rate limits.
