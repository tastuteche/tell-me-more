import pickle as pk
import asyncio
import requests
from cachecontrol import CacheControl
# NOTE: This requires lockfile be installed
from cachecontrol.caches import FileCache
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import bs4
from cachecontrol.heuristics import ExpiresAfter
from cachecontrol import CacheControlAdapter


def serialize_session(session):
    with open("save.p", "wb") as f:
        pk.dump(session, f)


def deserialize_session():
    with open("save.p", "rb") as f:
        return pk.load(f)


session = None


def init_session():
    global session
    try:
        if session is None:
            session = deserialize_session()
    except:
        session = requests.Session()
        serialize_session(session)


init_session()

sess = CacheControl(session,
                    cache=FileCache('.webcache', forever=True),
                    heuristic=ExpiresAfter(days=1))

# adapter = CacheControlAdapter(cache=FileCache(
#     '.webcache'), heuristic=ExpiresAfter(days=1))  # , forever=True
# sess = requests.Session()
# sess.mount('https://', adapter)


loop = asyncio.get_event_loop()
# p = ProcessPoolExecutor(2)  # Create a ProcessPool with 2 processes
p = ThreadPoolExecutor(2)


async def get_title(url):
    future1 = loop.run_in_executor(p, sess.get, url)
    # future1 = loop.run_in_executor(p, requests.get, url)
    response1 = await future1
    soup = bs4.BeautifulSoup(response1.text, "lxml")
    '''<div class="repository-meta-content col-11 mb-1">
          <span class="col-11 text-gray-dark mr-2" itemprop="about">
            Collection of emacs extensions specifically collected for python development, with workflow guidelines!
          </span>
          <span itemprop="url"><a href="http://gabrielelanaro.github.com/emacs-for-python" rel="nofollow">http://gabrielelanaro.github.com/emac…</a></span>
    </div>'''
    a = soup.find('div', class_='repository-meta-content')
    # print(a.text)
    return a.text


async def main():
    urls = ['https://github.com/ionrock/cachecontrol',
            'https://github.com/gabrielelanaro/emacs-for-python']
    futures = map(lambda url: get_title(url), urls)

    all_data = await asyncio.gather(*futures)
    print(all_data)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
