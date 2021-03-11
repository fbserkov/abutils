from datetime import datetime
from textwrap import shorten
from threading import Thread
from time import sleep

import pyodbc
from pyodbc import OperationalError

from jobs.config import LOGIN, PASSWORD, SERVERS
from telegram.api import send_message

with open('jobs/query.sql') as file:
    QUERY = file.read()
RESULT = {}


def _put_rows(key, alias):
    """Put rows from servers to the result list."""
    key_alias = f'{key} ({alias})'
    print(f'{key_alias} connection attempt')
    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={alias};DATABASE=msdb;'
            f'UID={LOGIN};PWD={PASSWORD}', timeout=10,
        )
    except OperationalError as error:
        print(f'{key_alias} connection failure')
        print(f'{key_alias} error:\n  {error}')
        if RESULT.get(key) is None:
            RESULT[key] = None
    else:
        cursor = connection.cursor()
        cursor.execute(QUERY)
        rows = cursor.fetchall()
        connection.close()
        print(f'{key_alias} connection success')
        print(f'{key_alias} result:\n  {rows}')
        RESULT[key] = rows


def _result_reception():
    """Reception results of servers polling."""
    threads = []
    for server in SERVERS:
        server['short_name'] = server['name'].split('.')[0]
    for alias in 'name', 'ip':
        for server in SERVERS:
            key = server['short_name']
            if RESULT.get(key) is None:
                thread = Thread(
                    target=_put_rows,
                    args=(key, server[alias])
                )
                threads.append(thread)
                thread.start()
        sleep(2)
    for thread in threads:
        thread.join()


def _replace_angle_brackets(line):
    line = line.replace('<', '&lt;')
    line = line.replace('>', '&gt;')
    return line


def _get_row_text(row):
    """Generates text for one row from server response."""
    job_name, step_id, step_name, date, time, message = row
    message = _replace_angle_brackets(message)
    dt = datetime.strptime(f'{date}{time:06}', '%Y%m%d%H%M%S')
    return (
        f'    <b>Задание:</b> {job_name}\n'
        f'    <b>Шаг:</b> {step_id}) {step_name}\n'
        f'    <b>Дата и время:</b> {dt}\n'
        f'    <b>Сообщение:</b> <i>{shorten(message, 256)}</i>\n'
    )


def _result_sending(test):
    for key in sorted(RESULT):
        text = '<b>jobs</b>\n<i>' + key + '</i>\n'
        rows = RESULT[key]
        if rows is None:
            text += 'Не отвечает.\n'
        elif not rows:
            text += 'Замечаний нет.\n'
        else:
            for row in rows:
                text += _get_row_text(row)
        send_message(text, test=test)


def check(run=True, test=False):
    if not run:
        return
    _result_reception()
    _result_sending(test)
