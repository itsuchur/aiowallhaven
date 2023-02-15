.. _api:

.. module:: aiowallhaven

The Base Class, Functions and Exceptions
========================================

Below you can find an information about the base class.

.. class:: aiowallhaven.api.WallHavenAPI(api_key)

API key is a key given to you by https://wallhaven.cc.

HTTP Method "GET"
-----------------

.. autofunction:: aiowallhaven.api.WallHavenAPI._get_method

Functions
---------

.. autofunction:: aiowallhaven.api.WallHavenAPI.get_wallpaper

.. autofunction:: aiowallhaven.api.WallHavenAPI.search

.. autofunction:: aiowallhaven.api.WallHavenAPI.get_tag

.. autofunction:: aiowallhaven.api.WallHavenAPI.my_settings

.. autofunction:: aiowallhaven.api.WallHavenAPI.get_collections

Exceptions
----------

.. autoexception:: aiowallhaven.api_exception_reasons.TooManyRequests

.. autoexception:: aiowallhaven.api_exception_reasons.Unauthorized

.. autoexception:: aiowallhaven.api_exception_reasons.GeneralError

.. autoexception:: aiowallhaven.api_exception_reasons.ValueErrorPurity

.. autoexception:: aiowallhaven.api_exception_reasons.ValueErrorCategory

.. autoexception:: aiowallhaven.api_exception_reasons.ValueErrorSorting

.. autoexception:: aiowallhaven.api_exception_reasons.ValueErrorOrder

.. autoexception:: aiowallhaven.api_exception_reasons.ValueErrorToprange

.. autoexception:: aiowallhaven.api_exception_reasons.ValueErrorAtleast
