from threading import Thread
from time import time

import requests

from common.dumper import Dumper
from housing.config import API
from housing.const import ENTITIES
from housing.sync import alch, stat, sync_entity
from telegram.api import send_message


def _get_msg():
    msg = ''
    for entity in ENTITIES:
        if stat[entity]["+"] or stat[entity]["~"] or stat[entity]["-"]:
            msg += '<i>' + entity + '</i> - '
            if stat[entity]['+']:
                msg += f'добавлено: {stat[entity]["+"]}, '
            if stat[entity]['~']:
                msg += f'обновлено: {stat[entity]["~"]}, '
            if stat[entity]['-']:
                msg += f'удалено: {stat[entity]["-"]}, '
            msg += '\n'
    if not msg:
        msg = 'Изменений нет.'
    return '<b>housing</b>\n' + msg


def _get_url_data_target(session, url, pages, result):
    while pages:
        page = pages.pop()
        print('Pages left:', len(pages))
        response = session.get(url, params={'page': page + 1})
        result[page] = response.json()['results']


def _get_url_data_thread(base_url, login, password, entity):
    start = time()
    result = {}
    session = requests.Session()
    session.auth = login, password
    url = f'{base_url}/{entity.replace("_", "")}-list'
    print(url)

    response = session.get(url)
    if response.status_code == 200:
        pages = list(range(response.json()['pages']))
    else:
        print(f'No pages for url: {url}')
        pages = []
    if not pages:
        return result

    threads = []
    for _ in range(5):
        thread = Thread(
            target=_get_url_data_target,
            args=(session, url, pages, result)
        )
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    print(f'Execution time: {time() - start:.3f} seconds')
    for key in sorted(result):
        for item in result[key]:
            yield item


def sync(run=True, commit=True, quick=False, test=False):
    if not run:
        return
    dumper = Dumper('housing')
    data = {}
    for entity in ENTITIES:
        if quick:
            data[entity] = list(dumper.read(entity))
        else:
            data[entity] = list(
                _get_url_data_thread(
                    API['base_url'], API['login'], API['password'], entity))
            dumper.write(entity, data[entity])
        sync_entity(data, entity)
        if commit:
            alch.session.commit()
    send_message(_get_msg(), test=test)
