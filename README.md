# aiowallhaven

aiowallhaven is an asynchronous API wrapper for popular
wallpaper hosting site wallhaven.cc.

## Basic Usage:

```
import asyncio
from aiowallhaven import WallHavenAPI

wallhaven = WallHavenAPI("Your-API-key")

async def wallpaper_details():
    request = await wallhaven.get_wallpaper("5758y8")
    print(request)

loop = asyncio.get_event_loop()
loop.run_until_complete(wallpaper_details())
```

## Prerequisites
The following dependencies are required:

- Python 3.10
- aiohttp library
- aiolimiter library

## Installation

```
$ pip install aiowallhaven
```

## Documentation

The documentation is available at [readthedocks](https://aiowallhaven.readthedocs.io/en/latest/).

## License

aiowallhaven is developed and distributed under the MIT
license.
