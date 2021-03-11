from common.alch import Alch
from housing.config import ALCH
from housing.const import (
    ADDRESS_COMPONENTS, BUILDING, BUILDING_TYPE, ENTITIES, MANAGEMENT_COMPANY)
from housing.olson import get_id


alch = Alch(**ALCH)
classes = {
    name: type(
        name,
        (alch.Base, ),
        {'__table__': alch.Table(name, alch.metadata, autoload=True)}
    ) for name in ENTITIES + (ADDRESS_COMPONENTS, )
}
stat = {entity: {'+': 0, '~': 0, '-': 0} for entity in ENTITIES}


def _add_obj(entity, record):
    params = {'uid': record['_uid']}
    if entity != BUILDING:
        params['name'] = record['name']
    if entity == MANAGEMENT_COMPANY:
        for key in ('is_our_company', 'inn', 'kpp', 'ogrn'):
            params[_map(entity, key)] = _get_value(record, key)
    if entity == BUILDING_TYPE:
        params['id'] = record['id']
    if entity == BUILDING:
        for key in (
            'import_uid', 'is_deleted', 'building_type', 'division',
            'exploitation_sector', 'sector', 'exploitation',
            'buildings_group', 'management_company', 'point', 'address',
            'normalized_address', 'house_fias_id', 'street_fias_id',
            'settlement_fias_id', 'cadastral_id', 'extended_code',
            'contract_tags',
        ):
            params[_map(entity, key)] = _get_value(record, key)

        ac_dict = record['address_components']
        ac_params = {'building_uid': record['_uid']}
        for key in (
            'area', 'city', 'flat', 'house', 'region', 'street', 'country',
            'section', 'building', 'settlement', 'postal_code', 'short',
        ):
            ac_params[_map(entity, key)] = _get_value(ac_dict, key)
        ac_obj = classes[ADDRESS_COMPONENTS](**ac_params)
        alch.session.add(ac_obj)

    obj = classes[entity](**params)
    alch.session.add(obj)
    stat[entity]['+'] += 1
    print(f'Add: <{entity}> ' + obj.uid)


def _delete_obj(entity, obj):
    alch.session.delete(obj)
    if entity == BUILDING:
        ac_obj = alch.session.query(classes[ADDRESS_COMPONENTS]).get(obj.uid)
        alch.session.delete(ac_obj)

    stat[entity]['-'] += 1
    print(f'Delete: <{entity}> ' + obj.uid)


def _get_uid_or_none(record):
    if record:
        return record['_uid']


def _get_value(record, key):
    value = record.get(key)
    if value is not None:
        if key in set(ENTITIES) - {BUILDING}:
            value = _get_uid_or_none(value)
        if key == 'point':
            value = get_id(value)
        if key == 'contract_tags':
            value = ', '.join(value)
        if key == 'short':
            value = value.get('locality')
    return value


def _map(entity, key):
    if entity == BUILDING:
        if key in set(ENTITIES) - {BUILDING}:
            return key + '_uid'
        if key == 'point':
            return 'olson_id'
        if key == 'building':
            return 'building_number'
        if key == 'short':
            return 'locality'
        return key
    if entity == MANAGEMENT_COMPANY:
        return key


def _update_field(obj, field, record, key, changes):
    value = _get_value(record, key)
    if getattr(obj, field) != value:
        setattr(obj, field, value)
        changes.append(key)


def _update_obj(entity, obj, record):
    changes = []
    if entity != BUILDING:
        _update_field(obj, 'name', record, 'name', changes)
    if entity == MANAGEMENT_COMPANY:
        for key in ('is_our_company', 'inn', 'kpp', 'ogrn'):
            _update_field(obj, _map(entity, key), record, key, changes)
    if entity == BUILDING_TYPE:
        _update_field(obj, 'id', record, 'id', changes)
    if entity == BUILDING:
        for key in (
            'import_uid', 'is_deleted', 'building_type', 'division',
            'exploitation_sector', 'sector', 'exploitation',
            'buildings_group', 'management_company', 'point', 'address',
            'normalized_address', 'house_fias_id', 'street_fias_id',
            'settlement_fias_id', 'cadastral_id', 'extended_code',
            'contract_tags',
        ):
            _update_field(obj, _map(entity, key), record, key, changes)

        ac_dict = record['address_components']
        ac_obj = alch.session.query(classes[ADDRESS_COMPONENTS]).get(obj.uid)
        for key in (
            'area', 'city', 'flat', 'house', 'region', 'street', 'country',
            'section', 'building', 'settlement', 'postal_code', 'short',
        ):
            _update_field(ac_obj, _map(entity, key), ac_dict, key, changes)

    if changes:
        stat[entity]['~'] += 1
        print(f'Update: <{entity}>', obj.uid, changes)


def sync_entity(data, entity):
    objs = {obj.uid: obj for obj in alch.session.query(classes[entity])}
    no_delete = set()

    count = 0
    for record in data[entity]:
        count += 1
        print('Update|Add Cycle:', count)
        no_delete.add(record['_uid'])
        obj = objs.get(record['_uid'])
        if obj:
            _update_obj(entity, obj, record)
        else:
            _add_obj(entity, record)

    for obj in alch.session.query(classes[entity]):
        if obj.uid not in no_delete:
            _delete_obj(entity, obj)
