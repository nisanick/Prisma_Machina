import aiohttp
import async_timeout
import json
import urllib.parse


class Web:

    @staticmethod
    async def get_response(link, parameters):
        async with aiohttp.ClientSession() as session:
            with async_timeout.timeout(10):
                url = "{}?{}".format(link, urllib.parse.urlencode(parameters))
                print(url)
                async with session.get(url) as response:
                    return json.loads(await response.text(encoding='utf8'))
