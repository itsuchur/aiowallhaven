import os
import unittest
from datetime import datetime as dt  # for "sorting" test

from aiowallhaven.api import WallHavenAPI
from aiowallhaven.wallhaven_types import (
    Ratio, Resolution, Sorting, TopRange, Order, Color, Purity, Category)

API_KEY = os.getenv("WALLHAVEN_API_KEY")


def get_wallpaper_datetime(date: str):
    return dt.strptime(date, "%Y-%m-%d %H:%M:%S")


@unittest.skipUnless(API_KEY, "Set WALLHAVEN_API_KEY to run live API tests")
class ApiTestSearch(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.api = WallHavenAPI(API_KEY)

    async def asyncTearDown(self):
        await self.api.close()

    async def test_query(self):
        target_query = "pool"
        response = await self.api.search(q=target_query)
        query = response["meta"]["query"]
        self.assertEqual(query, target_query)

    async def test_categories(self):
        all_categories = [
            Category(general=True),
            Category(anime=True),
            Category(people=True)
        ]

        for category in all_categories:
            response = await self.api.search(category=category)
            wallpapers = response["data"]
            for wallpaper in wallpapers:
                self.assertIn(wallpaper["category"], category._get_active_names())

    async def test_purity(self):
        all_purity = [
            Purity(sfw=True),
            Purity(sketchy=True),
            Purity(nsfw=True)
        ]

        for purity in all_purity:
            response = await self.api.search(purity=purity)
            wallpapers = response["data"]
            for wallpaper in wallpapers:
                self.assertIn(wallpaper["purity"], purity._get_active_names())

    async def test_sorting_date_added(self):
        target_sorting = Sorting.date_added
        target_order = Order.desc
        response = await self.api.search(sorting=target_sorting, order=target_order)

        wallpapers = response["data"]
        previous_date = get_wallpaper_datetime(wallpapers[0]["created_at"])
        for wallpaper in wallpapers:
            current_wallpaper_date = get_wallpaper_datetime(wallpaper["created_at"])
            self.assertLessEqual(current_wallpaper_date, previous_date)
            previous_date = current_wallpaper_date

    async def test_sorting_views(self):
        target_sorting = Sorting.views
        target_order = Order.desc
        response = await self.api.search(sorting=target_sorting, order=target_order)
        wallpapers = response["data"]

        previous_views = int(wallpapers[0][target_sorting.value])
        for wallpaper in wallpapers:
            current_views = int(wallpaper[target_sorting.value])
            self.assertLessEqual(current_views, previous_views)
            previous_views = current_views

    async def test_sorting_random(self):
        target_sorting = Sorting.random
        result = await self.api.search(sorting=target_sorting)
        self.assertIsNotNone(result["meta"]["seed"])  # random set seed

    async def test_sorting_favorites(self):
        target_sorting = Sorting.favorites
        target_order = Order.desc
        response = await self.api.search(sorting=target_sorting, order=target_order)

        wallpapers = response["data"]
        previous_favorites = int(wallpapers[0][target_sorting.value])
        for wallpaper in wallpapers:
            current_favorites = int(wallpaper[target_sorting.value])
            self.assertLessEqual(current_favorites, previous_favorites)
            previous_favorites = current_favorites

    async def test_at_least(self):
        target_at_least = Resolution(3000, 3000)
        response = await self.api.search(atleast=target_at_least)

        wallpapers = response["data"]
        for wallpaper in wallpapers:
            current_resolution = wallpaper["resolution"].split("x")
            current_x = current_resolution[0]
            current_y = current_resolution[1]
            self.assertGreaterEqual(int(current_x), int(target_at_least.x))
            self.assertGreaterEqual(int(current_y), int(target_at_least.y))

    async def test_resolution(self):
        target_resolution = [Resolution(1920, 1080)]
        response = await self.api.search(resolutions=target_resolution)

        wallpapers = response["data"]
        for wallpaper in wallpapers:
            self.assertEqual(wallpaper["resolution"], str(target_resolution[0]))

    async def test_ratios(self):
        target_ratio = Ratio(1, 1)
        response = await self.api.search(ratios=[target_ratio])

        wallpapers = response["data"]
        for wallpaper in wallpapers:
            self.assertEqual(target_ratio.x/target_ratio.y, float(wallpaper["ratio"]))

    async def test_color(self):
        target_color = Color.black
        response = await self.api.search(color=target_color)
        wallpapers = response["data"]

        for wallpaper in wallpapers:
            self.assertIn("#" + target_color.value, wallpaper["colors"])

    async def test_page(self):
        target_page = 2
        response = await self.api.search(q="anime", page=target_page)
        self.assertEqual(target_page, int(response["meta"]["current_page"]))

    # ------------------------------ #
    #      Manual Test Section       #
    # ------------------------------ #
    # These tests can't be fully verified in some cases
    # some of them are fully random
    # some of just don't have regularity to check
    # so just assume the tests below are ok if we have 200==OK response

    async def test_sorting_toplist(self):
        target_sorting = Sorting.toplist
        response = await self.api.search(sorting=target_sorting)
        self.assertIsNotNone(response["data"])

    async def test_sorting_relevance(self):
        target_sorting = Sorting.relevance
        response = await self.api.search(sorting=target_sorting)
        self.assertIsNotNone(response["data"])

    async def test_toprange(self):
        target_toprange = TopRange.one_day
        response = await self.api.search("anime", sorting=Sorting.toplist,
                                         toprange=target_toprange)
        self.assertIsNotNone(response["data"])

    async def test_seed(self):
        target_seed = "abc123"
        response = await self.api.search(sorting=Sorting.random, seed=target_seed)
        self.assertEqual(response["meta"]["seed"], target_seed)


@unittest.skipUnless(API_KEY, "Set WALLHAVEN_API_KEY to run live API tests")
class ApiTestGet(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.api = WallHavenAPI(API_KEY)

    async def asyncTearDown(self):
        await self.api.close()

    async def test_get_collections(self):
        username = "Raylz"
        target_purity = Purity(sfw=True)

        # first - get all collections
        response = await self.api.get_collections(username)

        # if there is something in the list - take first collection
        if response["data"]:
            collection_id = response["data"][0]["id"]
            response = await self.api.get_collections(username,
                                                 collection_id,
                                                 purity=target_purity)

            collection_wallpapers = response["data"]
            for wallpaper in collection_wallpapers:
                self.assertIn(wallpaper["purity"], target_purity._get_active_names())

    async def test_get_tag(self):
        res = await self.api.get_tag(1)
        self.assertIsNotNone(res["data"])

    async def test_get_settings(self):
        res = await self.api.my_settings()
        self.assertIsNotNone(res["data"])

    async def test_get_user_uploads(self):
        res = await self.api.get_user_uploads("provip")
        self.assertIsNotNone(res["data"])

    async def test_get_wallpaper(self):
        test_wallpaper_id = "e7jj6r"
        res = await self.api.get_wallpaper(test_wallpaper_id)
        self.assertEqual(res['data']['id'], test_wallpaper_id)
        self.assertIsNotNone(res["data"])


if __name__ == "__main__":
    unittest.main()
