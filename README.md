# Примитивная база данных

Учебный проект — консольная база данных на Python.

База данных позволяет создавать и удалять таблицы, добавлять, просматривать, изменять и удалять записи. Метаданные и данные таблиц сохраняются в JSON-файлах.

## Возможности

Поддерживаются команды `create_table`, `list_tables`, `drop_table`, `insert`, `select`, `update`, `delete`, `info`, `help`, `exit`.

Поддерживаемые типы данных: `int`, `str`, `bool`.

При создании таблицы автоматически добавляется поле `ID:int`.

## Установка

Для работы проекта необходимы Python и Poetry.

```bash
make install
```

## Запуск

```bash
make run
```

## Примеры команд

Создание таблицы:

```text
create_table users name:str age:int is_active:bool
```

Добавление записей:

```text
insert into users values ("Sergei", 28, true)
insert into users values ("Anna", 24, false)
```

Просмотр всех записей:

```text
select from users
```

Выборка по условию:

```text
select from users where age = 28
```

Обновление записи:

```text
update users set age = 29 where name = "Sergei"
```

Удаление записи:

```text
delete from users where ID = 1
```

Информация о таблице:

```text
info users
```

Список таблиц:

```text
list_tables
```

Удаление таблицы:

```text
drop_table users
```

## Хранение данных

Метаданные базы данных сохраняются в `db_meta.json`.

Данные каждой таблицы сохраняются отдельно в `data/<имя_таблицы>.json`, например:

```text
data/users.json
```

## Дополнительные возможности

- автоматическая генерация `ID`;
- проверка типов данных;
- проверка существования столбцов;
- подтверждение опасных операций;
- обработка ошибок с помощью декораторов;
- измерение времени выполнения операций;
- кэширование результатов `select`;
- вывод таблиц с помощью PrettyTable;
- разбор пользовательских команд;
- хранение данных в формате JSON.

## Демонстрация

Полный сценарий работы базы данных: создание таблицы, добавление и выборка записей, обновление, удаление, подтверждение опасных операций и удаление таблицы.

[![asciicast](https://asciinema.org/a/RkjrxYMv5siJXhD2.svg)](https://asciinema.org/a/RkjrxYMv5siJXhD2)

## Проверка кода

```bash
make lint
```

## Сборка

```bash
make build
```

Установка собранного пакета:

```bash
make package-install
```

Запуск установленного приложения:

```bash
poetry run database
```

## Структура проекта

```text
src/
├── __init__.py
└── primitive_db/
    ├── __init__.py
    ├── constants.py
    ├── core.py
    ├── decorators.py
    ├── engine.py
    ├── main.py
    ├── parser.py
    └── utils.py
```
