import os                               # os.getenv()
import unittest
import warnings                         # disable some socket warnings

from datetime import datetime as dt     # for "sorting" test

from api import WallHavenAPI
from api import SORTING, TOPRANGE


API_KEY = os.getenv("WALLHAVEN_API_KEY")
if not(API_KEY):
    raise Exception("The wallhaven API key is required for this test.")

api = WallHavenAPI(API_KEY)

def get_wallpaper_datetime(date: str):
    return dt.strptime(date, "%Y-%m-%d %H:%M:%S")


class ApiTestSearch(unittest.IsolatedAsyncioTestCase):
    # Sometimes tests cause unclosed socket warnings
    # I couldn't beat this yet, maybe something happens in _get_method of the API
    # if you know the issue, please open pull request with possible decision
    def setUp(self):
        warnings.filterwarnings(
            action="ignore",
            message="unclosed",
            category=ResourceWarning)
        return super().setUp()


    async def test_query(self):
        target_query = "pool"
        response = await api.search(q = target_query)
        query = response["meta"]["query"]
        self.assertEqual(query, target_query)


    async def test_categories(self):
        all_categories = ["general", "anime", "people"]
        for category in all_categories:
            response = await api.search(categories=[category])
            wallpapers = response["data"]
            for wallpaper in wallpapers:
                self.assertEqual(wallpaper["category"], category)


    async def test_purity(self):
        all_purity = ["sfw", "sketchy", "nsfw"]
        for purity in all_purity:
            response = await api.search(purity=[purity])
            wallpapers = response["data"]
            for wallpaper in wallpapers:
                self.assertEqual(wallpaper["purity"], purity)


    async def test_sorting_date_added(self):
        target_sorting = "date_added"
        self.assertIn(target_sorting, SORTING)
        response = await api.search(sorting=target_sorting, order="desc")

        wallpapers = response["data"]
        previous_date = get_wallpaper_datetime(wallpapers[0]["created_at"])
        for wallpaper in wallpapers:
            current_wallpaper_date = get_wallpaper_datetime(wallpaper["created_at"])
            self.assertLessEqual(current_wallpaper_date, previous_date)
            previous_date = current_wallpaper_date


    async def test_sorting_views(self):
        target_sorting = "views"
        self.assertIn(target_sorting, SORTING)
        response = await api.search(sorting=target_sorting, order="desc")
        wallpapers = response["data"]

        previous_views = int(wallpapers[0][target_sorting])
        for wallpaper in wallpapers:
            current_views = int(wallpaper[target_sorting])
            self.assertLessEqual(current_views, previous_views)
            previous_views = current_views


    async def test_sorting_random(self):
        target_sorting = "random"
        self.assertIn(target_sorting, SORTING)
        result = await api.search(sorting=target_sorting)
        self.assertIsNotNone(result["meta"]["seed"]) # random set seed


    async def test_sorting_favorites(self):
        target_sorting = "favorites"
        self.assertIn(target_sorting, SORTING)

        response = await api.search(sorting=target_sorting, order="desc")

        wallpapers = response["data"]
        previous_favorites = int(wallpapers[0][target_sorting])
        for wallpaper in wallpapers:
            current_favorites = int(wallpaper[target_sorting])
            self.assertLessEqual(current_favorites, previous_favorites)
            previous_favorites = current_favorites


    async def test_at_least(self):
        target_at_least = "3000x3000"
        response = await api.search(atleast=target_at_least)

        at_least_resolution = target_at_least.split("x")
        at_least_x = at_least_resolution[0]
        at_least_y = at_least_resolution[1]

        wallpapers = response["data"]
        for wallpaper in wallpapers:
            current_resolution = wallpaper["resolution"].split("x")
            current_x = current_resolution[0]
            current_y = current_resolution[1]
            self.assertGreaterEqual(int(current_x), int(at_least_x))
            self.assertGreaterEqual(int(current_y), int(at_least_y))


    async def test_resolution(self):
        target_resolution = ["1920x1080"]
        response = await api.search(resolutions=target_resolution)

        wallpapers = response["data"]
        for wallpaper in wallpapers:
            self.assertEqual(wallpaper["resolution"], target_resolution[0])


    async def test_ratios(self):
        target_ratio = "1x1"
        response = await api.search(ratios=target_ratio)

        wallpapers = response["data"]
        for wallpaper in wallpapers:
            self.assertEqual(1.0, float(wallpaper["ratio"]))


    async def test_color(self):
        target_color = "000000"
        response = await api.search(colors=target_color)
        wallpapers = response["data"]

        for wallpaper in wallpapers:
            self.assertIn("#" + target_color, wallpaper["colors"])


    async def test_page(self):
        target_page = "2"
        response = await api.search(q="anime", page=target_page)
        self.assertEqual(int(target_page), int(response["meta"]["current_page"]))


    # ------------------------------ #
    #      Manual Test Section       #
    # ------------------------------ #
    # These tests can't be fully verified in some cases
    # some of them are fully random
    # some of just don't have regularity to check
    # so just assume the tests below are ok if we have 200==OK response

    async def test_sorting_toplist(self):
        target_sorting = "toplist"
        self.assertIn(target_sorting, SORTING)
        response = await api.search(sorting=target_sorting)
        self.assertIsNotNone(response["data"])


    async def test_sorting_relevance(self):
        target_sorting = "relevance"
        self.assertIn(target_sorting, SORTING)
        response = await api.search(sorting=target_sorting)
        self.assertIsNotNone(response["data"])


    async def test_toprange(self):
        target_toprange = "1d"
        self.assertIn(target_toprange, TOPRANGE)
        response = await api.search("anime")
        self.assertIsNotNone(response["data"])


    # Something is completely wrong with seed values
    # it seems that API just ignores it, because different seeds
    # give same page of wallpapers (even with sorting=random)
    async def test_seed(self):
        target_seed = "abc123"
        response = await api.search(seed=target_seed)
        self.assertIsNotNone(response["data"])



class ApiTestGet(unittest.IsolatedAsyncioTestCase):
    # Sometimes tests cause unclosed socket warnings
    # I couldn't beat this yet, maybe something happens in _get_method of the API
    # if you know the issue, please open pull request with possible decision
    def setUp(self):
        warnings.filterwarnings(
            action="ignore",
            message="unclosed",
            category=ResourceWarning)
        return super().setUp()


    async def test_get_collections(self):
        username = "Raylz"
        response = await api.get_collections(username)
        target_purity = "sfw"

        if response["data"]:
            collection_id = response["data"][0]["id"]
            response = await api.get_collections(username,
                                                collection_id,
                                                purity=[target_purity])

            collection_wallpapers = response["data"]
            for wallpaper in collection_wallpapers:
                self.assertEqual(wallpaper["purity"], target_purity)


    async def test_get_tag(self):
        res = await api.get_tag(1)
        self.assertIsNotNone(res["data"])


    async def test_get_settings(self):
        res = await api.my_settings()
        self.assertIsNotNone(res["data"])


    async def test_get_user_uploads(self):
        res = await api.get_user_uploads("provip")
        self.assertIsNotNone(res["data"])


    async def test_get_wallpaper(self):
        test_wallpaper_id = "e7jj6r"
        res = await api.get_wallpaper(test_wallpaper_id)
        self.assertIsNotNone(res["data"])


if __name__ == "__main__":
    unittest.main()
