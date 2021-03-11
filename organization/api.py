import requests

from common.alch import Alch
from organization.config import ALCH, API
from telegram.api import send_message

alch = Alch(**ALCH)
stat = 0
url_session = requests.Session()
url_session.auth = API['login'], API['password']


class Company(alch.Base):
    __table__ = alch.Table('company', alch.metadata, autoload=True)


def _find_uid(company):
    inn, kpp = company.inn, company.kpp
    if not (inn and kpp):
        print(f'No inn or kpp: inn={inn} kpp={kpp}')
        _update_uid(company)
        return

    response = url_session.get(
        API['base_url'], params={'inn': inn, 'kpp': kpp})
    if response.status_code != 200:
        print('Bad status code!')
        return

    results = response.json()['results']
    if not results:
        print('No result:', 'inn=' + inn, 'kpp=' + kpp)
        _update_uid(company)
        return
    if len(results) > 1:
        print('Multiple results:', 'inn=' + inn, 'kpp=' + kpp)
        _update_uid(company)
    else:
        uid = results[0]['_uid']
        print('Right result:', 'inn=' + inn, 'kpp=' + kpp, 'uid=' + uid)
        _update_uid(company, uid)


def _get_msg():
    if stat:
        msg = f'Изменено uid: {stat}'
    else:
        msg = 'Изменений нет.'
    return '<b>organization</b>\n' + msg


def _update_uid(company, uid=None):
    if company.uid != uid:
        global stat
        stat = stat + 1
        company.uid = uid
        print('Update:', uid)


def sync(run=True, commit=True, test=False):
    if not run:
        return
    count = 0
    for company in alch.session.query(Company):
        count += 1
        print('Find Cycle:', count, end=' ')
        _find_uid(company)
    if commit:
        alch.session.commit()
    send_message(_get_msg(), test=test)
