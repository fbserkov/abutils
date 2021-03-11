import json
import requests


def get_contractors(base_url, token):
    response = requests.get(
        url=f'{base_url}/contractors',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
    )
    return response


def get_complexes(base_url, token, id_complex):
    response = requests.get(
        url=(
            f'{base_url}/complexes/'
            f'for-contractors?contractorIds={id_complex}'
        ),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
     )
    return response


def get_xml(
        base_url, token, id_contractor, source, date, id_complex):
    q_dict = dict(
        startDate=f'{str(date)}T00:00:00',
        endDate=f'{str(date)}T23:59:59',
        contractors=[id_contractor],
        source=source,
    )
    if id_complex:
        q_dict['complexes'] = [id_complex]

    response = requests.get(
        url=f'{base_url}/reports/transactions/xml?q={json.dumps(q_dict)}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
    )
    key = 'Content-Disposition'
    value = response.headers.get(key)
    if value:
        base_name, extension = value.split('=')[-1].split('.')
        name = f'{base_name}_{source}.{extension}'
    else:
        print(f"KeyError: '{key}'")
        name = None

    empty = "<?xml version='1.0' encoding='UTF-8'?>\n<response result=\"0\"/>"
    xml = response.text
    if xml == empty:
        xml = None

    return xml, name
