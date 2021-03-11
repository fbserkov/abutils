from os.path import join
import pickle

from lxml.html import fromstring
import requests

DIR = 'telegram'
proxy_iter = None


def _get_proxy_list():
    response = requests.get('https://free-proxy-list.net')
    html_parser = fromstring(response.text)
    for i in html_parser.xpath('//tbody/tr'):
        if i.xpath('.//td[7]/text()')[0] == 'yes':  # column 'Https'
            ip = i.xpath('.//td[1]/text()')[0]  # column 'IP Address'
            port = i.xpath('.//td[2]/text()')[0]  # column 'Port'
            yield {'https': f'{ip}:{port}'}


def get_proxy(refresh):
    global proxy_iter
    if refresh:
        if not proxy_iter:
            proxy_iter = _get_proxy_list()
        try:
            proxy = next(proxy_iter)
        except StopIteration:
            proxy_iter = _get_proxy_list()
            proxy = next(proxy_iter)
        with open(join(DIR, 'proxy.pickle'), 'wb') as file:
            pickle.dump(proxy, file)
        print(f'Next proxy: {proxy}')
        return proxy
    else:
        try:
            with open(join(DIR, 'proxy.pickle'), 'rb') as file:
                proxy = pickle.load(file)
            print(f'Saved proxy: {proxy}')
            return proxy
        except FileNotFoundError:
            return get_proxy(refresh=True)
