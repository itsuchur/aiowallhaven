import asyncio
import subprocess
import sys
import unittest
from unittest.mock import patch

import aiohttp
from aiohttp import web

from aiowallhaven import WallHavenAPI
from aiowallhaven.wallhaven_types import Purity, Ratio, Resolution


class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.requests = []
        self.status = 200
        self.gate = None
        self.arrived = asyncio.Event()

        async def handler(request):
            self.requests.append((dict(request.query), request.transport,
                                  request.headers.get("X-API-key")))
            self.arrived.set()
            if self.gate is not None:
                await self.gate.wait()
            if self.status != 200:
                return web.Response(status=self.status, headers={"Retry-After": "60"})
            return web.json_response({"data": [], "query": dict(request.query)})

        app = web.Application()
        app.router.add_get("/api/v1/{endpoint:.*}", handler)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        self.addAsyncCleanup(self.runner.cleanup)
        site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await site.start()
        port = self.runner.addresses[0][1]
        patcher = patch("aiowallhaven.api.BASE_API_URL", f"http://127.0.0.1:{port}/api")
        patcher.start()
        self.addCleanup(patcher.stop)
        self.api = WallHavenAPI("test-key")
        self.addAsyncCleanup(self.api.close)

    async def test_special_characters_stay_in_query(self):
        for query in ("cats&purity=111", "C++", "#123", "100% café = ?"):
            with self.subTest(query=query):
                result = await self.api.search(q=query)
                self.assertEqual(result["query"], {"q": query})
        self.assertEqual(self.requests[0][2], "test-key")

    async def test_list_filters_are_encoded_once(self):
        result = await self.api.search(
            resolutions=[Resolution(1920, 1080), Resolution(2560, 1440)],
            ratios=[Ratio(16, 9), Ratio(16, 10)],
        )
        self.assertEqual(result["query"], {
            "resolutions": "1920x1080,2560x1440", "ratios": "16x9,16x10",
        })

    async def test_http_errors_preserve_status_and_headers(self):
        for status in (401, 404, 429, 500):
            with self.subTest(status=status):
                self.status = status
                with self.assertRaises(aiohttp.ClientResponseError) as caught:
                    await self.api.get_wallpaper("missing")
                self.assertEqual(caught.exception.status, status)
                self.assertEqual(caught.exception.headers["Retry-After"], "60")
                self.assertEqual(caught.exception.request_info.real_url.path,
                                 "/api/v1/w/missing")

    async def test_session_reuses_connection_and_closes(self):
        async with self.api:
            await self.api.get_tag(1)
            session = self.api._session
            await self.api.get_tag(2)
            self.assertIs(self.requests[0][1], self.requests[1][1])
        self.assertTrue(session.closed)
        await self.api.close()  # closing twice is safe

    async def test_context_closes_after_error(self):
        self.status = 500
        with self.assertRaises(aiohttp.ClientResponseError):
            async with self.api:
                await self.api.get_tag(1)
        self.assertIsNone(self.api._session)

    async def test_cancelled_request_keeps_client_usable(self):
        self.gate = asyncio.Event()
        task = asyncio.create_task(self.api.get_tag(1))
        await asyncio.wait_for(self.arrived.wait(), timeout=5)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.gate.set()
        self.gate = None
        self.assertEqual((await self.api.get_tag(2))["data"], [])

    async def test_collections_filters(self):
        result = await self.api.get_collections("someone", 42, Purity(sfw=True), 2)
        self.assertEqual(result["query"], {"page": "2", "purity": "100"})

    async def test_rate_limit_is_not_shared_between_clients(self):
        other = WallHavenAPI("another-key")
        self.addAsyncCleanup(other.close)
        await self.api._rate_limit.acquire(12)
        result = await asyncio.wait_for(other.get_tag(1), timeout=2)
        self.assertEqual(result["data"], [])


class ImportTests(unittest.TestCase):
    def test_import_does_not_configure_root_logging(self):
        result = subprocess.run(
            [sys.executable, "-c",
             "import logging; before = (list(logging.root.handlers), logging.root.level); "
             "import aiowallhaven; "
             "assert (list(logging.root.handlers), logging.root.level) == before"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
