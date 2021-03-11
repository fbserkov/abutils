# Введение

Проверка наличия в журнале сообщений об ошибках в течение прошедших суток.

# Примеры команд

Отображение справочной информации:

    python journals/main.py -h

## Поиск ошибок и вывод сообщения

Консоль:

    python journals/main.py journals/config.json

Запись в файл:

    python journals/main.py journals/config.json > <filename>

Стандартный ввод другого приложения:

    python journals/main.py journals/config.json | python <name>.py

# Конфигурационный файл

config.py  
Позволяет задать сервер и пользователя.

# Файл с запросом

[query.sql](query.sql)  
Запрос, который выполняется для поиска записей об ошибках.
