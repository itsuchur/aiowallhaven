from __future__ import annotations

from typing import Dict

import aiohttp
from aiolimiter import AsyncLimiter

from aiowallhaven import api_exception_reasons as exception_reasons
from aiowallhaven.wallhaven_types import (
    Purity, Category, Color, Order, Sorting, TopRange, Resolution, Ratio)


VERSION = "v1"
BASE_API_URL = "https://wallhaven.cc/api"


class WallHavenAPI(object):
    r"""
        Base API Class.
        :api_key: 
            an API Key provided by Wallhaven. 
            If you don't have one get yours at https://wallhaven.cc/settings/account.
    """

    __slots__ = ("api_key", "_session", "_rate_limit")

    def __init__(self, api_key: str):
        self.api_key: str = api_key
        self._session: aiohttp.ClientSession | None = None
        self._rate_limit = AsyncLimiter(12, 60)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        """Close the connection pool. Use the client on a single event loop."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def _get_method(self, url: str, params: Dict = None) -> Dict:
        r"""
            Make an async GET request to https://wallhaven.cc

            :param url: API endpoint relative to the versioned base URL.
            :param params: Additional parameters for get method
            :return: :class: `JSON` object
        """

        if params is None:
            params = {}

        headers = {
            "X-API-key": f"{self.api_key}",
        }

        async with self._rate_limit:
            if self._session is None or self._session.closed:
                self._session = aiohttp.ClientSession()
            req_url = f"{BASE_API_URL}/{VERSION}/{url}"
            async with self._session.get(req_url, headers=headers, params=params) as response:
                response.raise_for_status()
                return await response.json()

    @staticmethod
    async def _purity(pur: Purity) -> str:
        return "{}{}{}".format(int(pur.sfw), int(pur.sketchy), int(pur.nsfw))

    @staticmethod
    async def _category(cat: Category):
        return "{}{}{}".format(int(cat.general), int(cat.anime), int(cat.people))

    async def get_wallpaper(self, wallpaper_id: str):
        r"""
            Get the details about wallpaper with given id.
        
            :param wallpaper_id:
                A string representing a unique id assigned to the wallpaper.

            :return:
                :class: `JSON` object
        """

        url = f"w/{wallpaper_id}"
        return await self._get_method(url)

    async def search(self,
                     q: str = None,
                     category: Category = None,
                     purity: Purity = None,
                     sorting: Sorting = None,
                     order: Order = None,
                     toprange: TopRange = None,
                     atleast: Resolution = None,
                     resolutions: list[Resolution] = None,
                     ratios: list[Ratio] = None,
                     color: Color = None,
                     page: int = None,
                     seed: str = None):
        r"""
            Perform search through Wallhaven.
            If no additional parameters are set
            the latest SFW wallpapers will be returned.

            :param q:
                Search query. Your main way of finding what you're looking for.
            :param category:
                Only wallpapers with specified categories will be returned.
            :param purity:
                Only wallpapers with specified purities will be returned.
            :param sorting:
                *(optional)* Method of sorting results.
            :param order:
                *(optional)* Sorting order. Default order is desc.
            :param toprange:
                *(optional)* Specify toplist sorting options.
                Sorting MUST be set to 'toplist'.
            :param atleast:
                *(optional)* Minimum resolution allowed. (e.g. "1920x1080")
            :param resolutions:
                *(optional)* List of exact wallpaper resolutions.
            :param ratios:
                *(optional)* List of exact ratios.
            :param color:
                *(optional)* Search by color.
            :param page:
                *(optional)* Pagination. Not actually infinite.
            :param seed:
                *(optional)* seed for random results. Example: ``[a-zA-Z0-9]{6}``.

            :return: :class: `JSON` object
        """

        query_params: dict = {}

        if q:
            query_params["q"] = q

        if category:
            query_params["categories"] = await self._category(category)

        if purity:
            query_params["purity"] = await self._purity(purity)

        if sorting:
            if not isinstance(sorting, Sorting):
                raise ValueError(exception_reasons.ValueErrorSorting)
            query_params["sorting"] = sorting.value

        if order:
            if not isinstance(order, Order):
                raise ValueError(exception_reasons.ValueErrorOrder)
            query_params["order"] = order.value

        if toprange:
            if not isinstance(toprange, TopRange):
                raise ValueError(exception_reasons.ValueErrorToprange)
            query_params["toprange"] = toprange.value

        if atleast:
            if not isinstance(atleast, Resolution):
                raise ValueError(exception_reasons.ValueErrorAtleast)
            query_params["atleast"] = str(atleast)

        if resolutions:
            if not isinstance(resolutions, list):
                raise ValueError(exception_reasons.ValueErrorResolutionsFormat)

            for res in resolutions:
                if not isinstance(res, Resolution):
                    raise ValueError(exception_reasons.ValueErrorResolutions)

            query_params["resolutions"] = ",".join(str(x) for x in resolutions)

        if ratios:
            if not isinstance(ratios, list):
                raise ValueError(exception_reasons.ValueErrorRatiosFormat)

            for rat in ratios:
                if not isinstance(rat, Ratio):
                    raise ValueError(exception_reasons.ValueErrorRatios)

            query_params["ratios"] = ",".join(str(x) for x in ratios)

        if color:
            query_params["colors"] = color.value

        if page:
            query_params["page"] = str(page)

        if seed:
            query_params["seed"] = seed

        return await self._get_method("search", params=query_params)

    async def get_tag(self, tag: int):    
        r"""
            Return the information about a specific tag.

            :param tag: an integer associated with a tag.

            :return: :class: `JSON` object
        """
        return await self._get_method(f"tag/{tag}")

    async def my_settings(self):
        r"""
            Return the user's settings. *API key is required for this method.*

            :return: :class: `JSON` object
        """
        return await self._get_method(f"settings")

    async def get_collections(self, username: str = None,
                              collection_id: int = None,
                              purity: Purity = None,
                              page: int = 1):
        r"""
            Allows a user to see their own or public collection.

            :param username:
                *(optional)* Specifies a username of user, whose collections you
                are looking for.
            :param collection_id:
                *(optional)* Argument to parse through user collection having
                the indicated ID.
            :param purity:
                *(optional)* Argument to choose purity of returned results
                (e.g. ["sfw", "sketchy", "nsfw"]).
            :param page:
                Page of the collection you are looking for.

            :return: :class: `JSON` object
        """

        query_url = "collections"

        if username:
            query_url += '/' + username

        if collection_id:
            query_url += '/' + str(collection_id)

        params = {"page": page}
        if purity:
            params["purity"] = await self._purity(purity)

        return await self._get_method(query_url, params=params)

    async def get_user_uploads(self,
                               username: str,
                               purity: Purity = None,
                               page=1):
        r"""
            Allows a user to get somebody's uploads.
            This function is an alias for search.

            :param username:
                Specifies a user which uploads you are looking for.
            :param purity:
                *(optional)* List with elements representing purity.
                Only wallpapers with purities in the list will be returned.
                (e.g. ``['sfw', 'sketchy']`` - only sfw or sketchy)
            :param page:
                *(optional)* Page of the user's uploads. First page by default.

            :return: :class: `JSON` object
        """

        if purity is None:
            purity = Purity(sfw=True, sketchy=True, nsfw=False)
        res = await self.search(q=f"@{username}", page=page, purity=purity)
        return res
