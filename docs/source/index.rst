.. aiowallhaven documentation master file, created by
   sphinx-quickstart on Tue Nov 29 20:06:57 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

aiowallhaven: a simple API
==========================

**aiowallhaven** is a Python library for synchronically interact with https://wallhaven.cc API.
It offers a *simple* and *intuitive* way to interact with the API.

-------------------

**An example**::

      import asyncio
      from aiowallhaven import WallHavenAPI

      wallhaven = WallHavenAPI("Your-API-key")

      async def wallpaper_details():
         request = await wallhaven.get_wallpaper("5758y8")
         print(request)

      loop = asyncio.get_event_loop()
      loop.run_until_complete(wallpaper_details())

aiowallhaven allows you to interact with wallhaven's API extremely easily. 
   

Check out the :doc:`usage` section for further information, including how to
:ref:`install <installation>` the library.

Check out the :doc:`api` section to learn more about the base class, functions and exceptions included with this library.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

The User Guide
--------------

.. toctree::

   usage
   api
