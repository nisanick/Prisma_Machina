import aiohttp
import async_timeout
import json
import urllib.parse
from bs4 import BeautifulSoup

class Web:

    @staticmethod
    async def get_response(link, parameters=None):
        async with aiohttp.ClientSession() as session:
            with async_timeout.timeout(10):
                if parameters:
                    url = "{}?{}".format(link, urllib.parse.urlencode(parameters))
                else:
                    url = '{}'.format(link)
                async with session.get(url) as response:
                    return json.loads(await response.text(encoding='utf8'))

    @staticmethod
    async def get_site_header(article_id):
        async with aiohttp.ClientSession() as session:
            with async_timeout.timeout(10):
                url = "http://www.prismatic-imperium.com/news.php?id={}".format(article_id)
                async with session.get(url) as response:
                    soup = BeautifulSoup(await response.text(), "html.parser")
                    title = soup.find("meta", property="og:title")
                    url = soup.find("meta", property="og:url")
                    description = soup.find("meta", property="og:description")
                    image = soup.find("meta", property="og:image")
                    return {
                        'title': title['content'],
                        'url': url['content'],
                        'description': description['content'],
                        'image': image['content']
                    }
