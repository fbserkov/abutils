from textwrap import shorten

import requests
from requests.exceptions import ProxyError, SSLError, Timeout

from telegram.config import MAIN_CHAT, TEST_CHAT, TOKEN
from telegram.proxy import get_proxy


def _make_request(method, payload=None, files=None):
    print(f'Call {method}()')
    url = f'https://api.telegram.org/bot{TOKEN}/{method}'
    refresh = False
    while True:
        try:
            if files:
                response = requests.post(
                    url, proxies=get_proxy(refresh),
                    data=payload, files=files, timeout=30,
                )
            else:
                response = requests.get(
                    url, proxies=get_proxy(refresh),
                    params=payload, timeout=30,
                )
            return response.json()
        except (ProxyError, SSLError, Timeout) as error:
            print('Error class:', error.__class__)
            print('Description:', error)
            refresh = True


def get_me():
    print(_make_request('getMe'))


def get_updates():
    print(_make_request('getUpdates'))


def send_message(text, test=False):
    if not text:
        return
    if len(text) > 4096:
        text = shorten(text, 4096)

    _make_request('sendMessage', {
        'chat_id': TEST_CHAT if test else MAIN_CHAT,
        'text': text,
        'parse_mode': 'HTML',
    })


def send_photo(file, test=False):
    _make_request(
        'sendPhoto',
        {'chat_id': TEST_CHAT if test else MAIN_CHAT},
        {'photo': file},
    )
