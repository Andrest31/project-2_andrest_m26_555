"""Command-line engine for the primitive database."""

import shlex

import prompt
from prettytable import PrettyTable

from src.primitive_db.constants import META_FILE
from src.primitive_db.core import (
    create_table,
    drop_table,
    insert,
    select,
)
from src.primitive_db.parser import parse_condition, parse_values
from src.primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Print available database commands."""
    print("\n***База данных***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> "
        "values (<значение1>, ...) - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> "
        "where <столбец> = <значение> - прочитать записи"
    )
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse_columns(column_args):
    """Parse column definitions from command arguments."""
    columns = []

    for column in column_args:
        if ":" not in column:
            raise ValueError(column)

        name, data_type = column.split(":", 1)
        columns.append((name, data_type))

    return columns


def print_table(metadata, table_name, table_data):
    """Print table records using PrettyTable."""
    columns = metadata[table_name]
    column_names = [column[0] for column in columns]

    table = PrettyTable()
    table.field_names = column_names

    for record in table_data:
        table.add_row(
            [record.get(column_name) for column_name in column_names]
        )

    print(table)


def handle_insert(metadata, args):
    """Handle an insert command."""
    if len(args) < 5 or args[1] != "into" or args[3] != "values":
        raise ValueError("Некорректная команда insert")

    table_name = args[2]
    values_text = " ".join(args[4:])
    values = parse_values(values_text)

    table_data = insert(metadata, table_name, values)
    save_table_data(table_name, table_data)


def handle_select(metadata, args):
    """Handle a select command."""
    if len(args) < 3 or args[1] != "from":
        raise ValueError("Некорректная команда select")

    table_name = args[2]

    if table_name not in metadata:
        raise KeyError(table_name)

    table_data = load_table_data(table_name)
    where_clause = None

    if len(args) > 3:
        if args[3] != "where":
            raise ValueError("Некорректная команда select")

        condition_text = " ".join(args[4:])
        where_clause = parse_condition(condition_text)

    result = select(table_data, where_clause)
    print_table(metadata, table_name, result)


def run():
    """Run the main database command loop."""
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string("Введите команду: ")
        args = shlex.split(user_input)

        if not args:
            continue

        command = args[0]

        try:
            if command == "exit":
                break

            if command == "help":
                print_help()

            elif command == "list_tables":
                if not metadata:
                    print("Таблицы отсутствуют.")
                else:
                    for table_name in metadata:
                        print(f"- {table_name}")

            elif command == "create_table":
                if len(args) < 3:
                    raise ValueError("create_table")

                table_name = args[1]
                columns = parse_columns(args[2:])

                old_metadata = metadata.copy()
                metadata = create_table(
                    metadata,
                    table_name,
                    columns,
                )

                if metadata != old_metadata:
                    save_metadata(META_FILE, metadata)

            elif command == "drop_table":
                if len(args) != 2:
                    raise ValueError("drop_table")

                old_metadata = metadata.copy()
                metadata = drop_table(metadata, args[1])

                if metadata != old_metadata:
                    save_metadata(META_FILE, metadata)

            elif command == "insert":
                handle_insert(metadata, args)

            elif command == "select":
                handle_select(metadata, args)

            else:
                print(f"Функции {command} нет. Попробуйте снова.")

        except KeyError as error:
            print(f"Ошибка: Таблица {error} не существует.")
        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова.")