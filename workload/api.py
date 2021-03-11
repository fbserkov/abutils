import datetime
import os
from pyodbc import connect, OperationalError, ProgrammingError
from time import sleep

import matplotlib.pyplot as plt

from telegram.api import send_photo
from workload.config import LOGIN, PASSWORD, SERVER
from workload.const import KEYS, LABELS, PATH


def _calc_metric(_len, _sum):
    if _len:
        return _sum*1000/_len
    return 0


def _calc_sum(rows):
    return sum((
        row['collection_time'] -
        row['start_time']).total_seconds() for row in rows
    )


def _filter_rows(rows):
    rows_all = [row for row in rows if (
        row['database_name'] == 'bill_ab' and
        row['login_name'] == 'AggregateDatabaseApi'
    )]
    rows_pa = [row for row in rows_all if (
        '[lk].[v_personal_account_vtb]' in row['sql_text'])]
    rows_tbs = [row for row in rows_all if (
        '[lk].[v_turnover_balance_sheet]' in row['sql_text'])]
    return {'all': rows_all, 'pa': rows_pa, 'tbs': rows_tbs}


def _get_connection():
    return connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={SERVER};DATABASE=master;'
        f'UID={LOGIN};PWD={PASSWORD}', timeout=10,
    )


def _get_metric(cursor):
    rows = _get_rows(cursor)
    rows_list = _filter_rows(rows)

    _length, _sum = {}, {}
    for key in rows_list:
        _length[key] = len(rows_list[key])
        _sum[key] = _calc_sum(rows_list[key])
        print(
            f'length_{key}: {_length[key]},',
            f'sum_{key}: {_sum[key]:.3f} s'
        )
    return _length, _sum


def _get_rows(cursor):
    try:
        cursor.execute('EXEC sp_WhoIsActive')
        items = cursor.fetchall()
    except OperationalError:
        print('OperationalError')
        return []
    except ProgrammingError:
        print('ProgrammingError')
        return []
    return [dict(zip(KEYS, item)) for item in items]


def _prepare_data(data, key):
    x = [item[0].hour + item[0].minute/60 for item in data]
    y = [_calc_metric(
        item[1][key]['len'], item[1][key]['sum']) for item in data]
    return x, y


def _prepare_data2(data, key):
    x = [item[0].hour + item[0].minute/60 for item in data]
    y = [item[1][key]['len'] for item in data]
    return x, y


def log():
    start = datetime.datetime.now()
    connection = _get_connection()
    cursor = connection.cursor()

    result = {
        'all': {'len': 0, 'sum': 0},
        'pa': {'len': 0, 'sum': 0},
        'tbs': {'len': 0, 'sum': 0},
    }
    while datetime.datetime.now() < start + datetime.timedelta(minutes=5):
        _length, _sum = _get_metric(cursor)
        for key in 'all', 'pa', 'tbs':
            result[key]['len'] += _length[key]
            result[key]['sum'] += _sum[key]
        sleep(10)

    os.makedirs(PATH, exist_ok=True)
    name = f'{start.month:02}{start.day:02}'
    with open(os.path.join(PATH, name + '.log'), 'a') as file:
        print(repr([start, result]), file=file)
    connection.close()


def plot(run=True, name=None, test=False):
    if not run:
        return
    if not name:
        _date = datetime.date.today() - datetime.timedelta(days=1)
        name = f'{_date.month:02}{_date.day:02}'
    with open(os.path.join(PATH, name + '.log')) as file:
        data = [eval(line) for line in file]
    average = 0
    for key in 'all', 'pa', 'tbs':
        x, y = _prepare_data(data, key)
        if key == 'all':
            average = sum(y)/len(y)
        plt.plot(x, y, label=LABELS[key])

    axes = plt.gca()
    axes.set_xlim([0, 24])
    axes.set_ylim([0, 2*average])
    plt.xticks([0, 3, 6, 9, 12, 15, 18, 21, 24])
    plt.grid()

    plt.legend()
    plt.title(f'workload ({name[2:]}.{name[:2]})')
    plt.xlabel('Время, час')
    plt.ylabel('Длительность запроса, мс')

    plt.savefig(os.path.join(PATH, 'fig.png'))
    with open(os.path.join(PATH, 'fig.png'), 'rb') as file:
        send_photo(file, test)


def plot2(run=True, name=None, test=False):
    if not run:
        return
    if not name:
        _date = datetime.date.today() - datetime.timedelta(days=1)
        name = f'{_date.month:02}{_date.day:02}'
    with open(os.path.join(PATH, name + '.log')) as file:
        data = [eval(line) for line in file]
    for key in 'all', 'pa', 'tbs':
        x, y = _prepare_data2(data, key)
        plt.plot(x, y, label=LABELS[key])

    axes = plt.gca()
    axes.set_xlim([0, 24])
    plt.xticks([0, 3, 6, 9, 12, 15, 18, 21, 24])
    plt.grid()

    plt.legend()
    plt.title(f'workload ({name[2:]}.{name[:2]})')
    plt.xlabel('Время, час')
    plt.ylabel('Активность запроса, баллы')

    plt.savefig(os.path.join(PATH, 'fig2.png'))
    with open(os.path.join(PATH, 'fig2.png'), 'rb') as file:
        send_photo(file, test)
