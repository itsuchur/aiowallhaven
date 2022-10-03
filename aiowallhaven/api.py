from __future__ import annotations

import logging
import re
from http import HTTPStatus
from typing import Dict, Union

import aiohttp
import aiohttp.web
from aiolimiter import AsyncLimiter

import api_exception_reasons as exception_reasons

logging.basicConfig(format='%(message)s', level=logging.INFO)

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
    """Base API Class

    API documentation is available at https://wallhaven.cc/help/api

    Attributes:

        self.api_key = an API Key provided by Wallhaven. 
        If you don't have one get yours at https://wallhaven.cc/settings/account
    """

    def __init__(self, api_key):
        self.api_key: str = api_key

    async def _get_method(self, url) -> Dict:
        """Make an async GET request to https://wallhaven.cc

        Args:
            url = request url

        Raises:
            Exception: if exception happens =(

        Returns:
            JSON"""

        headers = {
            "X-API-key": f"{self.api_key}",
        }

        async with RATE_LIMIT:
            async with aiohttp.ClientSession() as session:
                req_url = f"{BASE_API_URL}/{VERSION}/{url}"
                async with session.get(req_url, headers=headers) as response:
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
                                reason=exception_reasons.GeneralError
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
        """Get the details about wallpaper with given id.
        Args:
            wallpaper_id - string representing a unique id assigned to the wallpaper
        Returns:
            JSON"""
        url = f"w/{wallpaper_id}"
        return await self._get_method(url)

    async def search(self,
                     q=None,
                     categories: list = None,
                     purity: list = None,
                     sorting: str = None,
                     order: str = None,
                     toprange: str = None,
                     atleast: str = None,
                     resolutions: Union[str, list] = None,
                     ratios: Union[str, list] = None,
                     colors: Union[str, int, list] = None,
                     page: str = None,
                     seed: str = None):
        """Perform search through Wallhaven.
        With no additional parameters the search will display the latest SFW wallpapers
        Args:
            q - Search query - Your main way of finding what you're looking for.
            categories - Turn categories on(1) or off(0).
            purity - Turn purities on(1) or off(0).
            sorting - Method of sorting results.
            order - Sorting order. Default order is desc.
            toprange - Sorting MUST be set to 'toplist'.
            atleast - Minimum resolution allowed.
            resolution - List of exact wallpaper resolutions. Single resolution is allowed.
            color - Search by color.
            page - Pagination. Not actually infinite
            seed - Optional seed for random results. Example: [a-zA-Z0-9]{6}.
        Returns:
            JSON"""

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
            if re.search("^([0-9].*)x([1-9].*)$", atleast):
                query_params["atleast"] = atleast
            else:
                raise ValueError(exception_reasons.ValueErrorAtleast)

        if resolutions:
            if isinstance(resolutions, str):
                query_params["resolutions"] = resolutions
            if isinstance(resolutions, list):
                for x in resolutions:
                    if re.search("^([0-9].*)x([1-9].*)$", x):
                        query_params["resolutions"] = "%2C".join(resolutions)
                    else:
                        raise ValueError(exception_reasons.ValueErrorResolutions)
            else:
                raise ValueError(exception_reasons.ValueErrorResolutionsFormat)

        if ratios:
            if isinstance(ratios, str):
                if re.search("^[0-9]{0,2}x[0-9]{0,2}$", ratios):
                    query_params["ratios"] = ratios
                else:
                    raise ValueError(exception_reasons.ValueErrorRatios)
            elif isinstance(ratios, list):
                for x in ratios:
                    if re.search("^[0-9]{0,2}x[0-9]{0,2}$", x):
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
        """Return the information about a tag.
        Args:
            tag - a tag to look for
        Returns:
            JSON"""
        return await self._get_method(f"tag/{tag}")

    async def my_settings(self):
        """Allows the user to read their settings.
        Args:
            No args
        Returns: JSON
        """
        return await self._get_method(f"settings")

    async def get_collections(self, username: str = None,
                              collection_id: int = None,
                              purity: list = None):
        """Allows the user to see their own or public collection.
        Args:
            username - an optional argument allowing the user to check other users' public collections.
            collection_id - an optional argument to parse through user collection having the indicated ID
            purity - an optional argument to choose purity of returned results (i.e. sfw, sketchy, nsfw)
        Returns:
            JSON"""

        query_url = "collections"

        if username:
            query_url += '/' + username

        if collection_id:
            query_url += '/' + str(collection_id)

        if purity:
            query_url += '?purity=' + await self._translate_purity_to_value(purity)

        return await self._get_method(query_url)

    async def get_user_uploads(self, username,
                               purity=None,
                               page=1):
        if not purity:
            purity = ['sfw', "sketchy", "nsfw"]
        res = await self.search(q=f"@{username}", page=str(page), purity=purity)
        return res
