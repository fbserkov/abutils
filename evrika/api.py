import io
import json
import os

import requests
from smb.SMBConnection import SMBConnection

from evrika.it_e_api import get_xml
from evrika.config import (
    BASE_URL, DATE, IP, MAP, PACKAGE_DIR, PASSWORD,
    PATH, PATH2, SERVICE_NAME, TITLE, USERNAME,
)
from telegram.api import send_message

MODE = ''
NAMES = []


def _create_path(connection, path):
    try:
        connection.createDirectory(SERVICE_NAME, path[:-3])
    except:
        pass
    try:
        connection.createDirectory(SERVICE_NAME, path)
    except:
        pass

def get_connection():
    if MODE == 'local_test':
        return None
    try:
        connection = SMBConnection(
            USERNAME, PASSWORD, 'localpcname', 'servername',
            domain='comf', is_direct_tcp=True,
        )
        connection.connect(IP, 445)
        return connection
    except Exception as error:
        print(error.__class__)
        print(error)
        print(TITLE + 'Error: SMBConnection()')
        exit(1)


def get_token(base_url, username, password):
    try:
        response = requests.post(
            url=f'{base_url}/login',
            json={'username': username, 'password': password},
            headers={'Content-Type': 'application/json'},
        )
        return response.json()
    except Exception as error:
        print(error.__class__)
        print(error)
        print(TITLE + 'Error: get_token()')
        exit(1)


def write2local(path, name, xml):
    os.makedirs(path, exist_ok=True)
    full_name = os.path.join(path, name)
    with open(full_name, 'w') as file:
        file.write(xml)
    return full_name


def write2samba(
        connection, service_name, path, directory, subdirectory, name, xml):
    full_name = f'{path}\\{directory}\\{subdirectory}\\{name}'
    file = io.BytesIO(xml.encode())
    try:
        connection.storeFile(service_name, full_name, file)
    except Exception as error:
        print(error.__class__)
        print(error)
        print(TITLE + 'Error: storeFile()')
        exit(1)
    return full_name


def handle_core(connection, token, directory, subdirectory, source):
    name, xml = None, None
    try:
        xml, name = get_xml(
            BASE_URL, token, directory['id_contractor'],
            source, DATE, subdirectory['id_complex'],
        )
    except Exception as error:
        print(error.__class__)
        print(error)
        print(TITLE + 'Error: get_xml()')
        exit(1)

    if name and xml:
        NAMES.append(name)
        if MODE == 'local_test':
            path = os.path.join(
                PACKAGE_DIR, 'temp', directory['name'], subdirectory['name'])
            full_name = write2local(path, name, xml)

            path = os.path.join(
                PACKAGE_DIR, 'temp', MAP[directory['name']],
                '9701065411', f'{DATE.year}', f'{DATE.month:02}',
            )
            write2local(path, name, xml)
        else:
            path = PATH + '\\test' if MODE == 'samba_test' else PATH
            full_name = write2samba(
                connection, SERVICE_NAME, path,
                directory['name'], subdirectory['name'], name, xml,
            )
            path = PATH2 + '\\Тест' if MODE == 'samba_test' else PATH2
            directory = MAP[directory['name']]
            subdirectory = f'9701065411\\{DATE.year}\\{DATE.month:02}'
            _create_path(connection, f'{path}\\{directory}\\{subdirectory}')
            write2samba(
                connection, SERVICE_NAME, path,
                directory, subdirectory, name, xml,
            )
        print(f'Stored: ' + full_name)


def handle(connection, username, password, directories):
    token = get_token(BASE_URL, username, password)
    for directory in directories:
        for subdirectory in directory['subdirectories']:
            for source in subdirectory['sources']:
                handle_core(connection, token, directory, subdirectory, source)


def load(run=True, test=False):
    if not run:
        return
    if test:
        global MODE
        MODE = 'samba_test'  # local_test, samba_test

    targets = []
    path = os.path.join(PACKAGE_DIR, 'targets')
    for name in os.listdir(path):
        if name[0] == '_':
            continue
        with open(os.path.join(path, name), encoding='UTF-8') as file:
            targets.append(json.load(file))

    connection = get_connection()
    for target in targets:
        handle(connection, **target)
    if connection:
        connection.close()
    send_message(TITLE + f'Загружено реестров: {len(NAMES)}', test=test)
