import logging

import pyodbc
from pyodbc import OperationalError

from journals.config import LOGIN, PASSWORD, SERVER
from telegram.api import send_message

with open('journals/query.sql') as file:
    QUERY = file.read()


def get_notes(rows):
    return [row[5] for row in rows]


def get_rows():
    SERVER['short_name'] = SERVER['name'].split('.')[0]
    for key in 'short_name', 'name', 'ip':
        logging.info(f'{SERVER[key]} connection attempt')
        try:
            connection = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                f'SERVER={SERVER[key]};DATABASE=bill_ab;'
                f'UID={LOGIN};PWD={PASSWORD}', timeout=10,
            )
        except OperationalError as error:
            logging.info(f'{SERVER[key]} connection failure')
            logging.debug(f'{SERVER[key]} error:\n  {error}')
        else:
            cursor = connection.cursor()
            cursor.execute(QUERY)
            rows = cursor.fetchall()
            connection.close()
            logging.info(f'{SERVER[key]} connection success')
            logging.debug(f'{SERVER[key]} result:\n  {rows}')
            return rows
    logging.info('No result received!')


def check(run=True, test=False):
    if not run:
        return
    rows = get_rows()
    msg = '<b>journals</b>\n'
    if rows:
        msg += '\n'.join(get_notes(rows))
    else:
        msg += 'Замечаний нет.'
    send_message(msg, test=test)
