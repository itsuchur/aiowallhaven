from __future__ import annotations

import logging
import re
from http import HTTPStatus
from typing import Dict, Union

import aiohttp
import aiohttp.web
from aiolimiter import AsyncLimiter

from aiowallhaven import api_exception_reasons as exception_reasons

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

LOG = logging.getLogger(__name__)
VERSION = "v1"
BASE_API_URL = "https://wallhaven.cc/api"
RATE_LIMIT = AsyncLimiter(12, 60)  # self tested new API limits
TOPRANGE = ("1d", "3d", "1w", "1M", "3M", "6M", "1y")
SORTING = ("date_added", "relevance", "random", "views", "favorites", "toplist")
COLORS = (
    "660000", "990000", "cc0000", "cc3333", "ea4c88", "993399", "663399",
    "333399", "0066cc", "0099cc", "66cccc", "77cc33", "669900", "336600",
    "666600", "999900", "cccc33", "ffff00", "ffcc33", "ff9900", "ff6600",
    "cc6633", "996633", "663300", "000000", "999999", "cccccc", "ffffff",
    "424153"
)


class WallHavenAPI(object):
    __slots__ = "api_key"
    r"""
        Base API Class.
        :api_key: 
            an API Key provided by Wallhaven. 
            If you don't have one get yours at https://wallhaven.cc/settings/account.
    """

    def __init__(self, api_key):
        self.api_key: str = api_key

    async def _get_method(self, url, params=None) -> Dict:
        r"""
            Make an async GET request to https://wallhaven.cc

            :param url: URL for the new :class:`aiohttp.ClientSession` object.
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
    async def _translate_purity_to_value(purity: list) -> str:
        value = 0b000
        for pur in purity:
            match pur:
                case "sfw":
                    value |= 0b100
                case "sketchy":
                    value |= 0b010
                case 'nsfw':
                    value |= 0b001
                case _:
                    raise ValueError(exception_reasons.ValueErrorPurity)
        result = "{0:03b}".format(value)
        return result

    @staticmethod
    async def _translate_categories_to_value(categories: list):
        value = 0b000
        for category in categories:
            match category:
                case "general":
                    value |= 0b100
                case "anime":
                    value |= 0b010
                case 'people':
                    value |= 0b001
                case _:
                    raise ValueError(exception_reasons.ValueErrorCategory)
        result = "{0:03b}".format(value)
        return result

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
                     categories: list[str] = None,
                     purity: list[str] = None,
                     sorting: str = None,
                     order: str = None,
                     toprange: str = None,
                     atleast: str = None,
                     resolutions: Union[str, list] = None,
                     ratios: Union[str, list] = None,
                     colors: Union[str, int, list] = None,
                     page: str = None,
                     seed: str = None):
        r"""
            Perform search through Wallhaven.
            If no additional parameters are set
            the latest SFW wallpapers will be returned.

            :param q:
                Search query. Your main way of finding what you're looking for.
            :param categories:
                *(optional)* List with elements representing categories.
                Only wallpapers with categories in the list will be returned.
                (e.g. ``['anime', 'general']`` - only anime or general. )
            :param purity:
                *(optional)* List with elements representing purity.
                Only wallpapers with purities in the list will be returned.
                (e.g. ``['sfw', 'sketchy']`` - only sfw or sketchy. )
            :param sorting:
                *(optional)* Method of sorting results.
                Possible sorting values:
                ``"date_added", "relevance", "random",
                "views", "favorites", "toplist"``
            :param order:
                *(optional)* Sorting order. Default order is desc.
                Possible order values:
                ``"desc", "asc"``
            :param toprange:
                *(optional)* Specify toplist sorting options.
                Sorting MUST be set to 'toplist'.
                Possible toprange values:
                ``"1d", "3d", "1w", "1M", "3M", "6M", "1y"``
            :param atleast:
                *(optional)* Minimum resolution allowed. (e.g. "1920x1080")
            :param resolutions:
                *(optional)* List of exact wallpaper resolutions.
                Single resolution is allowed.
                e.g. ``["800x600", "1920x1080"]``
            :param ratios:
                *(optional)* List of exact ratios.
                e.g. ``["1x1", "16x9"]``
            :param colors:
                *(optional)* Search by color.
                e.g. ``"000000"`` - black color
            :param page:
                *(optional)* Pagination. Not actually infinite.
            :param seed:
                *(optional)* seed for random results. Example: ``[a-zA-Z0-9]{6}``.

            :return: :class: `JSON` object
        """

        query_params: dict = {}

        if q:
            query_params["q"] = q

        if categories:
            query_params["categories"] = await self._translate_categories_to_value(categories)

        if purity:
            query_params["purity"] = await self._translate_purity_to_value(purity)

        if sorting:
            if sorting in SORTING:
                query_params["sorting"] = sorting
            else:
                raise ValueError(exception_reasons.ValueErrorSorting)

        if order:
            match order:
                case "desc":
                    query_params["order"] = "desc"
                case "asc":
                    query_params["order"] = "asc"
                case _:
                    raise ValueError(exception_reasons.ValueErrorOrder)

        if toprange:
            if toprange in TOPRANGE:
                query_params["toprange"] = toprange
            else:
                raise ValueError(exception_reasons.ValueErrorToprange)

        if atleast:
            if re.search(r"^(\d.*)x([1-9].*)$", atleast):
                query_params["atleast"] = atleast
            else:
                raise ValueError(exception_reasons.ValueErrorAtleast)

        if resolutions:
            if isinstance(resolutions, str):
                query_params["resolutions"] = resolutions
            if isinstance(resolutions, list):
                for x in resolutions:
                    if re.search(r"^(\d.*)x([1-9].*)$", x):
                        query_params["resolutions"] = "%2C".join(resolutions)
                    else:
                        raise ValueError(exception_reasons.ValueErrorResolutions)
            else:
                raise ValueError(exception_reasons.ValueErrorResolutionsFormat)

        if ratios:
            if isinstance(ratios, str):
                if re.search(r"^\d{0,2}x\d{0,2}$", ratios):
                    query_params["ratios"] = ratios
                else:
                    raise ValueError(exception_reasons.ValueErrorRatios)
            elif isinstance(ratios, list):
                for x in ratios:
                    if re.search(r"^\d{0,2}x\d{0,2}$", x):
                        query_params["ratios"] = "%2C".join(ratios)
                    else:
                        raise ValueError(exception_reasons.ValueErrorRatios)
            else:
                raise ValueError(exception_reasons.ValueErrorRatiosFormat)

        if colors:
            query_params["colors"] = colors

        if page:
            query_params["page"] = page

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
                              purity: list = None,
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
            query_url += '?purity=' + await self._translate_purity_to_value(purity)

        return await self._get_method(query_url, params={"page": page})

    async def get_user_uploads(self, username, purity=None, page=1):
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

        if not purity:
            purity = ['sfw', "sketchy", "nsfw"]
        res = await self.search(q=f"@{username}", page=str(page), purity=purity)
        return res
