# aiowallhaven

aiowallhaven is an asynchronous API wrapper for popular 
wallpaper hosting site wallhaven.cc.

## Basic Usage:

```
from aiowallhaven import WallHavenAPI

request = await WallHavenAPI("Your-API-key").get_wallpaper("5758y8")
print(request)
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
## License

aiowallhaven is developed and distributed under the MIT 
license.
