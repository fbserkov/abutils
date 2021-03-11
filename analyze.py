from pprint import pprint

from housing.const import ENTITIES
from common.dumper import Dumper


class Analyze:
    def __init__(self, items, print_tree):
        self.items = items
        tree = {}
        for item in self.items:
            self._put(tree, item)
        if print_tree:
            pprint(tree)

    def _get_values(self, keys):
        values = []
        for item in self.items:
            value = item
            for key in keys:
                if value is None:
                    break
                value = value[key]
            else:
                values.append(value)
        return values

    def _put(self, target, source):
        if not isinstance(source, dict):
            return
        for key, value in source.items():
            if key not in target:
                target[key] = {}
                self._put(target[key], value)

    def analyze(self, keys):
        values = self._get_values(keys)
        types = {type(value) for value in values}
        if type(None) in types:
            values = [value for value in values if value]
            types -= {type(None)}
            if len(types):
                assert len(types) == 1, 'Must be one non-empty type!'
                print(keys, 'some values are empty')
            else:
                print(keys, 'all values are empty')
                return
        print(keys, types)
        if float in types:
            print('Minimum value:', min(values))
            print('Maximum value:', max(values))
        if int in types:
            print('Minimum value:', min(values))
            print('Maximum value:', max(values))
        if list in types:
            print('Minimum length:', min([len(value) for value in values]))
            print('Maximum length:', max([len(value) for value in values]))
            values_used = set()
            for value in values:
                values_used |= set(value)
            print('Values used:', sorted(values_used))
        if str in types:
            print('Minimum length:', min([len(value) for value in values]))
            print('Maximum length:', max([len(value) for value in values]))
            symbols_used = set()
            for value in values:
                symbols_used |= set(value)
            print('Symbols used:', ''.join(sorted(symbols_used)))


def main():
    entity = ENTITIES[7]
    print(entity)
    dumper = Dumper('housing')
    items = dumper.read(entity)

    Analyze(items, print_tree=False).analyze(
        keys=('contract_tags', ))
    # keys=('management_company', 'acquisition_date'))
    # keys=('management_company', 'created'))
    # keys=('extra_attrs', 'living_space'))
    # keys=('address', ))
    # keys=('_version', ))


if __name__ == '__main__':
    main()
