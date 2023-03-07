from __future__ import annotations

import logging

from http import HTTPStatus
from typing import Dict

import aiohttp
import aiohttp.web
from aiolimiter import AsyncLimiter

from aiowallhaven import api_exception_reasons as exception_reasons
from aiowallhaven.wallhaven_types import (
    Purity, Category, Color, Order, Sorting, TopRange, Resolution, Ratio)


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

LOG = logging.getLogger(__name__)
VERSION = "v1"
BASE_API_URL = "https://wallhaven.cc/api"
RATE_LIMIT = AsyncLimiter(12, 60)  # self tested new API limits


class WallHavenAPI(object):
    __slots__ = "api_key"
    r"""
        Base API Class.
        :api_key: 
            an API Key provided by Wallhaven. 
            If you don't have one get yours at https://wallhaven.cc/settings/account.
    """

    def __init__(self, api_key: str):
        self.api_key: str = api_key

    async def _get_method(self, url: str, params: Dict = None) -> Dict:
        r"""
            Make an async GET request to https://wallhaven.cc

            :param url: URL for the new :class:`aiohttp.ClientSession` object.
            :param params: Additional parameters for get method
            :return: :class: `JSON` object
        """

        if params is None:
            params = {}

        headers = {
            "X-API-key": f"{self.api_key}",
        }

        async with RATE_LIMIT:
            async with aiohttp.ClientSession() as session:
                req_url = f"{BASE_API_URL}/{VERSION}/{url}"
                async with session.get(req_url, headers=headers, params=params) as response:
                    status_code = response.status
                    match status_code:
                        case HTTPStatus.OK:
                            return await response.json()

                        case HTTPStatus.UNAUTHORIZED:
                            raise aiohttp.web.HTTPUnauthorized(
                                reason=exception_reasons.Unauthorized
                            )

                        case HTTPStatus.TOO_MANY_REQUESTS:
                            raise aiohttp.web.HTTPTooManyRequests(
                                reason=exception_reasons.TooManyRequests
                            )

                        case _:  # general error
                            raise aiohttp.web.HTTPException(
                                reason=exception_reasons.GeneralError.format(
                                    session=session, status_code=status_code)
                            )

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
                raise ValueError(exception_reasons.ValueErrorResolutions)
            query_params["atleast"] = str(atleast)

        if resolutions:
            if not isinstance(resolutions, list):
                raise ValueError(exception_reasons.ValueErrorResolutionsFormat)

            for res in resolutions:
                if not isinstance(res, Resolution):
                    raise ValueError(exception_reasons.ValueErrorResolutions)

            query_params["resolutions"] = "%2C".join(str(x) for x in resolutions)

        if ratios:
            if not isinstance(ratios, list):
                raise ValueError(exception_reasons.ValueErrorRatiosFormat)

            for rat in ratios:
                if not isinstance(rat, Ratio):
                    raise ValueError(exception_reasons.ValueErrorRatios)

            query_params["ratios"] = "%2C".join(str(x) for x in ratios)

        if color:
            query_params["colors"] = color.value

        if page:
            query_params["page"] = str(page)

        if seed:
            query_params["seed"] = seed

        return await self._get_method(
            f"search" if not query_params else
            f"search?{'&'.join('{}={}'.format(*i) for i in query_params.items())}")

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

        if purity:
            query_url += '?purity=' + await self._purity(purity)

        return await self._get_method(query_url, params={"page": page})

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
