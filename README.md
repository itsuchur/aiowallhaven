# aiowallhaven

aiowallhaven is an asynchronous API wrapper for wallhaven.cc.

## Basic usage

```python
import asyncio
from aiowallhaven import WallHavenAPI

async def wallpaper_details():
    async with WallHavenAPI("Your-API-key") as wallhaven:
        wallpaper = await wallhaven.get_wallpaper("5758y8")
        print(wallpaper)

asyncio.run(wallpaper_details())
```

Use the client on a single event loop. The async context manager closes its
reusable connection pool, including when a request fails. If you manage the
client yourself, call `await wallhaven.close()` when finished. Each client has
its own rate limiter; multiple clients do not share an aggregate rate limit.
HTTP errors raise `aiohttp.ClientResponseError`, with the response status,
headers (including `Retry-After`), and request information available to callers.

## Installation

Python 3.12 or newer is required. Runtime dependencies are aiohttp and aiolimiter.

```console
pip install aiowallhaven
```

## Development

Use Poetry to install the versions recorded in `poetry.lock`:

```console
poetry install
poetry run python -m unittest discover -v
poetry check --lock
poetry build
```

The default tests run against a local HTTP server and require no API key or
internet connection. To run the optional live tests, set `WALLHAVEN_API_KEY`
and run `poetry run python -m unittest aiowallhaven.api_tests -v`.

`pyproject.toml` declares runtime dependencies and package metadata;
`poetry.lock` records the development environment resolution.
Pip users can install the project with `pip install .`; a root
`requirements.txt` is not required. Read the Docs uses the separate
`docs/requirements.txt` for documentation dependencies.

## Documentation

The documentation is available at [Read the Docs](https://aiowallhaven.readthedocs.io/en/latest/).

## License

aiowallhaven is developed and distributed under the MIT license.
