import json
import os


class Dumper:
    def __init__(self, package):
        self.path = os.path.join(package, 'dumper')

    def _get_filename(self, entity):
        return os.path.join(self.path, entity + '.txt')

    def write(self, entity, items):
        os.makedirs(self.path, exist_ok=True)
        with open(self._get_filename(entity), 'w', encoding='UTF-8') as file:
            lines = (
                json.dumps(item, ensure_ascii=False) + '\n' for item in items)
            file.writelines(lines)

    def read(self, entity):
        try:
            with open(self._get_filename(entity), encoding='UTF-8') as file:
                result = [json.loads(line) for line in file]
            print(f'{len(result)} lines read: {entity}')
            return result
        except FileNotFoundError:
            print(f'Dump not found: {entity}')
