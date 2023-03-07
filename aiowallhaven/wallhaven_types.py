from enum import Enum
from dataclasses import dataclass, asdict

# Thanks for types to Goblenus
# https://github.com/Goblenus/WallhavenApi/blob/master/wallhavenapi.py
# I use dataclasses for categories and purity instead of enum for usability
# it's not exactly enumeration but logical object with options/data


@dataclass
class Resolution:
    """
        Object representing picture resolution as x and y (both must be positive).

        Can be represented in resolution format
        (e.g. 1920x1080)

        :raise InvalidResolution: either x or y are negative values
    """
    x: int
    y: int

    class InvalidResolution(Exception):
        pass

    def __post_init__(self):
        if self.x <= 0 or self.y <= 0:
            raise self.InvalidResolution("Both x and y must be positive.")

    def __repr__(self):
        return f"{self.x}x{self.y}"

    def __str__(self):
        return f"{self.x}x{self.y}"


@dataclass
class Ratio(Resolution):
    """
        Object representing picture ratio as x and y (both must be positive).

        Can be represented in ratio format
        (e.g. 16x9)

        :raise InvalidRatio: either x or y are negative values
    """
    class InvalidRatio(Exception):
        pass

    def __post_init__(self):
        if self.x <= 0 or self.y <= 0:
            raise self.InvalidRatio("Both x and y must be positive.")


@dataclass
class Purity:
    """
        Object representing purity filter (sfw, sketchy, nsfw)
    """
    sfw: bool = False
    sketchy: bool = False
    nsfw: bool = False

    def _get_active_names(self):
        """
        This function needed for testing purpose mainly

        :return: list of categories which are active (set as True)
        """
        fields = asdict(self)
        return [name for name, key in fields.items() if fields[name]]


@dataclass
class Category:
    """
        Object representing category filter (general, anime, people)
    """
    general: bool = False
    anime: bool = False
    people: bool = False

    def _get_active_names(self):
        """
        :return: list of categories which are active (set as True)
        """
        fields = asdict(self)
        return [name for name, key in fields.items() if fields[name]]


class Sorting(Enum):
    date_added = "date_added"
    relevance = "relevance"
    random = "random"
    views = "views"
    favorites = "favorites"
    toplist = "toplist"


class Order(Enum):
    # desc used by default
    desc = "desc"
    asc = "asc"


class TopRange(Enum):
    one_day = "1d"
    three_days = "3d"
    one_week = "1w"
    one_month = "1M"
    three_months = "3M"
    six_months = "6M"
    one_year = "1y"


class Color(Enum):
    # Color names from http://chir.ag/projects/name-that-color
    lonestar = "660000"
    red_berry = "990000"
    guardsman_red = "cc0000"
    persian_red = "cc3333"
    french_rose = "ea4c88"
    plum = "993399"
    royal_purple = "663399"
    sapphire = "333399"
    science_blue = "0066cc"
    pacific_blue = "0099cc"
    downy = "66cccc"
    atlantis = "77cc33"
    limeade = "669900"
    verdun_green = "336600"
    verdun_green_2 = "666600"
    olive = "999900"
    earls_green = "cccc33"
    yellow = "ffff00"
    sunglow = "ffcc33"
    orange_peel = "ff9900"
    blaze_orange = "ff6600"
    tuscany = "cc6633"
    potters_clay = "996633"
    nutmeg_wood_finish = "663300"
    black = "000000"
    dusty_gray = "999999"
    silver = "cccccc"
    white = "ffffff"
    gun_powder = "424153"
