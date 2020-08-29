from igramscraper.instagram import Instagram
from random import choice
import urllib3
import requests


proxylist = []

with open("proxies.txt", mode="r") as proxies:
    count = 0
    for proxy in proxies:
        proxylist.append(proxy.strip("\n"))
        count += 1
    print(count, "proxies loaded")

ig = Instagram()


def get_likes(code):
    proxies = {}
    proxy = choice(proxylist)
    proxies["http"] = proxy
    proxies["https"] = proxy
    # ig.set_proxies(proxies)

    post = None
    while post is None:
        try:
            post = ig.get_medias_by_code(code)
        except urllib3.exceptions.ProxySchemeUnknown:
            print("Bad proxy, retrying.")
            proxylist.remove(proxy)
            proxy = choice(proxylist)
            proxies["http"] = proxy
            proxies["https"] = proxy
            ig.set_proxies(proxies)
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError):
            print("Dead proxy, retrying.")
            proxylist.remove(proxy)
            proxy = choice(proxylist)
            proxies["http"] = proxy
            proxies["https"] = proxy
            ig.set_proxies(proxies)

    return int(post.likes_count)
